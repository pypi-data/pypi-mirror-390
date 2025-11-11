import logging
from rich.console import Console
from logosentinel.client.sync import LogSentinelClient

console = Console()

class SentinelLogger:
    LEVELS = {"DEBUG":10,"INFO":20,"SUCCESS":25,"WARNING":30,"ERROR":40,"CRITICAL":50}
    COLOR = {"DEBUG":"magenta","INFO":"cyan","SUCCESS":"green","WARNING":"yellow","ERROR":"red","CRITICAL":"bold red"}

    def __init__(self, api_key: str = None, base_url: str = None, send_remote: bool = True, min_remote_level: str = "INFO"):
        self.client = LogSentinelClient(api_key, base_url) if send_remote and api_key else None
        self.send_remote = send_remote and api_key is not None
        self.min_remote_level = min_remote_level.upper()
        self.min_remote_value = self.LEVELS.get(self.min_remote_level, 20)

    def _log(self, level: str, msg: str, **kwargs):
        level = level.upper()
        console.print(f"[{self.COLOR.get(level,'white')}][{level}][/]: {msg}")
        if self.send_remote and self.client and self.LEVELS.get(level,20) >= self.min_remote_value:
            self.client.send(msg, level=level, metadata=kwargs)

    def debug(self,msg,**k): self._log("DEBUG",msg,**k)
    def info(self,msg,**k): self._log("INFO",msg,**k)
    def success(self,msg,**k): self._log("SUCCESS",msg,**k)
    def warning(self,msg,**k): self._log("WARNING",msg,**k)
    def error(self,msg,**k): self._log("ERROR",msg,**k)
    def critical(self,msg,**k): self._log("CRITICAL",msg,**k)
    def exception(self,msg,**k):
        import traceback
        self._log("ERROR", f"{msg}\n{traceback.format_exc()}", **k)
