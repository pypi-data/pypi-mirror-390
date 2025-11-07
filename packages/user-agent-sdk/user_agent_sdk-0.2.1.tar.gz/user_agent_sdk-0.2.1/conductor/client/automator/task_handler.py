import importlib
import threading
from typing import List

from conductor.client.automator.task_runner import TaskRunner
from conductor.client.configuration.configuration import Configuration
from conductor.client.worker.worker_interface import WorkerInterface
from user_agent_sdk.utils.logger import get_logger

logger = get_logger(__name__)


class TaskHandler:
    def __init__(
            self,
            workers: List[WorkerInterface] = [],
            configuration: Configuration = None,
            import_modules: List[str] = None
    ):
        # imports
        importlib.import_module('conductor.client.http.models.task')
        if import_modules is not None:
            for module in import_modules:
                logger.info(f'loading module {module}')
                importlib.import_module(module)

        if workers is None:
            workers = []
        elif not isinstance(workers, list):
            workers = [workers]

        # Initialize thread control event
        self.stop_event = threading.Event()
        self.threads = []

        self.__create_task_runner_threads(workers, configuration)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self.stop_event.is_set():
            self.stop_threads()

    def stop_threads(self) -> None:
        # Signal all threads to stop
        self.stop_event.set()
        logger.info('Stop event set, worker threads will exit gracefully...')

    def start_threads(self) -> None:
        logger.info('Starting worker threads...')
        # Clear any existing stop signal
        self.stop_event.clear()
        self.__start_task_runner_threads()
        logger.info('Started all threads')

    def join_threads(self, timeout: int = None) -> None:
        try:
            self.__join_task_runner_threads(timeout)
            logger.info('Joined all threads')
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt: Stopping all threads')
            self.stop_threads()

    def __create_task_runner_threads(
            self,
            workers: List[WorkerInterface],
            configuration: Configuration,
    ) -> None:
        self.task_runner_threads: list[threading.Thread] = []
        for worker in workers:
            self.__create_task_runner_thread(
                worker, configuration,
            )

    def __create_task_runner_thread(
            self,
            worker: WorkerInterface,
            configuration: Configuration,
    ) -> None:
        task_runner = TaskRunner(worker, configuration)
        thread = threading.Thread(target=self.__run_task_runner, args=(task_runner,))
        thread.daemon = True
        self.task_runner_threads.append(thread)

    def __run_task_runner(self, task_runner):
        # Use stop_event to control thread execution
        while not self.stop_event.is_set():
            try:
                task_runner.run_once()
            except Exception as e:
                logger.error(f"Error in task runner: {e}")
                # Prevent tight loop if there's an error - check stop event with timeout
                if not self.stop_event.wait(1):
                    continue  # Continue if timeout occurs and stop_event is not set

    def __start_task_runner_threads(self):
        n = 0
        for task_runner_thread in self.task_runner_threads:
            task_runner_thread.start()
            n = n + 1
        logger.info(f'Started {n} TaskRunner thread(s)')

    def __join_task_runner_threads(self, timeout: int = None):
        for task_runner_thread in self.task_runner_threads:
            task_runner_thread.join(timeout=timeout)
        logger.info('Joined TaskRunner threads')
