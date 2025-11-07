from importlib.metadata import version as _version

from user_agent_sdk.decorators import user_agent

__version__ = _version("user_agent_sdk")

__all__ = [
    "user_agent",
]
