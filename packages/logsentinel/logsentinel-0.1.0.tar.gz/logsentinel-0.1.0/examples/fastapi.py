
from fastapi import FastAPI, HTTPException, responses
from logosentinel import LogSentinelASGIMiddleware


app = FastAPI()
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
    raise HTTPException(status_code=500, detail="Test error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)


