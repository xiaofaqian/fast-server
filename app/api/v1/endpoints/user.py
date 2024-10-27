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

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_200_OK)
async def register(user_data: UserCreate):
    try:
        user_service = UserService()
        user = await user_service.create_user(
            username=user_data.username,
            password=user_data.password
        )
        return RegisterResponse(
            code=200,
            msg="User registered successfully",
            data={
                "_id": str(user.id),
                "username": user.username,
                "points": user.points,
                "is_active": user.is_active
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login", response_model=LoginResponse)
async def login(form_data: UserCreate):
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
                updated_at=current_user.updated_at
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
