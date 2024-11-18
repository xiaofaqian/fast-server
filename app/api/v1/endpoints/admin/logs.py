from fastapi import APIRouter, Depends, HTTPException, status
from app.services.admin_service import AdminService
from app.models.response import ResponseModel
from app.services.auth_service import get_current_admin
from typing import Optional

router = APIRouter()

@router.get("/points/logs", response_model=ResponseModel)
async def get_points_logs(
    current_admin = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: int = -1
):
    """获取积分变动记录列表
    
    Args:
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
        skip (int): 分页起始位置，默认0
        limit (int): 每页记录数，默认10
        sort_by (str): 排序字段，默认created_at
        sort_order (int): 排序方式，1为升序，-1为降序，默认-1
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Success",
            "data": {
                "total": int,  # 总记录数
                "items": List[{  # 积分记录列表
                    "id": str,  # 记录ID
                    "user_id": str,  # 用户ID
                    "points": int,  # 积分变动数量
                    "reason": str,  # 变动原因
                    "created_at": datetime  # 创建时间
                }]
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
        logs_data = await admin_service.get_points_logs(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return ResponseModel(
            code=200,
            msg="Success",
            data=logs_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/logs", response_model=ResponseModel)
async def get_admin_logs(
    current_admin = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: int = -1,
    action: Optional[str] = None
):
    """获取管理员操作日志
    
    Args:
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
        skip (int): 分页起始位置，默认0
        limit (int): 每页记录数，默认10
        sort_by (str): 排序字段，默认created_at
        sort_order (int): 排序方式，1为升序，-1为降序，默认-1
        action (str, optional): 操作类型筛选
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Success",
            "data": {
                "total": int,  # 总记录数
                "items": List[{  # 日志列表
                    "id": str,  # 日志ID
                    "admin_id": str,  # 管理员ID
                    "action": str,  # 操作类型
                    "target_id": str,  # 操作目标ID
                    "details": dict,  # 操作详情
                    "created_at": datetime  # 操作时间
                }]
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
        logs_data = await admin_service.get_admin_logs(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            action=action
        )
        return ResponseModel(
            code=200,
            msg="Success",
            data=logs_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
