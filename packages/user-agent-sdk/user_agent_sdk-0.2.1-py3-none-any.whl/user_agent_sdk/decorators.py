import inspect
from functools import wraps
from typing import Callable, Any, List, Dict

# Registry to hold decorated methods and their config
user_agent_registry: List[Dict[str, Any]] = []


def user_agent(
        agent_id: str = None,
        worker_id: str = None,
        domain: str = None,
        poll_interval: int = 1000,
        workers: int = 1,
):
    def decorator(func: Callable):
        # Check if the function is async
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            # Store the function and config in the registry
            user_agent_config = {
                "func": async_wrapper,
                "config": {
                    "agent_id": agent_id,
                    "worker_id": worker_id,
                    "domain": domain,
                    "poll_interval": poll_interval,
                    "workers": workers,
                }
            }
            effective_wrapper = async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            # Store the function and config in the registry
            user_agent_config = {
                "func": func,
                "config": {
                    "agent_id": agent_id,
                    "worker_id": worker_id,
                    "domain": domain,
                    "poll_interval": poll_interval,
                    "workers": workers,
                }
            }
            effective_wrapper = wrapper

        user_agent_registry.append(user_agent_config)

        return effective_wrapper

    return decorator


def clear_user_agent_registry():
    """Utility function to clear the user agent registry."""
    user_agent_registry.clear()
