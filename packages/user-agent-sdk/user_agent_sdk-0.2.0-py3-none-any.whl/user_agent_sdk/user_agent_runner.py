import threading
import time

from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration
from conductor.client.configuration.settings.authentication_settings import AuthenticationSettings
from conductor.client.worker.worker_interface import WorkerInterface
from user_agent_sdk.agent_worker import AgentWorker
from user_agent_sdk.decorators import user_agent_registry
from user_agent_sdk.utils.logger import get_logger

logger = get_logger(__name__)

AUTH_URL = "https://auth.next.akabot.io/realms/user-agent/protocol/openid-connect/token"
SERVICE_URL = "https://external-api.next.akabot.io/api"


class RunnerConfig:
    def __init__(
            self,
            client_id: str,
            client_secret: str,
            service_url: str,
            auth_url: str,
            agent_id: str = None,
            debug: bool = False,
    ):
        self.debug = debug
        self.client_id = client_id
        self.client_secret = client_secret
        self.service_url = service_url
        self.auth_url = auth_url
        self.agent_id = agent_id

        if not self.client_id or not self.client_secret or not self.service_url or not self.auth_url:
            raise ValueError("Client ID, Client Secret, Service URL, and Auth URL must be provided.")


class UserAgentRunner:
    def __init__(
            self,
            config: RunnerConfig = None,
            config_file: str = None,
            debug: bool | None = None,
            workers: int | None = None,
            record_logs: bool = False,
            abort_signal: threading.Event = None,
    ):
        if config:
            self.config = config
        else:
            config_file = config_file or "credentials.json"
            self.config = self.__load_config_from_file(config_file)
        if debug is not None:
            self.config.debug = debug
        self.abort_signal = abort_signal or threading.Event()
        self.workers = workers
        self.record_logs = record_logs

    @staticmethod
    def __load_config_from_file(config_file: str) -> RunnerConfig:
        import json
        with open(config_file, 'r') as file:
            config_data = json.load(file)

        config = RunnerConfig(
            client_id=config_data.get('clientId'),
            client_secret=config_data.get('clientSecret'),
            service_url=config_data.get('serviceUrl') or SERVICE_URL,
            auth_url=config_data.get('authUrl') or AUTH_URL,
            agent_id=config_data.get('agentId', None),
            debug=config_data.get('debug', False),
        )

        if not config.client_id:
            raise ValueError("Client ID must be provided in the configuration file.")
        if not config.client_secret:
            raise ValueError("Client Secret must be provided in the configuration file.")

        return config

    def run(self):
        workers: list[WorkerInterface] = []
        index = 0
        for entry in user_agent_registry:
            config = entry["config"]
            worker_count = self.workers if self.workers is not None else self.__get_value(config, "workers", 1)

            for _ in range(max(1, worker_count)):
                index += 1
                func = entry["func"]
                worker = AgentWorker(
                    task_def_name=self.__get_value(config, "agent_id", self.config.agent_id),
                    execute_function=func,
                    poll_interval=self.__get_value(config, "poll_interval", 1000),
                    domain=self.__get_value(config, "domain", None),
                    worker_id=self.__get_value(config, "worker_id", None),
                    index=index,
                    record_logs=self.record_logs,
                )
                workers.append(worker)

        configuration = Configuration(
            debug=self.config.debug,
            server_api_url=self.config.service_url,
            authentication_settings=AuthenticationSettings(
                key_id=self.config.client_id,
                key_secret=self.config.client_secret,
                auth_url=self.config.auth_url
            )
        )

        try:
            self._run_workers(workers, configuration)
        except KeyboardInterrupt:
            pass

    def _run_workers(self, workers: list[WorkerInterface], configuration: Configuration):
        with TaskHandler(workers, configuration) as task_handler:
            task_handler.start_threads()
            logger.info("User Agent worker started")

            # Main thread waits and responds to Ctrl+C
            try:
                while not self.abort_signal.is_set():
                    time.sleep(0.3)
            except KeyboardInterrupt:
                task_handler.stop_threads()
                task_handler.join_threads(1)

    @staticmethod
    def __get_value(config: dict, key: str, default=None):
        """
        Helper function to get a value from a configuration dictionary.
        """
        value = config.get(key, default)
        return value if value is not None else default
