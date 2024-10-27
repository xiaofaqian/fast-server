from pydantic import BaseModel

class AdminLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str

class UpdatePasswordRequest(BaseModel):
    new_password: str

class IncreasePointsRequest(BaseModel):
    points: int
    reason: str = None

class CreateAdminRequest(BaseModel):
    username: str
    password: str
