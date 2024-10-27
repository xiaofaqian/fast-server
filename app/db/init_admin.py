import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from app.core.config import settings
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_db():
    try:
        print("Connecting to MongoDB...")
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DATABASE]
        
        print("Checking if admin exists...")
        # 先删除已存在的管理员账号
        await db.users.delete_one({"username": "nongfu"})
        
        # 创建新的管理员账号
        admin_dict = {
            "_id": ObjectId(),
            "username": "nongfu",
            "hashed_password": pwd_context.hash("shanquan"),
            "points": 0,
            "is_active": True,
            "is_superuser": True,
            "is_admin": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        print("Creating new admin account...")
        result = await db.users.insert_one(admin_dict)
        print(f"Admin created with id: {result.inserted_id}")
            
    except Exception as e:
        print(f"Error in init_db: {e}")
    finally:
        print("Closing MongoDB connection...")
        client.close()

if __name__ == "__main__":
    print("Starting admin initialization script...")
    asyncio.run(init_db())
    print("Admin initialization completed.")
