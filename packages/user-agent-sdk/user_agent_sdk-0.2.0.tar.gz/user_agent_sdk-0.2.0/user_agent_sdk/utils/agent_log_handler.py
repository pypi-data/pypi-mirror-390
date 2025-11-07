import time
from logging import Handler, LogRecord


class AgentLogHandler(Handler):
    logged_messages: list[tuple[int, str]] = []

    def emit(self, record: LogRecord):
        message = record.getMessage()
        self.logged_messages.append((int(time.time() * 1000), message))
