"""PyInstaller entry point for the bundled CADIVE hook (``cadive-hook.exe``).

Claude Code invokes this binary for every tool call, piping the PreToolUse event
on stdin. Because a frozen binary can't have per-install values baked in, it loads
the connection config (backend URL / agent key / agent id) from a small JSON file
the app's one-click "Connect" writes — ``~/.cadive/config.json`` by default, or
the path in the ``CADIVE_HOOK_CONFIG`` env var — then delegates to the stdlib
hook logic in :mod:`cadive_guard.hook`.

Keeping the secret in ``~/.cadive/config.json`` (not in Claude's
``settings.json``) means a project-scoped install won't leak the key if the repo
is committed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

_CONFIG_TO_ENV = {
    "url": "CADIVE_URL",
    "key": "CADIVE_API_KEY",
    "agent_id": "CADIVE_AGENT_ID",
    "approval_timeout": "CADIVE_HOOK_APPROVAL_TIMEOUT",
    "strict": "CADIVE_HOOK_STRICT",
}


def _load_config() -> None:
    cfg_path = os.getenv("CADIVE_HOOK_CONFIG") or str(Path.home() / ".cadive" / "config.json")
    try:
        cfg = json.loads(Path(cfg_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if not isinstance(cfg, dict):
        return
    # Don't clobber anything already set explicitly in the environment.
    for key, env_name in _CONFIG_TO_ENV.items():
        if key in cfg and os.getenv(env_name) is None:
            os.environ[env_name] = str(cfg[key])


_load_config()

from cadive_guard.hook import main  # noqa: E402  (after config is loaded into env)

main()
