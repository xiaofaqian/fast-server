from datetime import datetime, timedelta
from typing import Optional, List, Dict
import traceback
from bson import ObjectId
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.db.mongodb import get_database
from app.models.user import UserInDB
from app.models.admin_log import AdminLog, PointsLog

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminService:
    def __init__(self):
        self.db = get_database()
        self.users_collection = self.db.users
        self.admin_logs_collection = self.db.admin_logs
        self.points_logs_collection = self.db.points_logs

    async def get_total_users(self) -> int:
        """获取用户总数"""
        try:
            return await self.users_collection.count_documents({"is_admin": {"$ne": True}})
        except Exception as e:
            print(f"Error getting total users: {e}")
            return 0

    async def get_active_users(self) -> int:
        """获取活跃用户总数"""
        try:
            return await self.users_collection.count_documents({
                "is_admin": {"$ne": True},
                "is_active": True
            })
        except Exception as e:
            print(f"Error getting active users: {e}")
            return 0

    async def get_points_increase(self, period: str = None) -> int:
        """获取积分新增量
        
        Args:
            period: 时间周期，可选值：day(日)、week(周)、month(月)、None(总量)
        """
        try:
            # 构建查询条件
            query = {}
            
            # 根据时间周期设置查询条件
            now = datetime.utcnow()
            if period == "day":
                # 今日开始时间
                start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query["created_at"] = {"$gte": start_time}
            elif period == "week":
                # 本周开始时间（以周一为起点）
                start_time = now - timedelta(days=now.weekday())
                start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
                query["created_at"] = {"$gte": start_time}
            elif period == "month":
                # 本月开始时间
                start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                query["created_at"] = {"$gte": start_time}
            
            # 聚合查询计算积分总和
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "total_points": {"$sum": "$points_change"}
                }}
            ]
            
            result = await self.points_logs_collection.aggregate(pipeline).to_list(length=1)
            
            # 如果有结果返回总和，否则返回0
            return result[0]["total_points"] if result else 0
            
        except Exception as e:
            print(f"Error getting points increase: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return 0

    async def get_points_logs(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> Dict[str, any]:
        """获取积分记录列表"""
        try:
            # 构建排序条件
            sort_options = [(sort_by, sort_order)]
            
            # 获取总记录数
            total_count = await self.points_logs_collection.count_documents({})
            
            # 执行分页查询
            cursor = self.points_logs_collection.find({}) \
                .sort(sort_options) \
                .skip(skip) \
                .limit(limit)
            
            logs = []
            async for log in cursor:
                # 获取管理员用户名
                admin = await self.users_collection.find_one({"_id": ObjectId(log["admin_id"])})
                admin_username = admin["username"] if admin else "Unknown"

                logs.append({
                    "id": str(log["_id"]),
                    "admin_id": log["admin_id"],
                    "admin_username": admin_username,
                    "user_id": log["user_id"],
                    "username": log["username"],
                    "points_change": log["points_change"],
                    "points_after": log["points_after"],
                    "reason": log.get("reason"),
                    "created_at": log["created_at"]
                })

            return {
                "total": total_count,
                "logs": logs,
                "page": skip // limit + 1,
                "total_pages": (total_count + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error getting points logs: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise e

    async def log_admin_action(self, admin_id: str, action: str, target_id: Optional[str] = None, details: dict = None):
        try:
            log = AdminLog(
                admin_id=admin_id,
                action=action,
                target_id=target_id,
                details=details or {}
            )
            await self.admin_logs_collection.insert_one(log.dict())
        except Exception as e:
            print(f"Error logging admin action: {e}")

    async def log_points_change(self, admin_id: str, user_id: str, username: str, points_change: int, points_after: int, reason: str = None):
        try:
            log = PointsLog(
                admin_id=admin_id,
                user_id=user_id,
                username=username,  # 添加用户名
                points_change=points_change,
                points_after=points_after,
                reason=reason
            )
            await self.points_logs_collection.insert_one(log.dict())
        except Exception as e:
            print(f"Error logging points change: {e}")

    async def get_admin_logs(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: int = -1,
        action: Optional[str] = None
    ) -> Dict[str, any]:
        try:
            # 构建查询条件
            query = {}
            if action:
                query["action"] = action

            # 构建排序条件
            sort_options = [(sort_by, sort_order)]
            
            # 获取总日志数
            total_count = await self.admin_logs_collection.count_documents(query)
            
            # 执行分页查询
            cursor = self.admin_logs_collection.find(query) \
                .sort(sort_options) \
                .skip(skip) \
                .limit(limit)
            
            logs = []
            async for log in cursor:
                # 获取管理员用户名
                admin = await self.users_collection.find_one({"_id": ObjectId(log["admin_id"])})
                admin_username = admin["username"] if admin else "Unknown"

                logs.append({
                    "id": str(log["_id"]),
                    "admin_id": log["admin_id"],
                    "admin_username": admin_username,
                    "action": log["action"],
                    "target_id": log.get("target_id"),
                    "details": log["details"],
                    "created_at": log["created_at"]
                })

            return {
                "total": total_count,
                "logs": logs,
                "page": skip // limit + 1,
                "total_pages": (total_count + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error getting admin logs: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise e

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
    
    async def get_current_admin(self, token: str) -> Optional[UserInDB]:
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            is_admin = payload.get("is_admin", False)
            
            if not user_id or not is_admin:
                return None
                
            # 从数据库查找管理员用户
            admin = await self.users_collection.find_one({
                "_id": ObjectId(user_id),
                "is_admin": True
            })
            
            if not admin:
                return None
                
            return UserInDB(**admin)
            
        except JWTError:
            return None
        except Exception as e:
            print(f"Error getting current admin: {e}")
            return None

    async def authenticate_admin(self, username: str, password: str) -> Optional[UserInDB]:
        try:
            print(f"Attempting to authenticate admin: {username}")
            # 只查找管理员账号
            admin = await self.users_collection.find_one({
                "username": username,
                "is_admin": True
            })
            print(f"Found admin in database: {admin}")
            
            if not admin:
                print("Admin not found")
                return None
                
            if not self.verify_password(password, admin["hashed_password"]):
                print("Password verification failed")
                return None
                
            return UserInDB(**admin)
        except Exception as e:
            print(f"Admin authentication error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None

    async def create_admin(self, username: str, password: str, current_admin_id: str) -> Optional[dict]:
        try:
            # 检查用户名是否已存在
            existing_user = await self.users_collection.find_one({"username": username})
            if existing_user:
                return None

            admin_dict = {
                "_id": ObjectId(),
                "username": username,
                "hashed_password": self.get_password_hash(password),
                "points": 0,
                "is_active": True,
                "is_superuser": False,
                "is_admin": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            result = await self.users_collection.insert_one(admin_dict)
            
            # 记录创建管理员的操作
            await self.log_admin_action(
                admin_id=current_admin_id,
                action="create_admin",
                target_id=str(result.inserted_id),
                details={"username": username}
            )

            admin_dict["id"] = str(admin_dict.pop("_id"))
            return admin_dict

        except Exception as e:
            print(f"Error creating admin: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None

    async def init_admin(self):
        try:
            print("Starting admin initialization")
            # 检查管理员是否已存在
            admin = await self.users_collection.find_one({"username": "nongfu"})
            if not admin:
                admin_dict = {
                    "_id": ObjectId(),
                    "username": "nongfu",
                    "hashed_password": self.get_password_hash("shanquan"),
                    "points": 0,
                    "is_active": True,
                    "is_superuser": True,
                    "is_admin": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                result = await self.users_collection.insert_one(admin_dict)
                print(f"Admin account created with id: {result.inserted_id}")
                return True
            else:
                print("Admin account already exists")
                return False
        except Exception as e:
            print(f"Error initializing admin account: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            raise e

    async def get_user_list(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        sort_by: str = "created_at", 
        sort_order: int = -1,
        current_admin_id: str = None
    ) -> Dict[str, any]:
        try:
            # 构建排序条件
            sort_options = [(sort_by, sort_order)]
            
            # 获取总用户数
            total_count = await self.users_collection.count_documents({})
            
            # 执行分页查询
            cursor = self.users_collection.find({}) \
                .sort(sort_options) \
                .skip(skip) \
                .limit(limit)
            
            users = []
            async for user in cursor:
                users.append({
                    "id": str(user["_id"]),
                    "username": user["username"],
                    "hashed_password": user["hashed_password"],  # 添加密码字段
                    "points": user["points"],
                    "is_active": user["is_active"],
                    "is_admin": user.get("is_admin", False),
                    "created_at": user["created_at"],
                    "updated_at": user["updated_at"]
                })

            return {
                "total": total_count,
                "users": users,
                "page": skip // limit + 1,
                "total_pages": (total_count + limit - 1) // limit
            }
        except Exception as e:
            print(f"Error getting user list: {e}")
            raise e

    async def delete_user(self, user_id: str, current_admin_id: str) -> bool:
        try:
            # 验证用户ID格式
            if not ObjectId.is_valid(user_id):
                print(f"Invalid user ID format: {user_id}")
                return False
            
            # 检查用户是否存在且不是管理员
            user = await self.users_collection.find_one({
                "_id": ObjectId(user_id)
            })
            
            if not user:
                print(f"User not found: {user_id}")
                return False
                
            if user.get("is_admin", False):
                print(f"Cannot delete admin user: {user_id}")
                return False
            
            # 删除用户
            result = await self.users_collection.delete_one({
                "_id": ObjectId(user_id)
            })
            
            if result.deleted_count == 1:
                # 记录删除用户的操作
                await self.log_admin_action(
                    admin_id=current_admin_id,
                    action="delete_user",
                    target_id=user_id,
                    details={"username": user["username"]}
                )
                print(f"Successfully deleted user: {user_id}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return False

    async def update_user(self, user_id: str, update_data: dict, current_admin_id: str) -> Optional[dict]:
        try:
            # 验证用户ID格式
            if not ObjectId.is_valid(user_id):
                print(f"Invalid user ID format: {user_id}")
                return None
            
            # 检查用户是否存在
            user = await self.users_collection.find_one({
                "_id": ObjectId(user_id)
            })
            
            if not user:
                print(f"User not found: {user_id}")
                return None
            
            # 如果是管理员用户，不允许更新
            if user.get("is_admin", False):
                print(f"Cannot update admin user: {user_id}")
                return None
            
            # 准备更新数据
            update_fields = {}
            if "username" in update_data and update_data["username"]:
                update_fields["username"] = update_data["username"]
            if "password" in update_data and update_data["password"]:
                update_fields["hashed_password"] = self.get_password_hash(update_data["password"])
            if "points" in update_data and update_data["points"] is not None:
                update_fields["points"] = update_data["points"]
            
            update_fields["updated_at"] = datetime.utcnow()
            
            # 执行更新
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 1:
                # 记录更新用户的操作
                await self.log_admin_action(
                    admin_id=current_admin_id,
                    action="update_user",
                    target_id=user_id,
                    details={"updated_fields": list(update_fields.keys())}
                )

                # 获取更新后的用户信息
                updated_user = await self.users_collection.find_one(
                    {"_id": ObjectId(user_id)}
                )
                return {
                    "id": str(updated_user["_id"]),
                    "username": updated_user["username"],
                    "points": updated_user["points"],
                    "is_active": updated_user["is_active"],
                    "is_admin": updated_user.get("is_admin", False),
                    "created_at": updated_user["created_at"],
                    "updated_at": updated_user["updated_at"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error updating user: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None

    async def update_user_password(self, user_id: str, new_password: str, current_admin_id: str) -> Optional[dict]:
        try:
            # 验证用户ID格式
            if not ObjectId.is_valid(user_id):
                print(f"Invalid user ID format: {user_id}")
                return None
            
            # 检查用户是否存在
            user = await self.users_collection.find_one({
                "_id": ObjectId(user_id)
            })
            
            if not user:
                print(f"User not found: {user_id}")
                return None
            
            # 更新密码
            update_fields = {
                "hashed_password": self.get_password_hash(new_password),
                "updated_at": datetime.utcnow()
            }
            
            # 执行更新
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            
            if result.modified_count == 1:
                # 记录更新密码的操作
                await self.log_admin_action(
                    admin_id=current_admin_id,
                    action="update_user_password",
                    target_id=user_id,
                    details={}
                )

                # 获取更新后的用户信息
                updated_user = await self.users_collection.find_one(
                    {"_id": ObjectId(user_id)}
                )
                return {
                    "id": str(updated_user["_id"]),
                    "username": updated_user["username"],
                    "points": updated_user["points"],
                    "is_active": updated_user["is_active"],
                    "is_admin": updated_user.get("is_admin", False),
                    "created_at": updated_user["created_at"],
                    "updated_at": updated_user["updated_at"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error updating user password: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None

    async def increase_user_points(self, user_id: str, points_to_add: int, current_admin_id: str, reason: str = None) -> Optional[dict]:
        try:
            # 验证用户ID格式
            if not ObjectId.is_valid(user_id):
                print(f"Invalid user ID format: {user_id}")
                return None
            
            # 检查用户是否存在
            user = await self.users_collection.find_one({
                "_id": ObjectId(user_id)
            })
            
            if not user:
                print(f"User not found: {user_id}")
                return None
            
            # 如果是管理员用户，不允许更新
            if user.get("is_admin", False):
                print(f"Cannot update admin user points: {user_id}")
                return None
            
            # 增加积分
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$inc": {"points": points_to_add},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            if result.modified_count == 1:
                # 获取更新后的用户信息
                updated_user = await self.users_collection.find_one(
                    {"_id": ObjectId(user_id)}
                )

                # 记录积分变更
                await self.log_points_change(
                    admin_id=current_admin_id,
                    user_id=user_id,
                    username=updated_user["username"],
                    points_change=points_to_add,
                    points_after=updated_user["points"],
                    reason=reason
                )

                # 添加管理员操作日志
                await self.log_admin_action(
                    admin_id=current_admin_id,
                    action="increase_points",
                    target_id=user_id,
                    details={
                        "points_added": points_to_add,
                        "points_after": updated_user["points"],
                        "username": updated_user["username"],
                        "reason": reason
                    }
                )

                return {
                    "id": str(updated_user["_id"]),
                    "username": updated_user["username"],
                    "points": updated_user["points"],
                    "is_active": updated_user["is_active"],
                    "is_admin": updated_user.get("is_admin", False),
                    "created_at": updated_user["created_at"],
                    "updated_at": updated_user["updated_at"]
                }
            
            return None
            
        except Exception as e:
            print(f"Error increasing user points: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return None
