from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any


class PyObjectId(ObjectId):
    """自定义 ObjectId 类型，用于 Pydantic 模型"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # 更新 JSON Schema 以显示为字符串类型
        field_schema = handler(core_schema)
        field_schema.update(type='string')
        return field_schema
    
class UserTaskID(BaseModel):
    task_id: str = Field(..., description='任务唯一标识符')
    
class UserTaskCreateSchema(BaseModel):
    username: str = Field(..., description='用户名')

class UserTaskEndSchema(BaseModel):
    username: str = Field(..., description='用户名')
    task_id: str = Field(..., description='任务唯一标识符')

class GameDetail(BaseModel):
    is_up: bool = Field(..., description='是否是上分')
    valid_match: bool = Field(..., description='对局详细信息')
    nickname: str = Field(..., description='昵称')
    oppo_nickname: str = Field(..., description='对手昵称')
    records: int = Field(..., description='战绩')

class UserPointDetailSchema(BaseModel):
    username: str = Field(..., description='用户名')
    task_id: str = Field(..., description='关联的任务ID')
    game_detail: GameDetail = Field(..., description='对局详细信息')
  
class BillQueryParams(BaseModel):
    start_time: Optional[int] = Field(None, description='开始时间（毫秒级时间戳）')
    end_time: Optional[int] = Field(None, description='结束时间（毫秒级时间戳）')
    min_consumed_points: Optional[int] = Field(None, description='最小消耗点数')
    max_consumed_points: Optional[int] = Field(None, description='最大消耗点数')
    min_down_points: Optional[int] = Field(None, description='最小下分点数')
    max_down_points: Optional[int] = Field(None, description='最大下分点数')
    page: Optional[int] = Field(1, description='页码')
    page_size: int = Field(10, description='每页条数')
    
class UserTaskDocument(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    username: str = Field(..., description='用户名')
    task_id: str = Field(..., description='任务唯一标识符')
    start_time: Optional[int] = Field(None, description='任务开始时间（毫秒级时间戳）')
    current_points: Optional[int] = Field(default=0, description='当前点数')
    consumed_points: Optional[int] = Field(default=0, description='总消耗点数')
    game_count: Optional[int] = Field(default=0, description='总对局数')
    total_up_points: Optional[int] = Field(default=0, description='总上分点数')
    total_down_points: Optional[int] = Field(default=0, description='总下分点数')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserPointDetailDocument(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    username: str = Field(..., description='用户名')
    timestamp: int = Field(description='记录时间戳（毫秒级）')
    game_detail: GameDetail = Field(..., description='对局详细信息')
    consumed_points: int = Field(default=0, description='本次消耗点数')
    task_id: str = Field(..., description='关联的任务ID')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        
class CurrentTaskDocument(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias='_id')
    username: str = Field(..., description='用户名')
    current_task_id: str = Field(..., description='任务唯一标识符')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
