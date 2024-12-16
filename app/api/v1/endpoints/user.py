from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse, Token, LoginResponse, RegisterResponse, UserResponseData, PointsResponse
from app.services.user_service import UserService
from app.models.response import ResponseModel
from pydantic import BaseModel
from app.services.auth_service import get_current_user
from app.models.user import User, UserInDB

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/register", response_model=ResponseModel, status_code=status.HTTP_200_OK)
async def register(user_data: UserCreate):
    """用户注册接口
    
    Args:
        user_data (UserCreate): {
            "username": str,  # 用户名
            "password": str   # 密码
        }

    Raises:
        HTTPException 400: 注册参数无效
        HTTPException 500: 服务器内部错误
    """
    try:
        user_service = UserService()
        user = await user_service.create_user(
            username=user_data.username,
            password=user_data.password
        )
        return ResponseModel(
            code=200,
            msg="User registered successfully",
            data=None
        )
    except Exception as e:
        return ResponseModel(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            msg=str(e)
        )

@router.post("/login", response_model=LoginResponse)
async def login(form_data: UserCreate):
    """用户登录接口
    
    Args:
        form_data (UserCreate): {
            "username": str,  # 用户名
            "password": str   # 密码
        }
    
    Returns:
        LoginResponse: {
            "code": 200,
            "msg": "Login successful",
            "data": {
                "access_token": str,  # JWT访问令牌
                "token_type": str  # 令牌类型
            }
        }
    
    Raises:
        HTTPException 401: 用户名或密码错误
        HTTPException 500: 服务器内部错误
    """
    try:
        user_service = UserService()
        user = await user_service.authenticate_user(form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = user_service.create_access_token(data={"sub": str(user.id)})
        return LoginResponse(
            code=200,
            msg="Login successful",
            data={"access_token": access_token, "token_type": "bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息
    
    Args:
        current_user (User): 当前登录用户信息，由 OAuth2 认证提供
    
    Returns:
        UserResponse: {
            "code": 200,
            "msg": "Success",
            "data": {
                "_id": str,  # 用户ID
                "username": str,  # 用户名
                "points": int,  # 积分
                "is_active": bool,  # 是否激活
                "is_superuser": bool,  # 是否超级用户
                "is_admin": bool,  # 是否管理员
                "created_at": datetime,  # 创建时间
                "updated_at": datetime  # 更新时间
            }
        }
    
    Raises:
        HTTPException 500: 服务器内部错误
    """
    try:
        return UserResponse(
            code=200,
            msg="Success",
            data=UserResponseData(
                _id=str(current_user.id),
                username=current_user.username,
                points=current_user.points,
                is_active=current_user.is_active,
                is_superuser=current_user.is_superuser,
                is_admin=current_user.is_admin,
                created_at=current_user.created_at,
                updated_at=current_user.updated_at,
                current_total_up_points = current_user.current_total_up_points,
                current_total_down_points = current_user.current_total_down_points
            )
        )
    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/points", response_model=ResponseModel)
async def get_user_points(current_user: User = Depends(get_current_user)):
    """获取当前用户积分
    
    Args:
        current_user (User): 当前登录用户信息，由 OAuth2 认证提供
    
    Returns:
        ResponseModel: {
            "code": 200,
            "msg": "Success",
            "data": {
                "points": int  # 用户当前积分
            }
        }
    
    Raises:
        HTTPException 500: 服务器内部错误
    """
    try:
        return ResponseModel(
            code=200,
            msg="Success",
            data=PointsResponse(points=current_user.points)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/clearRecord")
async def clearRecord(
    current_user: User = Depends(get_current_user)
):
    """
    清除用户当前统计
    """
    try:
        result = await UserService.clearRecord(current_user)
        if result:
            return ResponseModel(
                    code=200,
                    msg="Success",
                )
        else:
            raise HTTPException(status_code=400, detail="重设记录失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))    