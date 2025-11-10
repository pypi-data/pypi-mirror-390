import logging
import time
from abc import abstractmethod
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple
from uuid import UUID

import celpy
from celpy import celtypes
from celpy.evaluation import CELEvalError, CELUnsupportedError
from numpy import isin
from pydantic import BaseModel, ConfigDict, PrivateAttr

from highlighter.agent.capabilities import Capability, StreamEvent
from highlighter.client import HLClient
from highlighter.client.base_models.entities import Entities, Entity

logger = logging.getLogger(__name__)


class Trigger(BaseModel):

    @abstractmethod
    def get_state(self, stream, **kwargs) -> bool:
        """Returns True if trigger is in 'on' state, False if in 'off' state."""
        pass


def create_trigger(trigger_params: Dict) -> Trigger:
    """Factory function to create trigger instances based on configuration."""
    trigger_type = trigger_params.get("type", "PeriodicTrigger")
    params = {k: v for k, v in trigger_params.items() if k != "type"}

    logger.debug(f"create_trigger called with: trigger_type='{trigger_type}', params={params}")

    if trigger_type == "PeriodicTrigger":
        trigger = PeriodicTrigger(**params)
        logger.debug(f"Created PeriodicTrigger: {trigger}")
        return trigger
    if trigger_type == "RuleTrigger":
        trigger = RuleTrigger(**params)
        logger.debug(f"Created RuleTrigger: {trigger}")
        return trigger
    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")


class PeriodicTrigger(Trigger):
    on_period: float  # sec
    off_period: float  # sec

    _start_time: Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _is_on_period(self) -> bool:
        """Determines if the current time is within an 'on' period."""
        current_time = time.time()

        if self._start_time is None:
            self._start_time = current_time

        elapsed = current_time - self._start_time
        cycle_time = self.on_period + self.off_period

        if cycle_time <= 0:
            # Avoid division by zero; default to 'on' if periods are non-positive.
            return True

        cycle_position = elapsed % cycle_time
        return cycle_position < self.on_period

    def get_state(self, *args, **kwargs) -> bool:
        """Returns True if in 'on' period, False if in 'off' period."""
        return self._is_on_period()


class RuleTrigger(Trigger):
    """Evaluate a CEL expression against the available trigger context."""

    expression: str
    patience: int = 0  # sec - time to wait after last True before returning False
    default_state: bool = False
    log_errors_every_n_frames: int = 100  # Log evaluation errors once every N frames (0 = always log)

    _attribute_collection_warnings: defaultdict = PrivateAttr(default_factory=lambda: defaultdict(int))
    _evaluation_error_count: defaultdict = PrivateAttr(default_factory=lambda: defaultdict(int))
    _program_cache: dict = PrivateAttr(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        self._last_true_trigger = None

    def get_state(self, stream, *, data_sample, **kwargs) -> bool:

        # Log entry with stream info
        logger.debug(f"=== RuleTrigger.get_state() called for stream {stream.stream_id} ===")

        is_entities = lambda x: isinstance(x, Entities) or (
            isinstance(x, dict) and x and isinstance(x[list(x)[0]], Entity)
        )

        # Collect attributes for Entities
        # Support entities dict and Entities object
        # ToDo: Only support one (Entities)
        entities = Entities()
        for ents in [e for e in kwargs.values() if is_entities(e)]:
            if isinstance(ents, Entities):
                entities.update(ents._entities)
            else:
                entities.update(ents)

        observations_table = entities.to_observations_table(stream.stream_id, data_sample)

        state = self.default_state
        try:
            now = time.perf_counter()
            result = observations_table.any(self.expression)
            logger.info(f"{self.expression} ---> evaluates to {result}")

            if result:
                self._last_true_trigger = time.perf_counter()
                state = True
            elif (self._last_true_trigger is not None) and ((now - self._last_true_trigger) > self.patience):
                state = False

        except Exception as exc:
            # Rate-limit error logging to avoid spam
            stream_id = getattr(stream, "stream_id", "unknown")
            error_key = f"{stream_id}:{type(exc).__name__}"
            self._evaluation_error_count[error_key] += 1

            # Log on first occurrence, then every Nth frame (if configured)
            # When log_errors_every_n_frames=0, always log
            should_log = (
                self.log_errors_every_n_frames == 0
                or self._evaluation_error_count[error_key] == 1
                or self._evaluation_error_count[error_key] % self.log_errors_every_n_frames == 0
            )

            if should_log:
                logger.warning(
                    "RuleTrigger evaluation failed for '%s' (count: %d): %s",
                    self.expression,
                    self._evaluation_error_count[error_key],
                    exc,
                )

        return state


class _StreamTrigger:

    def __init__(self, trigger: Callable, case_is_recording: bool):
        self.trigger = trigger
        self.case_is_recording = case_is_recording


class RecordingAction(Enum):
    START_RECORDING = 0
    STOP_RECORDING = 1
    CONTINUE_RECORDING = 2
    CONTINUE_WAITING = 3


class CreateCase(Capability):
    """
    Capability that monitors incoming data and creates cases when trigger conditions are met.

    Uses simple delta-from-start-time triggering initially.
    """

    class InitParameters(Capability.InitParameters):

        # Case creation parameters
        new_case_workflow_order_id: UUID
        new_case_entity_id: Optional[UUID] = None
        case_record_capabilities: List[str] = []
        new_case_task_step_id: Optional[str] = None

        # Case metadata
        case_name_template: Optional[str] = None

        # Trigger configuration
        trigger_params: Dict = {"type": "PeriodicTrigger", "on_period": 30, "off_period": 300}

    class StreamParameters(InitParameters):
        pass

    def __init__(self, context):
        super().__init__(context)
        self.stream_triggers = {}

        # (case_is_recording, trigger)
        START_RECORDING = (False, True)
        STOP_RECORDING = (True, False)
        CONTINUE_RECORDING = (True, True)
        CONTINUE_WAITING = (False, False)
        self._actions = {
            START_RECORDING: self._start_recording,
            STOP_RECORDING: self._stop_recording,
            CONTINUE_RECORDING: self._continue_recording,
            CONTINUE_WAITING: self._continue_waiting,
        }

    def start_stream(self, stream, stream_id, use_create_frame=True):
        """Initialize stream state"""
        stream_event, result = super().start_stream(stream, stream_id, use_create_frame=use_create_frame)

        # Get init parameters for this stream
        init_params = self.stream_parameters(stream_id)

        logger.debug(f"=== CreateCase.start_stream() for stream {stream_id} ===")
        logger.debug(f"trigger_params: {init_params.trigger_params}")

        # Initialize trigger instance
        case_create_trigger = create_trigger(init_params.trigger_params)
        logger.debug(f"Created trigger of type: {type(case_create_trigger)}")

        self.stream_triggers[stream_id] = _StreamTrigger(case_create_trigger, False)

        # Initialize client
        self.client = HLClient.get_client()
        return stream_event, result

    def stop_stream(self, stream, stream_id):
        """Clean up stream state and close open cases"""
        if stream_id in self.stream_triggers:
            stream_trigger = self.stream_triggers[stream_id]

            # Close any open cases before cleaning up
            if stream_trigger.case_is_recording:
                try:
                    parameters = self.stream_parameters(stream_id)
                    self._stop_recording(stream, parameters, stream_trigger)
                    self.logger.debug(f"Closed case during stream cleanup for stream {stream_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to close case during cleanup: {e}")

            del self.stream_triggers[stream_id]

        # Finalize any pending recordings in TaskContext
        if "task" in stream.variables:
            try:
                stream.variables["task"].finalise_submissions_on_recording_state_off()
            except Exception as e:
                self.logger.warning(f"Failed to finalize recordings during cleanup: {e}")

        return super().stop_stream(stream, stream_id)

    def process_frame(self, stream, data_samples, **kwargs) -> Tuple[StreamEvent, dict]:
        """
        Process incoming frame data and trigger case creation using Trigger class.

        Accepts arbitrary inputs from upstream capabilities via kwargs.
        """
        stream_id = stream.stream_id
        logger.debug(
            f"=== CreateCase.process_frame() called for stream {stream_id} with {len(data_samples)} data_samples ==="
        )

        # Check if stream is still active (may have been cleaned up during shutdown)
        if stream_id not in self.stream_triggers:
            self.logger.debug(f"Stream {stream_id} no longer active, skipping frame processing")
            response = {"data_samples": data_samples}
            response.update(kwargs)
            return StreamEvent.OKAY, response

        parameters = self.stream_parameters(stream_id)
        stream_trigger = self.stream_triggers[stream_id]
        logger.debug(
            f"Stream trigger type: {type(stream_trigger.trigger)}, case_is_recording: {stream_trigger.case_is_recording}"
        )

        if not stream_trigger.trigger:
            self.logger.warning(f"No trigger found for stream {stream_id}")
            return StreamEvent.OKAY, kwargs

        # ToDo: remove when entities are batched to corrispond to data_samples
        if len(data_samples) != 1:
            self.logger.warning(
                f"Expected 1 data sample, but got {len(data_samples)}. Processing first sample only."
            )

        for i, ds in enumerate(data_samples):
            trigger_kwargs = {"data_sample": ds}

            # ToDo: Entities are not batched. For now, we'll just assume
            # that we have one data_sample per tick.
            # trigger_kwargs.update({k: kwargs[k][i] for k in kwargs})
            trigger_kwargs.update(kwargs)

            case_is_recording = stream_trigger.case_is_recording
            logger.debug(f"Calling trigger.get_state() with kwargs: {list(trigger_kwargs.keys())}")
            trigger_state_on = stream_trigger.trigger.get_state(stream, **trigger_kwargs)
            logger.debug(f"Trigger returned: {trigger_state_on}, case_is_recording: {case_is_recording}")
            logger.debug(f"Action key: ({case_is_recording}, {trigger_state_on})")
            self._actions[(case_is_recording, trigger_state_on)](stream, parameters, stream_trigger)

        response = {"data_samples": data_samples}
        response.update(kwargs)
        return StreamEvent.OKAY, response

    def _start_recording(self, stream, parameters, stream_trigger):
        case_name = None
        if parameters.case_name_template:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            case_name = parameters.case_name_template.format(timestamp=timestamp, stream_id=stream.stream_id)

        # Ensure task context exists (may not exist if stream was recreated after error)
        if "task" not in stream.variables:
            from highlighter.client.tasks import TaskContext

            stream.variables["task"] = TaskContext()

        stream.variables["task"].start_recording(
            [
                self.pipeline.pipeline_graph.get_node(name).element._dsps[stream.stream_id]
                for name in parameters.case_record_capabilities
            ],
            parameters.new_case_workflow_order_id,
            case_name=case_name,
            entity_id=parameters.new_case_entity_id,
        )
        stream_trigger.case_is_recording = True

    def _stop_recording(self, stream, parameters, stream_trigger):
        # Defensive check - task should exist if we're recording
        if "task" not in stream.variables:
            self.logger.warning("Attempted to stop recording but task context doesn't exist")
            stream_trigger.case_is_recording = False
            return

        stream.variables["task"].stop_recording()
        stream_trigger.case_is_recording = False

    def _continue_recording(self, stream, parameters, stream_trigger):
        # No action
        pass

    def _continue_waiting(self, stream, parameters, stream_trigger):
        # No action
        pass
