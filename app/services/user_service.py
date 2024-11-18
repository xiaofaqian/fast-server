from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.db.mongodb import get_database
from app.models.user import UserInDB, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        try:
            user = await self.users_collection.find_one({"username": username})
            if not user:
                return None
            if not self.verify_password(password, user["hashed_password"]):
                return None
            
            # 更新用户活跃状态
            now = datetime.utcnow()
            await self.users_collection.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "is_active": True,
                        "last_active": now,
                        "updated_at": now
                    }
                }
            )
            user.update({
                "is_active": True,
                "last_active": now,
                "updated_at": now
            })
            
            return UserInDB(**user)
        except Exception as e:
            print(f"Authentication error: {e}")
            return None

    async def create_user(self, username: str, password: str) -> UserInDB:
        try:
            # 检查用户名是否已存在
            if await self.users_collection.find_one({"username": username}):
                raise ValueError("Username already registered")
            
            now = datetime.utcnow()
            user_dict = {
                "_id": ObjectId(),
                "username": username,
                "hashed_password": self.get_password_hash(password),
                "points": 0,
                "is_active": True,
                "is_superuser": False,
                "created_at": now,
                "updated_at": now,
                "last_active": now
            }
            print(user_dict)
            result = await self.users_collection.insert_one(user_dict)
            if not result.inserted_id:
                print("Failed to create user")
                raise Exception("Failed to create user")
            user_dict = await self.users_collection.find_one({"_id": result.inserted_id})    
            return user_dict
        except ValueError as e:
            raise e
        except Exception as e:
            print(f"Error creating user: {e}")
            raise Exception(f"Error creating user: {str(e)}")


    async def get_current_user(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            if user_id is None:
                return None
                
            # 获取用户数据并更新活跃状态
            now = datetime.utcnow()
            user_data = await self.users_collection.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_active": True,
                        "last_active": now,
                        "updated_at": now
                    }
                },
                return_document=True
            )
            
            if user_data is None:
                return None
                
            return User(
                id=user_data["_id"],
                username=user_data["username"],
                points=user_data.get("points", 0),
                is_active=user_data.get("is_active", True),
                is_superuser=user_data.get("is_superuser", False),
                is_admin=user_data.get("is_admin", False),
                created_at=user_data.get("created_at", datetime.utcnow()),
                updated_at=user_data.get("updated_at", datetime.utcnow()),
                last_active=user_data.get("last_active", datetime.utcnow()),
                current_total_up_points = user_data.get("current_total_up_points", 0),
                current_total_down_points = user_data.get("current_total_down_points", 0),
            )
        except JWTError:
            return None

    async def update_inactive_users(self):
        """更新不活跃用户状态"""
        try:
            now = datetime.utcnow()
            # 计算不活跃时间阈值（24小时）
            inactive_threshold = now - timedelta(hours=24)
            
            # 更新超过24小时未活跃的用户状态
            result = await self.users_collection.update_many(
                {
                    "last_active": {"$lt": inactive_threshold},
                    "is_active": True,
                    "is_admin": {"$ne": True},  # 排除管理员
                    "is_superuser": {"$ne": True}  # 排除超级用户
                },
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": now
                    }
                }
            )
            
            return result.modified_count
        except Exception as e:
            print(f"Error updating inactive users: {e}")
            return 0

    async def update_user_active_status(self, user_id: str):
        """手动更新用户活跃状态"""
        try:
            now = datetime.utcnow()
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_active": True,
                        "last_active": now,
                        "updated_at": now
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user active status: {e}")
            return False

    async def clearRecord(current_user: User):
        try:
            db = get_database()
            result = await db.users.update_one(
                {"username": current_user.username},
                {
                    "$set": {
                        'current_total_up_points':0,
                        'current_total_down_points':0
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error clearing user record: {e}")
            return False