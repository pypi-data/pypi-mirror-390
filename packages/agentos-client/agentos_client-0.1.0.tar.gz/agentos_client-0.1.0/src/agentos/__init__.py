"""Agent‑OS unified SDK and CLI (remote‑only).

Import surface:

    from agentos import Agent, PolicyDeniedError, tool
    from agentos import PolicyEnforcer

Distribution name on PyPI is ``agent-os``; import name is ``agentos``.
"""

# Re-export from the implementation package (distribution name: agent-os)
from agent_os.sdk import Agent, tool, PolicyDeniedError  # noqa: F401
from agent_os.enforcer import PolicyEnforcer  # noqa: F401

__version__ = "0.1.0"
version = __version__

__all__ = [
    "Agent",
    "tool",
    "PolicyDeniedError",
    "PolicyEnforcer",
    "__version__",
    "version",
]

__version__ = "0.1.0"
version = __version__  # convenience alias

__all__ = ["Agent", "tool", "PolicyDeniedError", "PolicyEnforcer", "__version__", "version"]
