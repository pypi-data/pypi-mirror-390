import time
import logging

from typing import Optional, Any

from logosentinel.client.a_sync import AsyncLogSentinelClient
from logosentinel.libs.utils import build_metadata
from logosentinel.config.prod import DEFAULT_BASE_URL, DEFAULT_API_KEY
logger = logging.getLogger("logsentinel.middleware")

status = None
response_body = b""
metadata = None

# ASGI middleware
class LogSentinelASGIMiddleware:
    def __init__(
        self,
        app: Optional[Any] =None,
        api_key: str= DEFAULT_API_KEY,
        base_url: Optional[str] = DEFAULT_BASE_URL,
        send_remote: bool = True,
    ):
        self.app = app
        self.client = AsyncLogSentinelClient(api_key, base_url) if send_remote else None

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        request_body = b""
        
        
        

        # --- Capture the incoming request body ---
        async def receive_wrapper():
            nonlocal request_body
            message = await receive()
            if message["type"] == "http.request":
                body_chunk = message.get("body", b"")
                request_body += body_chunk
            return message

        # --- Capture response info ---
        async def send_wrapper(message):
            nonlocal request_body
            nonlocal metadata
            nonlocal start
            status = ""
            response_body = b""

            if message["type"] == "http.response.start":
                status = message.get("status")
                metadata = build_metadata(
                    scope=scope,
                    start_time=start,
                    request_body=request_body.decode("utf-8", errors="ignore"),
                )
                metadata["response_status"] = status

            elif message["type"] == "http.response.body":
                body_chunk = message.get("body", b"")
                response_body += body_chunk

                if not message.get("more_body", False):
                    metadata["response_length"] = len(response_body)
                    metadata["request_body_length"] = len(request_body)

                    try:
                        metadata["response_body"] = response_body.decode("utf-8", errors="ignore")
                    except Exception:
                        metadata["response_body"] = "<could not decode>"

                    if self.client:
                        await self.client.send(
                            f"{metadata['method']} {metadata['path']} - {status}",
                            level="INFO",
                            metadata=metadata,
                        )

            await send(message)

        try:
            await self.app(scope, receive_wrapper, send_wrapper)
        except Exception as exc:
            metadata = build_metadata(
                scope=scope,
                exc=exc,
                start_time=start,
                request_body=request_body.decode("utf-8", errors="ignore"),
            )
            if self.client:
                await self.client.send(
                    f"Exception on {metadata['method']} {metadata['path']}",
                    level="ERROR",
                    metadata=metadata,
                )
            raise


# WSGI middleware
class LogSentinelWSGIMiddleware:
    def __init__(
        self,
        app: Optional[Any] =None,
        api_key: str = DEFAULT_API_KEY,
        base_url: Optional[str] = None,
        send_remote: bool = True,
    ):
        self.app = app
        self.client = AsyncLogSentinelClient(api_key, base_url) if send_remote else None

    def __call__(self, environ, start_response):
        start_time = time.time()

        def custom_start_response(status, response_headers, exc_info=None):
            try:
                status_code = int(status.split(" ", 1)[0])
            except Exception:
                status_code = 0

            metadata = build_metadata(environ=environ, start_time=start_time)
            metadata["status"] = status_code
            if self.client:
                self.client.send(
                    f"{metadata['method']} {metadata['path']} - {status_code}",
                    level="INFO",
                    metadata=metadata,
                )
            return start_response(status, response_headers, exc_info)

        try:
            return self.app(environ, custom_start_response)
        except Exception as exc:
            metadata = build_metadata(environ=environ, exc=exc, start_time=start_time)
            if self.client:
                self.client.send(
                    f"Exception on {metadata['method']} {metadata['path']}",
                    level="ERROR",
                    metadata=metadata,
                )
            raise
