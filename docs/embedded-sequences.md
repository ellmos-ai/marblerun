# Embedded sequence API

`llmauto.core.embedded` exposes `EMBEDDED_SEQUENCE_API = 1` and `run_sequence()`
for applications that already own their workers and task store. Package version
0.1.3 remains unchanged; installations of this new API must pin its source commit.

## Application callbacks

| Callback | Contract |
| --- | --- |
| `dispatch(step, request_id, completed)` | Admit the saved step once, using the supplied request identity. Return the actual job and authority identity. |
| `observe(handle)` | Observe that exact job. `terminal=True` requires physical termination. `succeeded=True` requires the application's authoritative completion acknowledgement. |
| `checkpoint(state)` | Save the immutable state durably, with the application's transaction, ownership and revision checks. Raise if the save is rejected. |
| `cancel(handle)` | Request cancellation of the exact job. Support repeating that same cancellation after recovery. |
| `should_stop()` | Read the current cancellation request as a boolean. |

`SequenceStep.from_payload()` freezes JSON inputs. `ExecutionHandle` correlates
the request, job and authority. `ExecutionObservation` carries the terminal
outcome and actual result. Each successful `CompletedStep` is passed to the
following dispatcher as context. Applications can use this mechanism for ordered
agents or for ordered skills executed by one worker identity.

The runner checkpoints admission intent before dispatch. It waits for each
correlated terminal observation before starting the next step. Cancellation
intent remains in the checkpoint until the current job is confirmed terminal.

## Recovery

Persist `state.as_record()` as JSON. Restore it using
`SequenceState.from_record()` and pass it as `initial_state` together with the
same approved plan. The plan digest, completed request identities and active
request identity are checked before callbacks execute. An active job is observed
using its saved authority and job identity. Completed steps are retained.

An uncertain call produces `phase="unconfirmed"`. A start without a saved
admission receipt requires the application to reconcile its durable request
identity against its controller. That state does not automatically repeat the
dispatch. A changed controller or generation must remain unconfirmed until the
application can provide authoritative evidence.

The embedding application owns provider selection, permissions, locks, task
leases, result validation, checkpoint fencing and controller identity checks.
Supply bounded callback requests and run the loop in the application's own
supervisor. The module's embedded path performs no file operations or CLI starts.
