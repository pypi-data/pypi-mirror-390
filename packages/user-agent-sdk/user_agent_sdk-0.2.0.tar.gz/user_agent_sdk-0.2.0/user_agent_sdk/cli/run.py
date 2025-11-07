"""FastMCP run command implementation with enhanced type hints."""

import sys
import threading

from user_agent_sdk.utils.logger import get_logger

logger = get_logger(__name__)


def run_command(
        agent_spec: str,
        config_file: str | None = None,
        debug: bool = False,
        abort_signal: threading.Event = None,
        workers: int | None = None,
        record_logs: bool = False,
) -> None:
    """
    Run a user agent based on the provided configuration.

    Args:
        agent_spec: Path to the agent Python file to run
        config_file: Path to the configuration file where all the settings are stored, use either config_file or the other parameters
        debug: Enable debug logging useful for troubleshooting
        abort_signal: Optional threading event to signal abortion of the agent run
        workers: Number of worker threads to spawn for the agent
        record_logs: Enable recording of execution logs for each task
    """

    try:
        from user_agent_sdk.decorators import clear_user_agent_registry
        clear_user_agent_registry()

        # Load the agent module dynamically
        import importlib.util
        from pathlib import Path

        path = Path(agent_spec).resolve()
        module_name = path.stem  # module name from filename
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Run the user agent worker
        from user_agent_sdk.user_agent_runner import UserAgentRunner
        from user_agent_sdk.user_agent_runner import RunnerConfig

        runner = UserAgentRunner(
            config_file=config_file,
            debug=debug,
            abort_signal=abort_signal,
            workers=workers,
            record_logs=record_logs,
        )
        runner.run()
    except Exception as e:
        logger.error(f"Failed to run user agent: {e}", exc_info=e)
        sys.exit(1)
