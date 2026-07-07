# AAL: Agent Abstraction Layer

Status: draft v0.1.

AAL is the GAL dialect for agent graphs. It describes agents, roles, tools,
tasks, capabilities, plans, handoffs, and execution receipts.

## Vocabulary

```json
{
  "id": "aal.v0",
  "nodeKinds": ["agent", "role", "tool", "capability", "task", "plan", "handoff", "receipt", "constraint", "workspace"],
  "relations": ["has_role", "can_use", "requires", "assigned_to", "delegates_to", "blocked_by", "produces", "consumes", "verifies", "runs_in", "governed_by", "observed_by"],
  "fields": ["confidence", "priority", "progress", "risk", "cost", "latency", "trust"],
  "signals": ["ready", "blocked", "needs_approval", "tool_available", "verified", "handoff_ready", "policy_ok"],
  "netOps": ["not1", "and2", "or2", "xor2", "lut5"],
  "standingOps": ["assign", "plan", "delegate", "verify", "checkpoint", "request_approval", "summarize"],
  "threads": ["tick", "agent", "review"]
}
```

## Node Kinds

| kind | purpose |
|---|---|
| `agent` | autonomous or assisted worker |
| `role` | responsibility profile |
| `tool` | callable capability boundary |
| `capability` | skill or permission |
| `task` | unit of work |
| `plan` | ordered or partial work plan |
| `handoff` | transfer record between agents or humans |
| `receipt` | execution evidence |
| `constraint` | work limitation or invariant |
| `workspace` | filesystem, repo, or runtime context |

## Required Loader Rules

- `tool` nodes must describe capability boundaries, not embed credentials.
- `task` nodes should preserve assignment and verification state.
- `handoff` nodes must identify producer, consumer, and remaining obligations
  when possible.
- `request_approval` operations must not auto-approve privileged actions.

## Example

```gal
@gal netlist.v0
@dialect aal.v0

agent_codex "Codex coding agent" trust(0.86) latency(0.30) [kind: agent]
role_spec_author "Specification author" priority(0.70) [kind: role]
task_define_dal "Define DAL dialect" progress(0.40) priority(0.80) [kind: task]
assigned_to> agent_codex(1.0)
requires> tool_git(0.8)
governed_by> policy_repo_publish(1.0)

tool_git "Git CLI" trust(0.92) [kind: tool] [permission: repo-write]
net can_execute and2 ready policy_ok
net needs_handoff or2 blocked needs_approval
addf plan0 agent [task: task_define_dal] [depth: shallow]
addf checkpoint0 tick [task: task_define_dal] [cadence: milestone]
setp task_define_dal.progress 0.75
```
