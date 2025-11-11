import logging
from logosentinel.client.sync import LogSentinelClient

class LogSentinelHandler(logging.Handler):
    def __init__(self, api_key: str, level=logging.NOTSET, base_url: str = None, min_remote_level: str = "INFO"):
        super().__init__(level)
        self.client = LogSentinelClient(api_key, base_url) if api_key else None
        self.min_remote_level = min_remote_level

        # map level name to numeric threshold
        self.level_map = {
            "DEBUG": 10, "INFO": 20, "SUCCESS": 25,
            "WARNING": 30, "ERROR": 40, "CRITICAL": 50
        }
        self.min_value = self.level_map.get(self.min_remote_level.upper(), 20)

    def emit(self, record: logging.LogRecord):
        try:
            level_name = record.levelname
            level_val = self.level_map.get(level_name, record.levelno)
            message = self.format(record)
            metadata = {
                "logger": record.name,
                "pathname": record.pathname,
                "lineno": record.lineno,
            }
            if self.client and level_val >= self.min_value:
                self.client.send(message, level=level_name, metadata=metadata)
        except Exception:
            self.handleError(record)
