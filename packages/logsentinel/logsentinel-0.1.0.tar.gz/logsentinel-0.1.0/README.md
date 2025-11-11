# LogSentinel Python SDK

LogSentinel is a lightweight SDK for monitoring and analyzing logs in Python applications. It automatically captures request and response data, builds detailed metadata, and sends them to the LogSentinel AI platform for analysis.

## Installation

```bash
pip install logsentinel
```

## Setup

1. Go to the [LogSentinel Dashboard](https://sentinel.ivps.cloud) and create an API key.
2. Add it to your environment variables:

```bash
export LOGSENTINEL_API_KEY="your_api_key_here"
```

## Example (FastAPI)

```python
from fastapi import FastAPI
from logosentinel import LogSentinelASGIMiddleware

app = FastAPI()
app.add_middleware(LogSentinelASGIMiddleware)

@app.post("/hello")
async def hello(data: dict):
    return {"message": "Hello, world!", "received": data}
```

Logs will automatically be captured and sent to your LogSentinel dashboard for AI analysis.

## License

MIT License
