from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services.admin_service import AdminService
from app.models.response import ResponseModel
from app.schemas.admin import Token, AdminLogin, UpdatePasswordRequest, IncreasePointsRequest, CreateAdminRequest
from app.schemas.user import UserUpdate
from typing import List, Optional
from app.services.auth_service import get_current_admin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

@router.post("/login", response_model=ResponseModel)
async def admin_login(login_data: AdminLogin):
    """管理员登录接口
    
    Args:
        login_data (AdminLogin): {
            "username": str,  # 管理员用户名
            "password": str   # 管理员密码
        }
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Login successful",
            "data": {
                "access_token": str  # JWT访问令牌
            }
        }
    
    Raises:
        HTTPException 401: 用户名或密码错误
        HTTPException 500: 服务器内部错误
    """
    try:
        admin_service = AdminService()
        admin = await admin_service.authenticate_admin(login_data.username, login_data.password)
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = admin_service.create_access_token(
            data={"sub": str(admin.id), "is_admin": True}
        )
        return ResponseModel(
            code=200,
            msg="Login successful",
            data=Token(access_token=access_token)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/create", response_model=ResponseModel)
async def create_admin(
    admin_data: CreateAdminRequest,
    current_admin = Depends(get_current_admin)
):
    """创建新管理员账号
    
    Args:
        admin_data (CreateAdminRequest): {
            "username": str,  # 新管理员用户名
            "password": str   # 新管理员密码
        }
        current_admin: 当前登录的管理员信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Admin created successfully",
            "data": {
                "id": str,  # 新管理员ID
                "username": str,  # 新管理员用户名
                "created_at": datetime  # 创建时间
            }
        }
    
    Raises:
        HTTPException 401: 未授权访问
        HTTPException 400: 用户名已存在
        HTTPException 500: 服务器内部错误
    """
    try:
        if not current_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )
        
        admin_service = AdminService()
        new_admin = await admin_service.create_admin(
            username=admin_data.username,
            password=admin_data.password,
            current_admin_id=str(current_admin.id)
        )
        
        if not new_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
            
        return ResponseModel(
            code=200,
            msg="Admin created successfully",
            data=new_admin
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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
