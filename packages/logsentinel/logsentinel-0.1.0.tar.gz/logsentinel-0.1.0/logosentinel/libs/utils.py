import time
import threading
from typing import Any, Dict
from datetime import datetime, timezone
import platform
import socket
import os
import traceback
import uuid

def utc_now_iso():
    """
    Return the time in isoformat
    
    Useful for system log timestamp
    """
    return datetime.now(timezone.utc).isoformat()

def safe_str(obj) -> str:
    try:
        return str(obj)
    except Exception:
        return "<unserializable>"


def run_in_thread(fn):
    """Decorator to run a function in a daemon thread."""
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        t.start()
        return t
    return wrapper


SENSITIVE_KEYS = [
    "KEY", "SECRET", "TOKEN", "PASSWORD", "API_KEY", "ACCESS", "PRIVATE"
]

def mask_sensitive_env(env: dict) -> dict:
    """Return a copy of env with sensitive values masked."""
    safe_env = {}
    for k, v in env.items():
        if any(s in k.upper() for s in SENSITIVE_KEYS):
            safe_env[k] = "***REDACTED***"
        else:
            safe_env[k] = v
    return safe_env


def build_metadata(scope=None, environ=None, exc=None, start_time=None, request=None, response=None,
                   request_body=None, response_body=None):
    """
    Build rich metadata for logging.

    Args:
        scope: ASGI scope object.
        environ: WSGI environ object.
        exc: Exception object if any.
        start_time: Request start time for duration calculation.
        request: Optional DRF/Starlette request object.
        response: Optional response object for status/body info.

    Returns:
        dict: enriched metadata for log submission.
    """
    duration = int((time.time() - start_time) * 1000) if start_time else None
    client_ip = "unknown"
    path = method = ""
    headers = {}
    query_params = {}
    body_length = None

    # ASGI
    if scope:
        path = scope.get("path", "")
        method = scope.get("method", "GET")
        client = scope.get("client")
        if client:
            client_ip = client[0]
        headers = {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
                   for k, v in scope.get("headers", [])}
        query_string = scope.get("query_string", b"")
        query_params = dict([q.split(b"=") for q in query_string.split(b"&") if b"=" in q])
        query_params = {k.decode(): v.decode() for k, v in query_params.items()}

    # WSGI
    elif environ:
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "")
        client_ip = environ.get("REMOTE_ADDR", "unknown")
        headers = {k[5:].replace("_", "-").title(): v for k, v in environ.items() if k.startswith("HTTP_")}
        query_params = environ.get("QUERY_STRING", "")
    
    # If DRF/Starlette Request object available
    if request:
        try:
            query_params = dict(request.query_params)
        except Exception:
            pass
        try:
            body_length = len(request.body) if hasattr(request, "body") else None
        except Exception:
            body_length = None

    # Response info
    status_code = None
    response_length = None
    if response:
        status_code = getattr(response, "status_code", None)
        response_length = len(getattr(response, "content", b"")) if hasattr(response, "content") else None

    # Build final metadata
    metadata = {
        "id": str(uuid.uuid4()),
        "path": path,
        "method": method,
        "duration_ms": duration,
        "client_ip": client_ip,
        "python_version": platform.python_version(),
        "os": platform.platform(),
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "thread_name": threading.current_thread().name,
        "timestamp": utc_now_iso(),
        "headers": headers,
        "query_params": query_params,
        "request_body_length": body_length,
        "response_status": status_code,
        "response_length": response_length,
        # "environment":  mask_sensitive_env(dict(os.environ)),  # optional: can filter for secrets
        "response_body_length": len(response_body) if response_body else None,
        "request_body": request_body,
        "response_body": response_body,
    }
    metadata["full_url"] = f"{metadata['headers'].get('schema', 'https')}://{metadata['headers'].get('host')}{metadata['path']}"


    # Exception info
    if exc:
        metadata.update({
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "stack_trace": traceback.format_exc(),
        })




    # Optional user/project info
    if request and hasattr(request, "user"):
        metadata["user"] = getattr(request.user, "username", None)
        metadata["project"] = getattr(request.user, "name", None)

    return metadata




