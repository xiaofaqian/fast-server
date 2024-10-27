from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    
async def connect_to_mongo():
    try:
        MongoDB.client = AsyncIOMotorClient(settings.MONGODB_URL)
        print("Connected to MongoDB.")
    except Exception as e:
        print(f"Could not connect to MongoDB: {e}")
    
async def close_mongo_connection():
    if MongoDB.client:
        MongoDB.client.close()
        print("Closed MongoDB connection.")
        
def get_database():
    if not MongoDB.client:
        raise Exception("MongoDB connection not established")
    return MongoDB.client[settings.MONGODB_DATABASE]
