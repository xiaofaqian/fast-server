from fastapi import APIRouter, Depends, HTTPException, status
from app.services.admin_service import AdminService
from app.models.response import ResponseModel
from app.services.auth_service import get_current_admin
from typing import Optional

router = APIRouter()

@router.get("/stats/points-increase", response_model=ResponseModel)
async def get_points_increase(
    period: Optional[str] = None,
    current_admin = Depends(get_current_admin)
):
    """获取积分新增量统计数据
    
    Args:
        period (str, optional): 统计周期，可选值：
            - day: 日统计
            - week: 周统计
            - month: 月统计
            - None: 总量统计
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Success",
            "data": {
                "points_increase": int  # 积分增加总量
            }
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 400: period参数无效
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        # 验证period参数
        valid_periods = ["day", "week", "month", None]
        if period not in valid_periods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Must be one of: day, week, month, or None"
            )
        
        admin_service = AdminService()
        points_increase = await admin_service.get_points_increase(period)
        
        return ResponseModel(
            code=200,
            msg="Success",
            data={"points_increase": points_increase}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/stats/total-users", response_model=ResponseModel)
async def get_total_users(current_admin = Depends(get_current_admin)):
    """获取系统用户总数
    
    Args:
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Success",
            "data": {
                "total_users": int  # 用户总数
            }
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        admin_service = AdminService()
        total_users = await admin_service.get_total_users()
        
        return ResponseModel(
            code=200,
            msg="Success",
            data={"total_users": total_users}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/stats/active-users", response_model=ResponseModel)
async def get_active_users(current_admin = Depends(get_current_admin)):
    """获取活跃用户数量
    
    Args:
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Success",
            "data": {
                "active_users": int  # 活跃用户数量
            }
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        admin_service = AdminService()
        active_users = await admin_service.get_active_users()
        
        return ResponseModel(
            code=200,
            msg="Success",
            data={"active_users": active_users}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
