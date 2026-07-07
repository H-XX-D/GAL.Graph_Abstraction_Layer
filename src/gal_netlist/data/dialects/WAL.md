# WAL: Workflow Abstraction Layer

Status: draft v0.1.

WAL is the GAL dialect for workflow graphs. It describes jobs, steps, gates,
dependencies, retries, artifacts, schedules, and completion state.

## Vocabulary

```json
{
  "id": "wal.v0",
  "nodeKinds": ["workflow", "job", "step", "gate", "artifact", "queue", "schedule", "trigger", "retry", "receipt"],
  "relations": ["starts", "precedes", "depends_on", "blocks", "unblocks", "emits", "consumes", "triggers", "retries", "verifies", "notifies"],
  "fields": ["status", "priority", "progress", "duration", "attempts", "risk", "cost"],
  "signals": ["ready", "running", "succeeded", "failed", "blocked", "retryable", "timed_out", "artifact_ready"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["schedule", "dispatch", "retry", "timeout", "gate", "notify", "checkpoint"],
  "threads": ["tick", "workflow", "queue"]
}
```

## Node Kinds

| kind | purpose |
|---|---|
| `workflow` | workflow container |
| `job` | executable work unit |
| `step` | ordered sub-unit |
| `gate` | transition condition |
| `artifact` | produced output |
| `queue` | work queue |
| `schedule` | timing source |
| `trigger` | event source |
| `retry` | retry policy |
| `receipt` | completion evidence |

## Required Loader Rules

- `precedes` and `depends_on` edges must not create cycles unless the dialect
  explicitly marks the loop as a schedule.
- `retry` nodes must include a maximum attempt count.
- `timeout` operations must produce a diagnostic target.
- `plan` mode should list queue mutations without dispatching jobs.

## Example

```gal
@gal netlist.v0
@dialect wal.v0

workflow_release "Release workflow" progress(0.20) priority(0.78) [kind: workflow]
job_build "Build artifact" status(0.70) attempts(1) [kind: job]
job_verify "Verify release" status(0.25) [kind: job]
precedes> job_verify(1.0)

artifact_image "Container image" status(0.60) [kind: artifact]
job_build emits> artifact_image(1.0)
job_verify consumes> artifact_image(1.0)

net can_dispatch and2 ready artifact_ready
net should_retry and2 failed retryable
addf dispatch0 queue [workflow: workflow_release] [job: job_build]
addf retry0 workflow [job: job_verify] [max: 3] [backoff: exponential]
setp retry0.max 2
```
