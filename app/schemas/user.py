from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class UserBase(BaseModel):
    username: str
    
class UserCreate(UserBase):
    password: str
    
class UserLogin(BaseModel):
    username: str
    password: str
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    points: Optional[int] = None
    
class UserResponseData(BaseModel):
    _id: str
    username: str
    hashed_password: Optional[str] = None  # 添加密码字段，设为可选
    points: int
    is_active: bool
    is_superuser: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

class UserResponse(BaseModel):
    code: int
    msg: str
    data: UserResponseData

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
class TokenPayload(BaseModel):
    sub: str = None

class TokenData(BaseModel):
    access_token: str
    token_type: str

class LoginResponse(BaseModel):
    code: int
    msg: str
    data: TokenData

class RegisterResponse(BaseModel):
    code: int
    msg: str
    data: UserResponseData

class PointsResponse(BaseModel):
    points:int
