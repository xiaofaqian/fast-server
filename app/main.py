# app/main.py

from datetime import datetime
import time
from fastapi import FastAPI, Request
from app.api.v1.endpoints.play import router as play_router

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    request_body = await request.body()
    print(f"{current_time} - {request.method} {request.url.path} - Body: {request_body.decode('utf-8')}")
    response = await call_next(request)
    return response
# 包含 play.py 中的路由
app.include_router(play_router, prefix="/api/v1")

# 如果你想在本地运行这个应用程序，可以使用以下代码
# 在终端中运行：uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
