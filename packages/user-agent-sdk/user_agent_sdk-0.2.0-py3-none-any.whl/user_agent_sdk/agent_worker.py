import dataclasses
import datetime
import inspect
import json
import time
import traceback
from typing import Callable, Any

from conductor.client.http.api_client import ApiClient
from conductor.client.http.models import Task, TaskResult, TaskExecLog
from conductor.client.http.models.task_result_status import TaskResultStatus
from conductor.client.worker.worker_interface import WorkerInterface
from user_agent_sdk.utils.agent_log_handler import AgentLogHandler
from user_agent_sdk.utils.exception import NonRetryableException
from user_agent_sdk.utils.execution_history import execution_history
from user_agent_sdk.utils.logger import get_logger

logger = get_logger(__name__)


class AgentWorker(WorkerInterface):
    def __init__(
            self,
            task_def_name: str,
            execute_function: Callable,
            poll_interval: float = 1000,
            domain: str = None,
            worker_id: str = None,
            index: int = 0,
            record_logs: bool = False,
    ):
        super().__init__(task_def_name)
        self.execute_function = execute_function
        self.poll_interval = poll_interval
        self.domain = domain
        self.worker_id = worker_id
        self.api_client = ApiClient()
        self.index = index
        self.record_logs = record_logs

    def get_identity(self) -> str:
        return self.worker_id if self.worker_id else super().get_identity()

    def execute(self, task: Task):
        task_result: TaskResult = self.get_task_result_from_task(task)
        agent_logger = get_logger(f"{self.get_identity()}.${self.index}")
        log_handler = AgentLogHandler()
        agent_logger.addHandler(log_handler)

        def save_log():
            logs = self.__convert_logged_messages_to_logs(log_handler.logged_messages, task.task_id)
            task_result.logs = logs

        platform_task_id = task.input_data.get("__task_id__")
        platform_agent_id = task.input_data.get("__deployed_workflow_id__")
        started_at = datetime.datetime.now()

        try:
            self.__normalize_task_input_data(task)
            task_output = self.__run_sync(
                self.execute_function,
                input_data=task.input_data,
                logger=agent_logger,
                task=task,
                platform_task_id=platform_task_id,
                platform_agent_id=platform_agent_id
            )

            save_log()

            if type(task_output) == TaskResult:
                task_output.task_id = task.task_id
                task_output.workflow_instance_id = task.workflow_instance_id
                return task_output
            else:
                task_result.status = TaskResultStatus.COMPLETED
                task_result.output_data = task_output

        except NonRetryableException as ne:
            save_log()
            task_result.status = TaskResultStatus.FAILED_WITH_TERMINAL_ERROR
            if len(ne.args) > 0:
                task_result.reason_for_incompletion = ne.args[0]

        except Exception as ne:
            logger.error(
                f'Error executing task {task.task_def_name} with id {task.task_id}.  error = {traceback.format_exc()}')
            save_log()
            task_result.logs = [
                *task_result.logs,
                TaskExecLog(traceback.format_exc(), task_result.task_id, int(time.time()))
            ]
            task_result.status = TaskResultStatus.FAILED
            if len(ne.args) > 0:
                task_result.reason_for_incompletion = ne.args[0]
        finally:
            agent_logger.removeHandler(log_handler)

        if dataclasses.is_dataclass(type(task_result.output_data)):
            task_output = dataclasses.asdict(task_result.output_data)
            task_result.output_data = task_output
            return task_result
        if not isinstance(task_result.output_data, dict):
            task_output = task_result.output_data
            task_result.output_data = self.api_client.sanitize_for_serialization(task_output)
            if not isinstance(task_result.output_data, dict):
                task_result.output_data = {'result': task_result.output_data}

        if self.record_logs:
            ended_at = datetime.datetime.now()
            execution_history.record(
                task_id=platform_task_id,
                agent_id=platform_agent_id,
                user_agent_id=self.task_definition_name,
                started_at=started_at.isoformat(),
                ended_at=ended_at.isoformat(),
                status="success" if task_result.status == TaskResultStatus.COMPLETED else "error",
                input_data=json.dumps(task.input_data),
                output_data=json.dumps(task_result.output_data),
                error_message=task_result.reason_for_incompletion,
            )

        return task_result

    @staticmethod
    def __convert_logged_messages_to_logs(
            logged_messages: list[tuple[int, str]],
            task_id: str
    ) -> list[TaskExecLog]:
        logs = []
        for timestamp, message in logged_messages:
            logs.append(TaskExecLog(
                task_id=task_id,
                log=message,
                created_time=timestamp
            ))
        return logs

    @staticmethod
    def __run_sync(func: Callable[..., Any], **kwargs) -> Any:
        """
        Run any function (sync or async) in a synchronous way safely.
        - If `func` is synchronous → executes directly.
        - If `func` is asynchronous → runs it using an event loop safely.
        - Works both inside or outside an existing event loop.
        """

        def call_with_matched_args(func, **kwargs):
            """Call `func` with only the arguments it accepts."""
            sig = inspect.signature(func)
            accepted = {
                k: v for k, v in kwargs.items()
                if k in sig.parameters
            }
            return func(**accepted)

        # Sync function → execute directly
        if not inspect.iscoroutinefunction(func):
            return call_with_matched_args(func, **kwargs)

        import asyncio

        try:
            # Case 1: Already running inside an event loop
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Case 2: No running loop → safe to start a new one
            return asyncio.run(call_with_matched_args(func, **kwargs))
        else:
            # Case 3: Inside an existing loop
            coro = call_with_matched_args(func, **kwargs)
            return loop.run_until_complete(coro)

    @staticmethod
    def __normalize_task_input_data(task: Task):
        # Remove internal keys that follow the pattern __*__
        keys_to_remove = [key for key in task.input_data.keys() if key.startswith("__") and key.endswith("__")]
        for key in keys_to_remove:
            del task.input_data[key]
