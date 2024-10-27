from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class AdminLog(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    admin_id: str
    action: str
    target_id: Optional[str] = None
    details: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PointsLog(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()))
    admin_id: str
    user_id: str
    username: str
    points_change: int
    points_after: int
    reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
