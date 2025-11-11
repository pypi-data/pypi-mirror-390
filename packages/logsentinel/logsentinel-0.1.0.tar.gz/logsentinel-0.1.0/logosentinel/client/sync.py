import requests
import logging
from typing import Dict, Optional
from logosentinel.config.prod import DEFAULT_API_KEY, DEFAULT_BASE_URL
from logosentinel.libs.utils import utc_now_iso, safe_str

logger = logging.getLogger("logsentinel.client.sync")

class LogSentinelClient:
    """
    Synchronous client that immediately sends logs to LogSentinel backend.
    """

    def __init__(self, api_key: str = DEFAULT_API_KEY, base_url: str = DEFAULT_BASE_URL):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "logsentinel-python-sdk/1.0",
        })

    def send(self, message: str, level: str = "INFO", metadata: Optional[Dict] = None):
        """
        Immediately send a log to the backend.
        """
        payload = {
            "timestamp": utc_now_iso(),
            "message": safe_str(message),
            "level": level.upper(),
            "metadata": metadata or {},
        }
        try:
            url = f"{self.base_url}/logs"
            response = self.session.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return response.json()  # optional, if backend returns JSON
        except requests.RequestException as e:
            logger.error("Failed to send log to LogSentinel: %s", e)
            return None
