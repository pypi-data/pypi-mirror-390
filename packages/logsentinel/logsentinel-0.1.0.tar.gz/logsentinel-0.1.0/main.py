# from logosentinel import SentinelLogger, LogSentinelClient

# logger = SentinelLogger(base_url="http://localhost:8000")

# logger.info("✅ This is a test log from the Python SDK!")

# client = LogSentinelClient()
# client.send("Hello people")
# test_asgi.py
from fastapi import FastAPI, HTTPException, responses
from logosentinel import LogSentinelASGIMiddleware

# API_KEY = "your_test_api_key_here"

app = FastAPI()

# app.add_middleware(LogSentinelASGIMiddleware(app, api_key=API_KEY), )
# Wrap your FastAPI app with LogSentinel middleware
# app = LogSentinelASGIMiddleware(app, api_key=API_KEY)
app.add_middleware(
    LogSentinelASGIMiddleware,
   # api_key=API_KEY,
    send_remote=True
)

@app.post("/hello")
async def hello_post(payload: dict):
    return responses.JSONResponse(content={"detail": "Invalid user credentials"}, status_code=401)

@app.get("/error")
async def error():
    # This will trigger exception logging
    raise HTTPException(status_code=500, detail="Test error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)


