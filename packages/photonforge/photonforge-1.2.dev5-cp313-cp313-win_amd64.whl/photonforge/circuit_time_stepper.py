import threading
import time
import warnings
from collections.abc import Sequence
from queue import Queue
from typing import Any

from . import typing as pft
from .cache import _mode_overlap_cache
from .circuit_base import _gather_status, _process_component_netlist
from .extension import (
    Component,
    FiberPort,
    GaussianPort,
    Port,
    TimeStepper,
    config,
    register_time_stepper_class,
)
from .tidy3d_model import _align_and_overlap


def _stepper(work_queue):
    while True:
        fn, args, outputs = work_queue.get()
        if fn is None:
            return
        try:
            result = fn(*args)
        except Exception as err:
            result = str(err)
        outputs.append(result)
        work_queue.task_done()


class CircuitTimeStepper(TimeStepper):
    """Circuit-level time stepper.

    Constructs time steppers for individual circuit elements and handles
    connections between them. Each time stepper initialization is preceded
    by an update to the componoent's technology, the component itself, and
    its active model by calling :attr:`Reference.update`. They are reset to
    their original state afterwards.

    If a reference includes repetitions, it is flattened so that each
    instance is called separatelly.

    Args:
        mesh_refinement: Minimum number of mesh elements per wavelength used
          for mode solving.
        max_iterations: Maximum number of iterations for self-consistent
          signal propagation through the circuit. A larger value may be
          needed for larger circuits or high-Q feedback loops.
        abs_tolerance: The absolute tolerance for the convergence check.
        rel_tolerance: The relative tolerance for the convergence check.
        max_threads: Maximum number of threads used for stepping individual
          subcomponents.
        verbose: Flag setting the verbosity of mode solver runs.
    """

    def __init__(
        self,
        mesh_refinement: pft.PositiveFloat | None = None,
        max_iterations: pft.PositiveInt = 100,
        abs_tolerance: pft.PositiveFloat = 1e-8,
        rel_tolerance: pft.PositiveFloat = 1e-5,
        max_threads: pft.PositiveInt = 8,
        verbose: bool = True,
    ):
        super().__init__(
            mesh_refinement=mesh_refinement,
            max_iterations=max_iterations,
            abs_tolerance=abs_tolerance,
            rel_tolerance=rel_tolerance,
            max_threads=max_threads,
            verbose=verbose,
        )
        self._status = None
        self._work_queue = None

    def setup_state(
        self,
        *,
        component: Component,
        time_step: float,
        carrier_frequency: float,
        monitors: dict[str, Port | FiberPort | GaussianPort] = {},
        updates: dict[Sequence[str | int | None], dict[str, dict[str, Any]]] = {},
        chain_technology_updates: bool = True,
        verbose: bool | None = None,
        **kwargs,
    ):
        """Initialize internal circuit variables.

        Args:
            component: Component for the time stepper.
            time_step: The interval between time steps (in seconds).
            carrier_frequency: The carrier frequency used to construct the time
              stepper. The carrier should be omitted from the input signals, as
              it is handled automatically by the time stepper.
            monitors: Additional ports to include in the outputs as a dictionary
              with monitor names as keys. Subcomponent ports can be obtained
              with :func:`Reference.get_ports` for the 1st level of references
              or with :func:`Component.query` for more deeply-nested ports.
            updates: Dictionary of parameter updates to be applied to
              components, technologies, and models for references within the
              main component. See :func:`CircuitModel.start` for examples.
            chain_technology_updates: if set, a technology update will trigger
              an update for all components using that technology.
            verbose: If set, overrides the model's ``verbose`` attribute and
              is passed to reference models.
            kwargs: Keyword arguments passed to reference models.

        Returns:
            Object with a status dictionary.
        """
        time_stepper_kwargs = {
            "time_step": time_step,
            "carrier_frequency": carrier_frequency,
        }
        if verbose is None:
            verbose = self.parametric_kwargs["verbose"]
        else:
            time_stepper_kwargs["verbose"] = verbose

        frequencies = [carrier_frequency if carrier_frequency > 0 else (1 / time_step)]
        (
            runners,
            self.time_steppers,
            _,
            port_connections,
            self.connections,
            instance_port_data,
            self.monitors,
        ) = _process_component_netlist(
            component,
            frequencies,
            self.parametric_kwargs["mesh_refinement"],
            monitors,
            updates,
            chain_technology_updates,
            verbose,
            False,
            kwargs,
            None,
            time_stepper_kwargs,
        )

        self.port_connections = [
            (index, f"{ref_port_name}@{n}", f"{port_name}@{n}")
            for (index, ref_port_name, num_modes), port_name in port_connections.items()
            for n in range(num_modes)
        ]

        self.component_name = component.name

        self.lock = threading.Lock()
        self._status = {"message": "running", "progress": 0}
        self.setup_thread = threading.Thread(
            daemon=True, target=self._setup_and_monitor, args=(runners, instance_port_data)
        )
        self.setup_thread.start()
        return self

    def _setup_and_monitor(self, runners, instance_port_data):
        runners = {k: v for k, v in runners.items() if v is not None}
        joint_status = _gather_status(*runners.values())

        with self.lock:
            self._status = dict(joint_status)
            self._status["progress"] *= 0.95

        while joint_status["message"] == "running":
            time.sleep(0.3)
            joint_status = _gather_status(*runners.values())
            with self.lock:
                self._status = dict(joint_status)
                self._status["progress"] *= 0.95

        if joint_status["message"] == "error":
            with self.lock:
                self._status = joint_status
            return

        with self.lock:
            self._status = joint_status
            self._status["message"] = "running"
            self._status["progress"] *= 0.95

        self.mode_factors = [{} for _ in range(len(instance_port_data))]
        for index, (instance_ports, instance_keys) in enumerate(instance_port_data):
            # Check if reference is needed
            if instance_ports is None:
                continue

            # Fix port phases if a rotation is applied
            if instance_keys is not None:
                for port_name, port in instance_ports:
                    key = instance_keys.get(port_name)
                    if key is None:
                        continue

                    # Port mode
                    overlap = _mode_overlap_cache[key]
                    if overlap is None:
                        overlap = _align_and_overlap(
                            self.runners[(index, port_name, 0)].data,
                            self.runners[(index, port_name, 1)].data,
                        )[0]
                        _mode_overlap_cache[key] = overlap

                    self.mode_factors[index].update(
                        {f"{port_name}@{mode}": overlap[mode] for mode in range(port.num_modes)}
                    )

            with self.lock:
                self._status["progress"] = 95 + 5 * (index + 1) / len(instance_port_data)

        self.port_state = [{} for _ in instance_port_data]
        for connection in self.connections:
            for index, port_name, num_modes in connection:
                self.port_state[index].update(
                    {f"{port_name}@{mode}": 0 for mode in range(num_modes)}
                )

        self.emitted_convergence_warning = False

        with self.lock:
            self._status["progress"] = 100
            self._status["message"] = "success"

    def reset(self):
        """Reset the state of the circuit variables."""
        self.port_state = [{} for _ in self.port_state]
        for connection in self.connections:
            for index, port_name, num_modes in connection:
                self.port_state[index].update(
                    {f"{port_name}@{mode}": 0 for mode in range(num_modes)}
                )

        self.emitted_convergence_warning = False

        for time_stepper in self.time_steppers.values():
            time_stepper.reset()

    @property
    def status(self):
        if not self.setup_thread.is_alive() and self._status["message"] == "running":
            self._status["message"] = "error"
        with self.lock:
            return self._status

    def step_single(
        self, inputs: dict[str, complex], time_index: int, update_state: bool, shutdown: bool
    ) -> dict[str, complex]:
        """Take a single time step on the given inputs.

        Args:
            inputs: Dictionary containing inputs at the current time step,
              mapping port names to complex values.
            time_index: Time series index for the current input.
            update_state: Whether to update the internal stepper state.
            shutdown: Whether this is the last call to the single stepping
              function for the provided :class:`TimeSeries`.

        Returns:
            Outputs at the current time step.
        """
        num_instances = len(self.port_state)
        abs_tolerance = self.parametric_kwargs["abs_tolerance"]
        rel_tolerance = self.parametric_kwargs["rel_tolerance"]

        if self._work_queue is None:
            self._work_queue = Queue()
            for _ in range(max(1, min(num_instances, self.parametric_kwargs["max_threads"]))):
                threading.Thread(daemon=True, target=_stepper, args=(self._work_queue,)).start()

        input_state = [dict(d) for d in self.port_state]

        # apply input to input_state
        for index, ref_name, port_name in self.port_connections:
            if port_name in inputs:
                input_state[index][ref_name] = inputs[port_name]
            elif ref_name not in input_state[index]:
                input_state[index][ref_name] = 0

        max_iterations = max(self.parametric_kwargs["max_iterations"], 1)
        is_last_iteration = max_iterations == 1

        # self.port_state stores inputs at time t. Compute outputs at time t, and use them as inputs
        # at time t, iterate. Once converged, use the outputs as inputs at time t+1
        for current_iteration in range(1, max_iterations + 1):
            if current_iteration == max_iterations:
                is_last_iteration = True

            update = update_state and is_last_iteration
            shdwn = shutdown and is_last_iteration
            work_items = []
            for index, mode_factors in enumerate(self.mode_factors):
                instance_inputs = {
                    k: v * mode_factors.get(k, 1.0) for k, v in input_state[index].items()
                }
                work_item = (
                    self.time_steppers[index].step_single,
                    (instance_inputs, time_index, update, shdwn),
                    [],
                )
                work_items.append(work_item)
                self._work_queue.put(work_item)

            # block for runners to finish
            self._work_queue.join()

            output_state = [{} for _ in range(num_instances)]
            for index, (_, _, results) in enumerate(work_items):
                if isinstance(results[0], str):
                    raise RuntimeError(results[0])
                mf = self.mode_factors[index]
                output_state[index] = {k: v / mf.get(k, 1.0) for k, v in results[0].items()}

            # apply connections
            next_input_state = [{} for _ in range(num_instances)]
            for (idx1, port_name1, num_modes), (idx2, port_name2, _) in self.connections:
                for mode in range(num_modes):
                    key1 = f"{port_name1}@{mode}"
                    key2 = f"{port_name2}@{mode}"
                    val1 = output_state[idx1].get(key1)
                    if val1 is not None:
                        next_input_state[idx2][key2] = val1
                    val2 = output_state[idx2].get(key2)
                    if val2 is not None:
                        next_input_state[idx1][key1] = val2

            # apply input to input_state
            for index, ref_name, port_name in self.port_connections:
                if port_name in inputs:
                    next_input_state[index][ref_name] = inputs[port_name]
                elif ref_name not in next_input_state[index]:
                    next_input_state[index][ref_name] = 0

            if is_last_iteration:
                break

            # check convergence: math.isclose is symmetric and numpy.isclose is not
            converged = True
            for prv, nxt in zip(input_state, next_input_state, strict=True):
                for k, v1 in nxt.items():
                    v0 = prv.get(k, 0)
                    if abs(v1 - v0) > max(abs_tolerance, rel_tolerance * max(abs(v1), abs(v0))):
                        converged = False
                        break
                if not converged:
                    break

            if converged:
                is_last_iteration = True

            input_state = next_input_state

        if update_state:
            self.port_state = next_input_state

        if shutdown:
            self._work_queue.put((None, None, None))
            self._work_queue = None

        if max_iterations > 1 and not self.emitted_convergence_warning and not converged:
            warnings.warn(
                f"Time stepper for component '{self.component_name}' failed to converge. "
                f"Consider increasing 'max_iterations'.",
                stacklevel=2,
            )
            self.emitted_convergence_warning = True

        # store outputs
        outputs = {
            port_name: output_state[index].get(ref_name, 0)
            for index, ref_name, port_name in self.port_connections
        }

        # include monitors
        for index, port_name, num_modes, monitor_name in self.monitors:
            outputs.update(
                {
                    f"{monitor_name}@{mode}-": input_state[index].get(f"{port_name}@{mode}", 0)
                    for mode in range(num_modes)
                }
            )
            outputs.update(
                {
                    f"{monitor_name}@{mode}+": output_state[index].get(f"{port_name}@{mode}", 0)
                    for mode in range(num_modes)
                }
            )
        return outputs


register_time_stepper_class(CircuitTimeStepper)
config.default_time_steppers["CircuitModel"] = CircuitTimeStepper()
