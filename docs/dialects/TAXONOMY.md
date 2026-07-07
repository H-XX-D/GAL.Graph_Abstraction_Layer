# GAL Dialect Taxonomy

The GAL dialect family is broad by design. Dialects should be treated as
optional lenses over graph state, not as a mandatory stack.

## Foundation Dialects

These describe reusable graph-runtime primitives.

| dialect | focus |
|---|---|
| `mal.v0` | memory graphs |
| `kal.v0` | knowledge and provenance |
| `real.v0` | reasoning traces and decisions |
| `cal.v0` | capabilities and grants |
| `ial.v0` | interfaces and contracts |

## Runtime Dialects

These describe live system behavior and topology.

| dialect | focus |
|---|---|
| `dal.v0` | deployments |
| `ral.v0` | resources |
| `sal.v0` | state |
| `eal.v0` | events |
| `tal.v0` | topology |
| `wal.v0` | workflows |
| `oal.v0` | observability |

## Assurance Dialects

These describe quality, risk, verification, and accountability.

| dialect | focus |
|---|---|
| `pal.v0` | policy |
| `qal.v0` | quality |
| `fal.v0` | failure and recovery |
| `goval.v0` | governance |
| `riskal.v0` | risk |
| `audal.v0` | audit |
| `val.v0` | verification |
| `lal.v0` | learning and calibration |

## Selection Rule

Start with the dialect that owns the primary graph question:

- "What is deployed?" -> DAL.
- "What can act?" -> CAL.
- "What happened?" -> EAL or AUDAL.
- "What is broken?" -> OAL or FAL.
- "What is allowed?" -> PAL.
- "What proves this works?" -> VAL.
- "What did the system learn?" -> LAL.

Then add only the adjacent dialects needed for explicit edges. For example, a
release graph might combine DAL with PAL, OAL, RISKAL, and VAL; it does not need
KAL or LAL unless the runtime is modeling knowledge or learning behavior.
