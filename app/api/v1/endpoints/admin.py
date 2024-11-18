from fastapi import APIRouter
from .admin import router as admin_router

router = APIRouter()

# 将所有admin子模块的路由包含到主路由中
router.include_router(admin_router, prefix="")
