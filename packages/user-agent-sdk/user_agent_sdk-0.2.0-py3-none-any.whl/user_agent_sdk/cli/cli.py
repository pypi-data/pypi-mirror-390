import platform
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated

import cyclopts
from rich.console import Console
from rich.table import Table

import user_agent_sdk
from user_agent_sdk.cli import run as run_module
from user_agent_sdk.utils.logger import LogLevelType, configure_logging
from user_agent_sdk.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

app = cyclopts.App(
    name="user agent sdk",
    help="A secure SDK for building custom user agents (workers) that run in your environment and connect safely with the akaBot 2.0 platform.",
    version=user_agent_sdk.__version__,
)


def _get_npx_command():
    """Get the correct npx command for the current platform."""
    if sys.platform == "win32":
        # Try both npx.cmd and npx.exe on Windows
        for cmd in ["npx.cmd", "npx.exe", "npx"]:
            try:
                subprocess.run([cmd, "--version"], check=True, capture_output=True)
                return cmd
            except subprocess.CalledProcessError:
                continue
        return None
    return "npx"  # On Unix-like systems, just use npx


def _parse_env_var(env_var: str) -> tuple[str, str]:
    """Parse environment variable string in format KEY=VALUE."""
    if "=" not in env_var:
        logger.error("Invalid environment variable format. Must be KEY=VALUE")
        sys.exit(1)
    key, value = env_var.split("=", 1)
    return key.strip(), value.strip()


@contextmanager
def with_argv(args: list[str] | None):
    """Temporarily replace sys.argv if args provided.

    This context manager is used at the CLI boundary to inject
    server arguments when needed, without mutating sys.argv deep
    in the source loading logic.

    Args are provided without the script name, so we preserve sys.argv[0]
    and replace the rest.
    """
    if args is not None:
        original = sys.argv[:]
        try:
            # Preserve the script name (sys.argv[0]) and replace the rest
            sys.argv = [sys.argv[0], *args]
            yield
        finally:
            sys.argv = original
    else:
        yield


@app.command
def version():
    """Display version information and platform details."""
    info = {
        "UserAgentSdk version": user_agent_sdk.__version__,
        "Python version": platform.python_version(),
        "Platform": platform.platform(),
        "Root path": Path(user_agent_sdk.__file__).resolve().parents[1],
    }

    g = Table.grid(padding=(0, 1))
    g.add_column(style="bold", justify="left")
    g.add_column(style="cyan", justify="right")
    for k, v in info.items():
        g.add_row(k + ":", str(v).replace("\n", " "))

    console.print(g)


@app.command
def run(
        agent_spec: Annotated[
            str,
            cyclopts.Parameter(
                name=["--path", "-p"],
                help="Path to agent python file to run",
            ),
        ],
        config_file: Annotated[
            str | None,
            cyclopts.Parameter(
                name=["--config-file", "-c"],
                help="Path to configuration file, if not provided will auto-detect",
            )] = None,
        workers: Annotated[
            int | None,
            cyclopts.Parameter(
                name=["--workers", "-w"],
                help="Number of worker threads to spawn for the agent",
            )] = None,
        record_execution_logs: Annotated[
            bool,
            cyclopts.Parameter(
                name=["--record-execution-logs", "-r"],
                help="Enable recording of execution logs for each task",
            ),
        ] = False,
        log_level: Annotated[
            LogLevelType,
            cyclopts.Parameter(
                name=["--log-level", "-l"],
                help="Set the logging level",
                show_default=True,
            )] = "INFO",
        debug: Annotated[
            bool,
            cyclopts.Parameter(
                name=["--debug", "-d"],
                help="Enable debug logging useful for troubleshooting",
            ),
        ] = False,
) -> None:
    """
    Run a user agent

    Args:
        agent_spec: Path to agent python file to run
        config_file: Path to configuration file, if not provided will auto-detect
        workers: Number of worker threads to spawn for the agent\
        record_execution_logs: Enable recording of execution logs for each task
        log_level: Set the logging level
        debug: Enable debug logging useful for troubleshooting
    """

    configure_logging(
        level=log_level,
    )

    run_module.run_command(
        agent_spec=agent_spec,
        config_file=config_file,
        debug=debug,
        workers=workers,
        record_logs=record_execution_logs,
    )


@app.command
def history(
        agent_id: Annotated[
            str | None,
            cyclopts.Parameter(
                name=["--agent-id", "-a"],
                help="Filter by agent ID",
            ),
        ] = None,
        user_agent_id: Annotated[
            str | None,
            cyclopts.Parameter(
                name=["--user-agent-id", "-u"],
                help="Filter by user agent ID",
            ),
        ] = None,
        limit: Annotated[
            int,
            cyclopts.Parameter(
                name=["--limit", "-n"],
                help="Maximum number of records to display",
                show_default=True,
            ),
        ] = 50,
        db_path: Annotated[
            str,
            cyclopts.Parameter(
                name=["--db-path", "-db"],
                help="Path to the execution history database",
                show_default=True,
            ),
        ] = "execution_history.db",
        export_csv: Annotated[
            str | None,
            cyclopts.Parameter(
                name=["--export-csv", "-e"],
                help="Export history to CSV file at the specified path",
            ),
        ] = None,
) -> None:
    """
    Show execution history of user agents

    Args:
        agent_id: Filter by agent ID
        user_agent_id: Filter by user agent ID
        limit: Maximum number of records to display
        db_path: Path to the execution history database
        export_csv: Export history to CSV file at the specified path
    """
    from user_agent_sdk.utils.execution_history import ExecutionHistory
    from rich.table import Table

    history_db = ExecutionHistory(db_path=db_path)

    try:
        records = history_db.get_history(
            agent_id=agent_id,
            user_agent_id=user_agent_id,
            limit=limit
        )

        if not records:
            console.print("[yellow]No execution history found.[/yellow]")
            return

        # Export to CSV if requested
        if export_csv:
            import csv
            try:
                with open(export_csv, 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    # Write header
                    csv_writer.writerow([
                        "ID", "Task ID", "Agent ID", "User Agent ID",
                        "Started At", "Ended At", "Status",
                        "Input Data", "Output Data", "Error Message"
                    ])
                    # Write records
                    for record in records:
                        csv_writer.writerow([
                            record[0],  # id
                            record[1] or "",  # task_id
                            record[2] or "",  # agent_id
                            record[3] or "",  # user_agent_id
                            record[4] or "",  # started_at
                            record[5] or "",  # ended_at
                            record[6] or "",  # status
                            record[7] or "",  # input_data
                            record[8] or "",  # output_data
                            record[9] or "",  # error_message
                        ])
                console.print(f"[green]✓[/green] Exported {len(records)} record(s) to [cyan]{export_csv}[/cyan]")
            except Exception as e:
                console.print(f"[red]Error exporting to CSV: {e}[/red]")
                return

        # Create table for display
        table = Table(title="Execution History", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Task ID", width=12)
        table.add_column("Agent ID", width=20)
        table.add_column("User Agent ID", width=20)
        table.add_column("Started At", width=19)
        table.add_column("Ended At", width=19)
        table.add_column("Status", width=10)
        table.add_column("Error", width=30)

        for record in records:
            # record format: (id, task_id, agent_id, user_agent_id, started_at, ended_at, status, input_data, output_data, error_message)
            record_id, task_id, agent_id_val, user_agent_id_val, started_at, ended_at, status, input_data, output_data, error_message = record

            # Color code status
            status_style = "[green]✓[/green]" if status == "success" else "[red]✗[/red]"
            status_text = f"{status_style} {status}"

            # Truncate error message if too long
            error_display = (error_message[:27] + "...") if error_message and len(error_message) > 30 else (
                    error_message or "")

            table.add_row(
                str(record_id),
                task_id or "",
                agent_id_val or "",
                user_agent_id_val or "",
                started_at or "",
                ended_at or "",
                status_text,
                error_display
            )

        console.print(table)
        console.print(f"\n[dim]Showing {len(records)} record(s)[/dim]")

    finally:
        history_db.close()


@app.command(name=["history-detail", "hd"])
def history_detail(
        record_id: Annotated[
            int,
            cyclopts.Parameter(
                help="ID of the execution history record to display",
            ),
        ],
        db_path: Annotated[
            str,
            cyclopts.Parameter(
                name=["--db-path", "-db"],
                help="Path to the execution history database",
                show_default=True,
            ),
        ] = "execution_history.db",
) -> None:
    """
    Show detailed information about a specific execution history record

    Args:
        record_id: ID of the execution history record to display
        db_path: Path to the execution history database
    """
    from user_agent_sdk.utils.execution_history import ExecutionHistory
    from rich.panel import Panel
    from rich.syntax import Syntax
    import json

    history_db = ExecutionHistory(db_path=db_path)

    try:
        record = history_db.get_record_by_id(record_id)

        if not record:
            console.print(f"[red]No execution history found with ID: {record_id}[/red]")
            return

        # Unpack record
        # record format: (id, task_id, agent_id, user_agent_id, started_at, ended_at, status, input_data, output_data, error_message)
        rec_id, task_id, agent_id, user_agent_id, started_at, ended_at, status, input_data, output_data, error_message = record

        # Display basic info
        console.print(f"\n[bold magenta]Execution History Detail - ID: {rec_id}[/bold magenta]\n")

        from rich.table import Table
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column(style="bold cyan", justify="right")
        info_table.add_column(style="white")

        info_table.add_row("Task ID:", task_id or "N/A")
        info_table.add_row("Agent ID:", agent_id or "N/A")
        info_table.add_row("User Agent ID:", user_agent_id or "N/A")
        info_table.add_row("Started At:", started_at or "N/A")
        info_table.add_row("Ended At:", ended_at or "N/A")

        # Color code status
        status_display = f"[green]✓ {status}[/green]" if status == "success" else f"[red]✗ {status}[/red]"
        info_table.add_row("Status:", status_display)

        console.print(info_table)
        console.print()

        # Display error message if present
        if error_message:
            console.print(Panel(
                error_message,
                title="[bold red]Error Message[/bold red]",
                border_style="red",
                expand=False
            ))
            console.print()

        # Display input data
        if input_data:
            try:
                parsed_input = json.loads(input_data)
                formatted_input = json.dumps(parsed_input, indent=2)
                syntax = Syntax(formatted_input, "json", theme="monokai", line_numbers=False)
                console.print(Panel(
                    syntax,
                    title="[bold cyan]Input Data[/bold cyan]",
                    border_style="cyan",
                    expand=False
                ))
            except json.JSONDecodeError:
                console.print(Panel(
                    input_data,
                    title="[bold cyan]Input Data (raw)[/bold cyan]",
                    border_style="cyan",
                    expand=False
                ))
            console.print()

        # Display output data
        if output_data:
            try:
                parsed_output = json.loads(output_data)
                formatted_output = json.dumps(parsed_output, indent=2)
                syntax = Syntax(formatted_output, "json", theme="monokai", line_numbers=False)
                console.print(Panel(
                    syntax,
                    title="[bold green]Output Data[/bold green]",
                    border_style="green",
                    expand=False
                ))
            except json.JSONDecodeError:
                console.print(Panel(
                    output_data,
                    title="[bold green]Output Data (raw)[/bold green]",
                    border_style="green",
                    expand=False
                ))
            console.print()

    finally:
        history_db.close()


@app.command
def dev(
        agent_spec: Annotated[
            str,
            cyclopts.Parameter(
                name=["--path", "-p"],
                help="Path to agent python file to run",
            ),
        ],
        config_file: Annotated[
            str | None,
            cyclopts.Parameter(
                name=["--config-file", "-c"],
                help="Path to configuration file, if not provided will auto-detect",
            )] = None,
        workers: Annotated[
            int | None,
            cyclopts.Parameter(
                name=["--workers", "-w"],
                help="Number of worker threads to spawn for the agent",
            )] = None,
        log_level: Annotated[
            LogLevelType,
            cyclopts.Parameter(
                name=["--log-level", "-l"],
                help="Set the logging level",
                show_default=True,
            )] = "INFO",
        debug: Annotated[
            bool,
            cyclopts.Parameter(
                name=["--debug", "-d"],
                help="Enable debug logging useful for troubleshooting",
            ),
        ] = False,
) -> None:
    """
    Run a user agent in development mode with auto-reload on file changes

    Args:
        agent_spec: Path to agent python file to run
        config_file: Path to configuration file, if not provided will auto-detect
        workers: Number of worker threads to spawn for the agent
        log_level: Set the logging level
        debug: Enable debug logging useful for troubleshooting
    """

    configure_logging(
        level=log_level,
    )

    import time
    import threading
    from pathlib import Path
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    agent_path = Path(agent_spec).resolve()

    if not agent_path.exists():
        logger.error(f"Agent file not found: {agent_path}")
        sys.exit(1)

    # Track the running thread and abort signal
    current_thread: threading.Thread | None = None
    abort_signal: threading.Event | None = None

    def start_agent():
        """Start the agent in a separate thread."""
        nonlocal current_thread, abort_signal

        # Stop existing thread if running
        if current_thread and current_thread.is_alive():
            logger.info("Stopping existing agent thread...")
            abort_signal.set()
            current_thread.join(timeout=5)
            if current_thread.is_alive():
                logger.warning("Agent thread did not stop gracefully")

        # Create new abort signal and start new thread
        logger.info(f"Starting agent from {agent_path}...")
        abort_signal = threading.Event()
        current_thread = threading.Thread(
            target=run_module.run_command,
            kwargs={
                "agent_spec": agent_spec,
                "config_file": config_file,
                "debug": debug,
                "abort_signal": abort_signal,
                "workers": workers,
            }
        )
        current_thread.daemon = True
        current_thread.start()

    class AgentFileHandler(FileSystemEventHandler):
        """Handle file system events for the agent file."""

        def __init__(self):
            self.last_modified = time.time()
            self.debounce_seconds = 1.0  # Debounce to avoid multiple reloads

        def on_modified(self, event):
            if event.src_path == str(agent_path):
                current_time = time.time()
                if current_time - self.last_modified > self.debounce_seconds:
                    self.last_modified = current_time
                    console.print(f"[yellow]File changed: {agent_path.name}[/yellow]")
                    console.print("[cyan]Reloading agent...[/cyan]")
                    start_agent()

    # Start the agent initially
    console.print("[green]Development mode started[/green]")
    console.print(f"[cyan]Watching: {agent_path}[/cyan]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    start_agent()

    # Setup file watcher
    event_handler = AgentFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(agent_path.parent), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
            # Check if thread is still alive
            if current_thread and not current_thread.is_alive():
                logger.warning("Agent thread stopped unexpectedly")
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
        observer.stop()
        if abort_signal:
            abort_signal.set()
        if current_thread and current_thread.is_alive():
            current_thread.join(timeout=5)
    finally:
        observer.join()


if __name__ == "__main__":
    app()
