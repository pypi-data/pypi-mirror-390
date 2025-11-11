import asyncio
import httpx
import logging
from typing import Dict, Optional
from logosentinel.config.prod import DEFAULT_API_KEY, DEFAULT_BASE_URL
from logosentinel.libs.utils import utc_now_iso, safe_str

logger = logging.getLogger("logsentinel.async_client")

class AsyncLogSentinelClient:
    """
    Async client that immediately sends logs to LogSentinel backend using httpx.
    """

    def __init__(self, api_key: str = DEFAULT_API_KEY, base_url: str = DEFAULT_BASE_URL):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "logsentinel-python-sdk/1.0",
                },
                timeout=5.0
            )
        return self._client

    async def send(self, message: str, level: str = "INFO", metadata: Optional[Dict] = None):
        payload = {
            "timestamp": utc_now_iso(),
            "message": safe_str(message),
            "level": level.upper(),
            "metadata": metadata or {},
        }
        try:
            client = await self._get_client()
            response = await client.post(f"{self.base_url}/api/sdk/logs", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to send log to LogSentinel: %s", e)
            return None

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
