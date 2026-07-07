# cadive-guard

The source-available client that stands between an AI agent and the actions it's about
to take.

[CADIVE](https://cadive.net) is a guard for AI agents — before an agent (Claude Code, a
chatbot, anything with real tool access) does something, CADIVE checks it against your
rules first. This repo is the part that actually runs on your machine and asks the
question. The source is public on purpose: if something is intercepting every tool call
your agent makes, you should be able to read exactly what it does, not just trust a
vendor's word for it.

You're free to read, run, and modify this code for your own use, including
commercially (Using the Cadive-guard to block your agents going rogue, in your business. Comercially DOES NOT mean you get to distribute it) — guard your own agents, at your own company, no strings attached. What
you can't do is hand it (as-is or modified) to someone else as part of a product or
service you give them — that includes an unrelated product, not just a competing one.
If you want to build that in, talk to us first — see [License](#license) below.

The detection logic itself (the rules engine, anomaly detection, and CADIVE's paid
features) lives in the CADIVE backend — see [cadive.net](https://cadive.net) for the full
product. This SDK is the thin, dependency-free, auditable client that talks to it.

## Install

```bash
pip install -e .            # from this directory
# or just copy the cadive_guard/ package next to your agent
```

## Usage

```python
from cadive_guard import CadiveGuard

guard = CadiveGuard(
    agent_id="claude_code_agent_1",
    backend_url="http://localhost:8000",
    api_key="sk_agt_...",   # mint one per agent in the console (API Keys page)
    fail_mode="hard",       # "hard": block if CADIVE is down; "soft": allow
)

# Wrap an agent — every call is validated first.
wrapped = guard.monitor(my_agent)
await wrapped("do something")

# Or validate specific actions explicitly.
decision = await guard.avalidate(
    action="api_call",
    details={"url": "https://api.anthropic.com/v1/messages"},
    metadata={"cost": 0.02},
)
if decision.blocked:
    ...  # handle deny/pause
```

### Claude Code

The same package ships a `cadive-hook` console script that speaks Claude Code's
`PreToolUse`/`PostToolUse` hook protocol directly — see `cadive_guard/hook.py` for the
exact stdin/stdout contract, and [cadive.net](https://cadive.net) for the one-click
console setup.

## Semantics

| Decision  | `allowed` | `blocked` | Wrapper behaviour                    |
|-----------|-----------|-----------|--------------------------------------|
| allowed   | ✅        |           | runs the function                    |
| flagged   | ✅        |           | runs, but recorded as suspicious     |
| paused    |           | ✅        | raises `CadiveBlocked`               |
| denied    |           | ✅        | raises `CadiveBlocked`               |

Set `raise_on_block=False` to get the `CadiveDecision` back instead of an
exception (the wrapper then returns `None` for blocked calls).

## Failure handling (fail closed)

The client is built to **fail closed** — when in doubt, it does not let the
action run:

- **Backend unreachable** — with `fail_mode="hard"` (the default) `validate()`
  raises `CadiveUnavailable`, so the wrapped action never executes. Use
  `fail_mode="soft"` only when availability matters more than enforcement; it
  treats an unreachable backend as `allowed`.
- **Unrecognized response** — if the backend returns a 2xx whose body has no
  known `decision`, the client treats it as `denied` rather than assuming
  `allowed`.

This is the one behavioral guarantee worth reading the source to verify yourself,
which is the whole point of this being a separate, open repo.

## Tests

```bash
pip install -e ".[dev]"   # installs pytest
python -m pytest          # no backend needed — the client is mocked
```

## License

[Cadive Open License v1.1](LICENSE) — free to use, copy, and modify for your own
purposes, including commercially. Not allowed without Cadive's written consent:
shipping the Software (as-is or modified) to a third party as part of any product or
service you offer — related or unrelated to CADIVE — building a competing
agent-guarding product, reselling it under a new name, or rebranding a fork as an
official Cadive release. Violating those terms ends your license immediately and any
further use is copyright infringement — see the LICENSE file for the full terms.

The CADIVE backend (detection rules, safeguard catalog, and paid features) is closed
source and not covered by this license.
