from fastapi import APIRouter, Depends, HTTPException, status
from app.services.admin_service import AdminService
from app.models.response import ResponseModel
from app.schemas.admin import UpdatePasswordRequest, IncreasePointsRequest
from app.schemas.user import UserUpdate
from app.services.auth_service import get_current_admin
from typing import Optional

router = APIRouter()

@router.get("/users", response_model=ResponseModel)
async def get_users(
    current_admin = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: int = -1
):
    """获取用户列表
    
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
                "total": int,  # 总用户数
                "items": List[{  # 用户列表
                    "id": str,  # 用户ID
                    "username": str,  # 用户名
                    "points": int,  # 用户积分
                    "created_at": datetime,  # 创建时间
                    "last_login": datetime  # 最后登录时间
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
        users_data = await admin_service.get_user_list(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            current_admin_id=str(current_admin.id)
        )
        return ResponseModel(
            code=200,
            msg="Success",
            data=users_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/users/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: str,
    current_admin = Depends(get_current_admin)
):
    """删除指定用户
    
    Args:
        user_id (str): 要删除的用户ID
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "User deleted successfully",
            "data": None
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 404: 用户不存在
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        admin_service = AdminService()
        result = await admin_service.delete_user(user_id, str(current_admin.id))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return ResponseModel(
            code=200,
            msg="User deleted successfully",
            data=None
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/users/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_admin = Depends(get_current_admin)
):
    """更新用户信息
    
    Args:
        user_id (str): 要更新的用户ID
        user_update (UserUpdate): {
            "username": str,  # 新用户名
            "points": int,  # 新积分值
            "status": str  # 新状态
        }
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "User updated successfully",
            "data": {
                "id": str,  # 用户ID
                "username": str,  # 更新后的用户名
                "points": int,  # 更新后的积分
                "status": str,  # 更新后的状态
                "updated_at": datetime  # 更新时间
            }
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 404: 用户不存在
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        admin_service = AdminService()
        updated_user = await admin_service.update_user(
            user_id,
            user_update.dict(exclude_unset=True),
            str(current_admin.id)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or could not be updated"
            )
            
        return ResponseModel(
            code=200,
            msg="User updated successfully",
            data=updated_user
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/users/{user_id}/password", response_model=ResponseModel)
async def update_user_password(
    user_id: str,
    password_update: UpdatePasswordRequest,
    current_admin = Depends(get_current_admin)
):
    """更新用户密码
    
    Args:
        user_id (str): 要更新密码的用户ID
        password_update (UpdatePasswordRequest): {
            "new_password": str  # 新密码
        }
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "User password updated successfully",
            "data": {
                "id": str,  # 用户ID
                "username": str,  # 用户名
                "updated_at": datetime  # 更新时间
            }
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 404: 用户不存在
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        admin_service = AdminService()
        updated_user = await admin_service.update_user_password(
            user_id,
            password_update.new_password,
            str(current_admin.id)
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or could not be updated"
            )
            
        return ResponseModel(
            code=200,
            msg="User password updated successfully",
            data=updated_user
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/users/{user_id}/points/increase", response_model=ResponseModel)
async def increase_user_points(
    user_id: str,
    points_update: IncreasePointsRequest,
    current_admin = Depends(get_current_admin)
):
    """增加用户积分
    
    Args:
        user_id (str): 要增加积分的用户ID
        points_update (IncreasePointsRequest): {
            "points": int,  # 要增加的积分数量
            "reason": str   # 增加积分的原因
        }
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "User points increased successfully",
            "data": {
                "id": str,  # 用户ID
                "username": str,  # 用户名
                "points": int,  # 更新后的总积分
                "updated_at": datetime  # 更新时间
            }
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 404: 用户不存在
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        admin_service = AdminService()
        updated_user = await admin_service.increase_user_points(
            user_id,
            points_update.points,
            str(current_admin.id),
            points_update.reason
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or could not be updated"
            )
            
        return ResponseModel(
            code=200,
            msg="User points increased successfully",
            data=updated_user
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
