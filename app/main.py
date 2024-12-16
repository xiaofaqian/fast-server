from datetime import datetime
import time
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import connect_to_redis, close_redis_connection
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.bills import router as bills_router
from app.core.scheduler import start_scheduler
from app.api.v1.endpoints.play import router as play_router

app = FastAPI(title=settings.PROJECT_NAME)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()
    await connect_to_redis()
    # 启动定时任务
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()
    await close_redis_connection()

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

# 包含路由
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(bills_router, prefix="/api/v1/bills", tags=["bills"])
app.include_router(play_router, prefix="/api/v1", tags=["play"])
# 47.98.192.59
# uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
