from fastapi import APIRouter
from . import auth, user_management, stats, logs

router = APIRouter()

# 添加各个子模块的路由
router.include_router(auth.router, tags=["admin-auth"])
router.include_router(user_management.router, tags=["admin-user-management"])
router.include_router(stats.router, tags=["admin-stats"])
router.include_router(logs.router, tags=["admin-logs"])
