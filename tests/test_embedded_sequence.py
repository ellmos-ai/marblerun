"""Embedded applications use exact execution receipts and durable checkpoints."""
import json
from dataclasses import replace
from unittest.mock import Mock

import pytest
from llmauto.core.embedded import (
    CompletedStep,
    ExecutionHandle,
    ExecutionObservation,
    SequenceState,
    SequenceStep,
    request_id_for,
    run_sequence,
)


@pytest.fixture
def harness():
    class Harness:
        steps = [SequenceStep.from_payload("first", {"profile": "one"}),
                 SequenceStep.from_payload("second", {"profile": "two"})]

        def __init__(self):
            self.states = []
            self.started = []
            self.observed = []
            self.cancelled = []
            self.stop = False
            self.live_rounds = 1

        def dispatch(self, step, request_id, completed):
            assert self.states[-1].phase == "starting"
            self.started.append((step.key, request_id, completed))
            return ExecutionHandle(request_id, step.key + "-job", "controller-v1")

        def observe(self, handle):
            self.observed.append(handle)
            if self.observed.count(handle) <= self.live_rounds:
                return ExecutionObservation(handle, False)
            return ExecutionObservation(handle, True, True, "Prüfung beendet: " + handle.job_id)

        def cancel(self, handle):
            assert self.states[-1].phase == "stopping" and self.states[-1].stop_requested
            self.cancelled.append(handle)

        def run(self, **changes):
            return run_sequence("run-1", self.steps, **{
                "dispatch": self.dispatch, "observe": self.observe, "checkpoint": self.states.append,
                "cancel": self.cancel, "should_stop": lambda: self.stop, "wait": lambda _: None,
                **changes,
            })
    return Harness()


def test_ordered_steps_use_terminal_receipts_and_real_previous_outputs(harness):
    result = harness.run()
    assert result.phase == "complete" and result.cursor == 2
    assert [item[0] for item in harness.started] == ["first", "second"]
    assert harness.observed[:2] == [result.completed[0].handle] * 2
    assert harness.started[1][2] == (result.completed[0],)
    assert result.completed[0].output == "Prüfung beendet: first-job"
    assert all(a.revision < b.revision for a, b in zip(harness.states, harness.states[1:], strict=False))
    restored = SequenceState.from_record(json.loads(json.dumps(result.as_record(), ensure_ascii=False)))
    assert restored == result


def test_terminal_failure_never_starts_a_successor(harness):
    result = harness.run(observe=lambda handle: ExecutionObservation(handle, True, False, reason="task_ack_missing"))
    assert result.phase == "failed" and result.reason == "task_ack_missing"
    assert len(harness.started) == 1 and not result.completed


def test_answer_text_without_terminal_does_not_advance(harness):
    observed = []
    def observe(handle):
        observed.append(handle)
        if len(observed) == 1:
            assert len(harness.started) == 1
            return ExecutionObservation(handle, False, output="FERTIG")
        return ExecutionObservation(handle, True, False, reason="task_pending")
    assert harness.run(observe=observe).phase == "failed"
    assert len(harness.started) == 1


def test_cancellation_waits_for_physical_terminal_and_keeps_intent(harness):
    def observe(handle):
        harness.observed.append(handle)
        harness.stop = True
        return ExecutionObservation(handle, len(harness.observed) >= 3,
                                    True if len(harness.observed) >= 3 else None)
    result = harness.run(observe=observe)
    assert result.phase == "stopped" and result.stop_requested
    assert len(harness.observed) == 3 and len(harness.cancelled) == 1
    assert len(harness.started) == 1 and result.active is None


def test_cancellation_before_first_admission_starts_nothing(harness):
    harness.stop = True
    assert harness.run().phase == "stopped"
    assert not harness.started and not harness.cancelled


def test_lost_cancel_ack_remains_unconfirmed_and_resumes_exact_cancellation(harness):
    def observe(handle):
        harness.stop = True
        return ExecutionObservation(handle, False)
    state = harness.run(observe=observe, cancel=Mock(side_effect=OSError("network lost")))
    assert state.phase == "unconfirmed" and state.active is not None and state.stop_requested
    harness.stop = False
    result = harness.run(initial_state=state, observe=lambda handle: ExecutionObservation(handle, True, True))
    assert result.phase == "stopped" and len(harness.started) == 1
    assert harness.cancelled == [state.active]


@pytest.mark.parametrize("stage", ["dispatch", "observe"])
def test_uncertain_calls_never_infer_success_or_replay_admission(harness, stage):
    result = harness.run(**{stage: Mock(side_effect=TimeoutError("unconfirmed"))})
    assert result.phase == "unconfirmed" and not result.completed
    if stage == "dispatch":
        assert result.active is None
        resumed = harness.run(initial_state=result)
        assert resumed.phase == "unconfirmed" and not harness.started
    else:
        assert result.active is not None
        resumed = harness.run(initial_state=result)
        assert resumed.phase == "complete" and len(harness.started) == 2


def test_changed_execution_identity_never_advances(harness):
    result = harness.run(observe=lambda handle: ExecutionObservation(
        replace(handle, job_id="foreign-generation"), True, True, "FERTIG"))
    assert result.phase == "unconfirmed" and result.reason == "execution_identity_conflict"
    assert len(harness.started) == 1 and not result.completed


def test_admission_receipt_must_match_the_exact_request(harness):
    result = harness.run(dispatch=lambda *args: ExecutionHandle("foreign-request", "job", "controller"))
    assert result.phase == "unconfirmed" and result.active is None


def test_checkpoint_failure_before_admission_prevents_dispatch(harness):
    with pytest.raises(OSError):
        harness.run(checkpoint=Mock(side_effect=OSError("database unavailable")))
    assert not harness.started


def test_changed_plan_cannot_resume_existing_execution(harness):
    state = harness.run(observe=Mock(side_effect=TimeoutError()))
    harness.steps = [SequenceStep.from_payload("first", {"profile": "changed"}), harness.steps[1]]
    with pytest.raises(ValueError, match="approved plan"):
        harness.run(initial_state=state)
    assert len(harness.started) == 1


def test_completed_checkpoint_is_not_reexecuted(harness):
    state = harness.run()
    assert harness.run(initial_state=state) == state and len(harness.started) == 2


def test_resuming_uncertainty_records_confirmed_running_before_waiting(harness):
    state = harness.run(observe=Mock(side_effect=TimeoutError()))
    observed = []
    def observe(handle):
        observed.append(handle)
        if len(observed) == 1:
            return ExecutionObservation(handle, False)
        return ExecutionObservation(handle, True, True, "actual result")
    def wait(_):
        assert harness.states[-1].phase == "running"
        assert harness.states[-1].active == state.active
    result = harness.run(initial_state=state, observe=observe, wait=wait)
    assert result.phase == "complete" and len(harness.started) == 2


def test_checkpoint_cannot_reuse_the_same_execution_for_another_step(harness):
    state = harness.run()
    first, second = state.completed
    forged = CompletedStep(second.key, replace(second.handle, job_id=first.handle.job_id), second.output)
    with pytest.raises(ValueError, match="reused"):
        harness.run(initial_state=replace(state, completed=(first, forged)))


def test_stop_intent_survives_unconfirmed_admission_until_host_reconciliation(harness):
    unknown = harness.run(dispatch=Mock(side_effect=TimeoutError()))
    assert unknown.active is None and not unknown.stop_requested
    harness.stop = True
    requested = harness.run(initial_state=unknown)
    assert requested.phase == "unconfirmed" and requested.stop_requested and requested.active is None
    reconciled = replace(requested, active=ExecutionHandle(request_id_for("run-1", 0), "first-job", "controller-v1"))
    harness.stop = False
    result = harness.run(initial_state=reconciled, observe=lambda handle: ExecutionObservation(handle, True, True))
    assert result.phase == "stopped" and result.stop_requested
    assert harness.cancelled == [reconciled.active] and not harness.started


@pytest.mark.parametrize("field", ["run_id", "plan_digest", "phase", "cursor", "completed",
                                   "active", "reason", "revision", "stop_requested"])
def test_missing_checkpoint_fields_cannot_default_to_a_new_admission(harness, field):
    state = harness.run(dispatch=Mock(side_effect=TimeoutError()))
    record = state.as_record()
    del record[field]
    with pytest.raises(ValueError, match="fields"):
        SequenceState.from_record(record)
    assert not harness.started


@pytest.mark.parametrize("phase", ["ready", "starting", "complete", "failed", "stopped"])
def test_inactive_checkpoint_phases_cannot_hide_an_active_execution(harness, phase):
    state = harness.run(observe=Mock(side_effect=TimeoutError()))
    with pytest.raises(ValueError, match="active execution"):
        harness.run(initial_state=replace(state, phase=phase))


@pytest.mark.parametrize("terminal,succeeded", [("true", True), (False, True), (True, None), (True, "yes")])
def test_receipts_require_actual_booleans(terminal, succeeded):
    with pytest.raises(ValueError):
        ExecutionObservation(ExecutionHandle("request", "job", "authority"), terminal, succeeded)


def test_payloads_are_immutable_and_reject_non_json_values():
    payload = {"skills": ["first", "second"]}
    step = SequenceStep.from_payload("skills", payload)
    payload["skills"].append("foreign")
    step.payload["skills"].append("foreign")
    assert step.payload["skills"] == ["first", "second"]
    with pytest.raises(ValueError):
        SequenceStep.from_payload("bad", {"value": float("nan")})


def test_duplicate_steps_invalid_polling_and_forged_completion_are_rejected(harness):
    harness.steps = [harness.steps[0], harness.steps[0]]
    with pytest.raises(ValueError):
        harness.run()
    harness.steps = [harness.steps[0]]
    for interval in (-1, float("nan"), True):
        with pytest.raises(ValueError):
            harness.run(poll_interval=interval)
    state = harness.run()
    with pytest.raises(ValueError):
        harness.run(initial_state=replace(state, cursor=0, completed=()))
    assert request_id_for("run-1", 0) != request_id_for("run-1", 1)
