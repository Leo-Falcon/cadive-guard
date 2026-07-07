"""Example: guarding a Claude Code style agent with CADIVE.

Run the backend first (uvicorn app.main:app), create an agent + rules, then:

    python example_integration.py <AGENT_ID>
"""

from __future__ import annotations

import asyncio
import os
import sys

from cadive_guard import CadiveBlocked, CadiveGuard


async def claude_code_call(task: str) -> str:
    """Stand-in for a real model/tool call."""
    await asyncio.sleep(0.05)
    return f"completed: {task}"


async def main(agent_id: str) -> None:
    guard = CadiveGuard(
        agent_id=agent_id,
        backend_url="http://localhost:8000",
        api_key=os.getenv("CADIVE_API_KEY"),  # mint one in the console; required if auth is on
        fail_mode="hard",  # block if CADIVE is unreachable
    )

    # Option A — wrap an existing agent so every call is validated.
    async def my_agent(task: str) -> str:
        return await claude_code_call(task)

    wrapped_agent = guard.monitor(my_agent)

    try:
        print(await wrapped_agent("summarise the repo"))
    except CadiveBlocked as exc:
        print(f"Blocked: {exc.decision.reasoning}")

    # Option B — validate specific actions explicitly (full control).
    decision = await guard.avalidate(
        action="api_call",
        details={"url": "https://api.anthropic.com/v1/messages"},
        metadata={"cost": 0.02, "tokens": 1500},
    )
    print(f"api_call -> {decision.decision} ({decision.reasoning})")

    delete_decision = await guard.avalidate(action="delete", details={"path": "/etc/hosts"})
    print(f"delete -> {delete_decision.decision} ({delete_decision.reasoning})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python example_integration.py <AGENT_ID>")
        raise SystemExit(1)
    asyncio.run(main(sys.argv[1]))
