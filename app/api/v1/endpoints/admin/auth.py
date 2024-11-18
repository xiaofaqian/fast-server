from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.admin_service import AdminService
from app.models.response import ResponseModel
from app.schemas.admin import Token, AdminLogin, CreateAdminRequest
from app.services.auth_service import get_current_admin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
