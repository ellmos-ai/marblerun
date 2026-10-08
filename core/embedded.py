"""Embedded sequential execution with explicit admission and terminal receipts.

The embedding application supplies its dispatcher, execution observer, durable
checkpoint and cancellation callback. These callbacks own provider authority,
task acknowledgements and access checks. All steps run in their saved order.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass, replace

EMBEDDED_SEQUENCE_API = 1
_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")
_PHASES = {"ready", "starting", "running", "stopping", "complete", "failed", "stopped", "unconfirmed"}


def _identifier(value: str) -> None:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise ValueError("Invalid sequence identity")


@dataclass(frozen=True)
class SequenceStep:
    key: str
    payload_json: str

    def __post_init__(self):
        _identifier(self.key)
        if not isinstance(self.payload_json, str) or len(self.payload_json.encode("utf-8")) > 200_000:
            raise ValueError("Invalid step payload")
        if not isinstance(json.loads(self.payload_json), dict):
            raise ValueError("Step payload must be a JSON object")
        # Reject non-JSON numeric values even when a permissive decoder accepts them.
        json.dumps(json.loads(self.payload_json), allow_nan=False)

    @classmethod
    def from_payload(cls, key: str, payload: dict) -> SequenceStep:
        return cls(key, json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False))

    @property
    def payload(self) -> dict:
        return json.loads(self.payload_json)


@dataclass(frozen=True)
class ExecutionHandle:
    request_id: str
    job_id: str
    authority_id: str

    def __post_init__(self):
        for value in (self.request_id, self.job_id, self.authority_id):
            _identifier(value)


@dataclass(frozen=True)
class ExecutionObservation:
    handle: ExecutionHandle
    terminal: bool
    succeeded: bool | None = None
    output: str = ""
    reason: str = ""

    def __post_init__(self):
        if not isinstance(self.handle, ExecutionHandle) or type(self.terminal) is not bool:
            raise ValueError("An exact execution handle and terminal boolean are required")
        if self.terminal:
            if type(self.succeeded) is not bool:
                raise ValueError("A terminal observation requires a confirmed outcome")
        elif self.succeeded is not None:
            raise ValueError("A live execution cannot have a terminal outcome")
        if not isinstance(self.output, str) or len(self.output.encode("utf-8")) > 500_000:
            raise ValueError("Invalid execution output")
        if not isinstance(self.reason, str) or len(self.reason) > 4000:
            raise ValueError("Invalid observation reason")


@dataclass(frozen=True)
class CompletedStep:
    key: str
    handle: ExecutionHandle
    output: str


@dataclass(frozen=True)
class SequenceState:
    run_id: str
    plan_digest: str
    phase: str = "ready"
    cursor: int = 0
    completed: tuple[CompletedStep, ...] = ()
    active: ExecutionHandle | None = None
    reason: str = ""
    revision: int = 0
    stop_requested: bool = False

    def as_record(self) -> dict:
        return {"schema": "marblerun.sequence.v1", **asdict(self)}

    @classmethod
    def from_record(cls, record: dict) -> SequenceState:
        if not isinstance(record, dict) or record.get("schema") != "marblerun.sequence.v1":
            raise ValueError("Invalid sequence checkpoint schema")
        fields = {key: value for key, value in record.items() if key != "schema"}
        completed = fields.get("completed", ())
        if not isinstance(completed, (list, tuple)) or len(completed) > 64:
            raise ValueError("Invalid completed steps")
        fields["completed"] = tuple(CompletedStep(item["key"], ExecutionHandle(**item["handle"]), item["output"])
                                    for item in completed)
        active = fields.get("active")
        fields["active"] = ExecutionHandle(**active) if active is not None else None
        state = cls(**fields)
        _validate_state(state)
        return state


def _validate_state(state: SequenceState) -> None:
    _identifier(state.run_id)
    if not isinstance(state.plan_digest, str) or not re.fullmatch(r"[a-f0-9]{64}", state.plan_digest):
        raise ValueError("Invalid saved plan digest")
    if state.phase not in _PHASES or type(state.cursor) is not int or state.cursor < 0:
        raise ValueError("Invalid sequence phase or cursor")
    if type(state.revision) is not int or state.revision < 0 or state.cursor != len(state.completed):
        raise ValueError("Invalid sequence revision or completed cursor")
    if not isinstance(state.completed, tuple) or len(state.completed) > 64:
        raise ValueError("Invalid completed steps")
    for item in state.completed:
        if not isinstance(item, CompletedStep) or not isinstance(item.handle, ExecutionHandle):
            raise ValueError("Invalid completed step")
        _identifier(item.key)
        if not isinstance(item.output, str) or len(item.output.encode("utf-8")) > 500_000:
            raise ValueError("Invalid saved output")
    if state.active is not None and not isinstance(state.active, ExecutionHandle):
        raise ValueError("Invalid active execution")
    if not isinstance(state.reason, str) or len(state.reason) > 4000:
        raise ValueError("Invalid sequence reason")
    if type(state.stop_requested) is not bool:
        raise ValueError("Invalid saved cancellation request")
    handles = [item.handle for item in state.completed]
    if state.active is not None:
        handles.append(state.active)
    if len({(handle.authority_id, handle.job_id) for handle in handles}) != len(handles):
        raise ValueError("Saved execution reused for another step")
    if state.phase in {"ready", "starting", "complete", "stopped"} and state.active is not None:
        raise ValueError("This phase cannot hold an active execution")
    if state.phase in {"running", "stopping"} and state.active is None:
        raise ValueError("Active execution receipt missing")
    if state.phase == "stopping" and not state.stop_requested:
        raise ValueError("Cancellation intent missing")


def request_id_for(run_id: str, cursor: int) -> str:
    _identifier(run_id)
    if type(cursor) is not int or cursor < 0:
        raise ValueError("Invalid sequence cursor")
    return hashlib.sha256(f"marblerun.sequence.v1:{run_id}:{cursor}".encode("utf-8")).hexdigest()[:32]


def run_sequence(
    run_id: str,
    steps: Iterable[SequenceStep],
    *,
    dispatch: Callable[[SequenceStep, str, tuple[CompletedStep, ...]], ExecutionHandle],
    observe: Callable[[ExecutionHandle], ExecutionObservation],
    checkpoint: Callable[[SequenceState], None],
    cancel: Callable[[ExecutionHandle], None],
    should_stop: Callable[[], bool] = lambda: False,
    wait: Callable[[float], None] = time.sleep,
    poll_interval: float = 1.0,
    initial_state: SequenceState | None = None,
) -> SequenceState:
    """Run ordered steps; advance only after a correlated successful terminal.

    Checkpoints happen before admission and cancellation. An uncertain start
    or observation returns ``unconfirmed`` and never dispatches the next step.
    Resuming an active checkpoint observes that exact execution. A checkpoint
    without its admission receipt needs reconciliation by the application;
    it is never automatically dispatched again.
    """
    _identifier(run_id)
    plan = tuple(steps)
    if not 1 <= len(plan) <= 64 or any(not isinstance(step, SequenceStep) for step in plan):
        raise ValueError("A sequence requires 1 to 64 valid steps")
    if len({step.key for step in plan}) != len(plan):
        raise ValueError("Duplicate step identity")
    if type(poll_interval) not in {int, float} or not 0 <= poll_interval <= 60:
        raise ValueError("Invalid polling interval")
    digest = hashlib.sha256(json.dumps([asdict(step) for step in plan], sort_keys=True,
                                       ensure_ascii=False).encode("utf-8")).hexdigest()
    state = initial_state or SequenceState(run_id, digest)
    _validate_state(state)
    if state.run_id != run_id or state.plan_digest != digest or state.cursor > len(plan):
        raise ValueError("Saved sequence differs from the approved plan")
    for index, completed in enumerate(state.completed):
        if completed.key != plan[index].key or completed.handle.request_id != request_id_for(run_id, index):
            raise ValueError("Saved completed execution differs from the approved step")
    if state.active is not None and (state.cursor == len(plan)
            or state.active.request_id != request_id_for(run_id, state.cursor)):
        raise ValueError("Saved active execution differs from the approved step")
    if state.phase == "complete" and state.cursor != len(plan):
        raise ValueError("Saved completion is missing successful steps")
    if state.phase in {"complete", "failed", "stopped"}:
        return state

    def stopping():
        requested = should_stop()
        if type(requested) is not bool:
            raise ValueError("Stop callback must return a boolean")
        return requested or state.stop_requested

    def save(**changes):
        nonlocal state
        candidate = replace(state, revision=state.revision + 1, **changes)
        _validate_state(candidate)
        checkpoint(candidate)
        state = candidate
        return state

    if state.phase in {"starting", "unconfirmed"} and state.active is None:
        return save(phase="unconfirmed", reason="admission_receipt_requires_reconciliation")
    cancellation_sent = False
    while state.cursor < len(plan):
        stop = stopping()
        if state.active is None:
            if stop:
                return save(phase="stopped", stop_requested=True, reason="cancelled_before_admission")
            step = plan[state.cursor]
            request_id = request_id_for(run_id, state.cursor)
            save(phase="starting", reason="")
            try:
                handle = dispatch(step, request_id, state.completed)
                if not isinstance(handle, ExecutionHandle) or handle.request_id != request_id:
                    raise ValueError("Admission identity differs from the requested execution")
                if any((item.handle.authority_id, item.handle.job_id) == (handle.authority_id, handle.job_id)
                       for item in state.completed):
                    raise ValueError("Execution reused for another step")
            except Exception as exc:
                return save(phase="unconfirmed", reason="admission_unconfirmed:" + type(exc).__name__)
            save(phase="running", active=handle)
            cancellation_sent = False
        stop = stopping()
        if stop and not cancellation_sent:
            save(phase="stopping", stop_requested=True, reason="cancel_requested")
            try:
                cancel(state.active)
                cancellation_sent = True
            except Exception as exc:
                return save(phase="unconfirmed", reason="cancellation_unconfirmed:" + type(exc).__name__)
        try:
            observation = observe(state.active)
            if not isinstance(observation, ExecutionObservation) or observation.handle != state.active:
                return save(phase="unconfirmed", reason="execution_identity_conflict")
        except Exception as exc:
            return save(phase="unconfirmed", reason="observation_unconfirmed:" + type(exc).__name__)
        if not observation.terminal:
            if state.phase == "unconfirmed" and not state.stop_requested:
                save(phase="running", reason="")
            wait(poll_interval)
            continue
        if state.phase == "stopping" or stopping():
            return save(phase="stopped", stop_requested=True, active=None, reason="cancelled_after_terminal")
        if not observation.succeeded:
            return save(phase="failed", active=None, reason=observation.reason or "execution_failed")
        result = CompletedStep(plan[state.cursor].key, state.active, observation.output)
        save(phase="ready", active=None, cursor=state.cursor + 1, completed=(*state.completed, result), reason="")
    return save(phase="complete", reason="")
