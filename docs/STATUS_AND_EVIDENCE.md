# Status and evidence

Prepared: **2026-11-24**. Documentation review updated: **2026-11-27**.

## Portfolio scope

Agent Factory is an Agent Execution Harness and orchestration project in development. This repository includes selected source components, a PM agent example and a curated architecture summary. It is not the full private project or a production release.

The original private repository and its history were not made public. Machine names, local user paths, private document identifiers, session identifiers and runtime logs from the internal handoff were excluded.

## Source-document update on 27 November 2026

The project owner supplied BUILD_PLAN.md and HANDOFF.md for review. This update summarizes those documents without publishing the private files or independently rerunning their tests.

- HANDOFF reports implemented path-based write controls, human gate approvals and requirements locking after Gate 1, with selected live checks on specified Claude Code versions.
- It reports 113 component tests on Windows: 111 passed and two skipped. Skipped checks remain unverified. This is a reported source-project result, separate from the 18 stop tests reproduced in this public portfolio on 24 November.
- The L1 stop mechanism blocks new tool calls in the documented checks; it does not establish termination of model calls or processes already running.
- Full orchestration and end-to-end client delivery are not established. The readiness checklist remains incomplete; cost tracking, dashboards and ROI are not demonstrated.
- The supplied documents contain stale headings and statuses. They are not evidence of the latest local runtime state. Earlier-version observations must not be presented as universal guarantees.
- This public repository still contains selected components only, not the full gate mechanism or an installable orchestration system.

## Evidence levels

| Claim | Evidence | Limit |
|---|---|---|
| Five core agent definitions exist | The source directory lists pm, spec, design, builder and qa files | File presence does not prove working coordination |
| A PM contract is defined | The full PM file was read and is included under examples | This is a configuration snapshot, not a verified runtime guarantee |
| Stop creation and hook response work in an isolated test harness | All 18 existing tests in test_stop.py passed on Linux with Python 3.12.14 on 2026-11-24 | No live Claude Code session or Windows reproduction was run |
| Gate approvals and document locking have implementation work | gate.py was observed; the internal handoff reports implementation and partial checks | Gate code and its test suite were not rerun or independently verified here |
| Current extension behavior is partly measured | The internal handoff has an update dated 2026-11-24 describing limited measurements | Version-specific historical report, not a current complete integration test |
| End-to-end delivery, dashboards and positive ROI are ready | No such evidence is established in this portfolio | Do not claim these outcomes |

## Reproduced test result

Command:

```bash
python3 -m unittest discover -s tests -p test_stop.py -v
```

Result:

```text
Ran 18 tests
OK
```

The source tests copy scripts into temporary project directories. They cover file creation, ISO timestamp formatting, reason sanitization, UTF-8, idempotence, parallel creation, failure behavior, and hook responses before/after stop activation and manual removal.

The hook tests run the Python process with synthetic JSON and inspect its exit code. They do not prove that a real agent tool call will be blocked by a registered hook, and do not test all malformed input or environment cases.

## Source mapping

| Public path | Original source path |
|---|---|
| scripts/stop.py | scripts/stop.py |
| .claude/hooks/stop.py | .claude/hooks/stop.py |
| tests/test_stop.py | tests/test_stop.py |
| examples/agents/pm.md | .claude/agents/pm.md |

These selected source files were copied without functional changes. The architecture and portfolio text are newly curated summaries of observed files and internal status documentation. Agent instructions are included as a sample; they are not instructions for a reader's own session.

The original root README is stale: it still describes the foundations stage without agents, while the agent files and later handoff describe further work. This portfolio uses the more specific evidence above and makes no blanket completion claim.

## Limits and next validation

- No live multi-agent routing, full human gate cycle or client delivery was reproduced.
- No settings file is supplied to register the hook or install role permissions.
- No security certification, complete tool isolation or production readiness is claimed.
- No measured project cost, task success rate, client adoption or ROI is available.
- The internal handoff itself records bypass risks and incomplete version-specific measurements.

Next: run a tiny synthetic requirement through intake, human approval, specification, build and QA; verify permission failures and stopping; repeat integration checks on the chosen runtime version; then define and measure a pilot baseline.

## Publication check

The selected source was read before publication and reviewed for common credential patterns and personal contact data. No runtime secrets, customer material or full handoff log were included. This is a limited check of this curated set, not a scan of the original repository or its full history.
