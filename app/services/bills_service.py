from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from bson import ObjectId
from fastapi import logger
from app.db.mongodb import get_database
from app.schemas.bills import (
    CurrentTaskDocument, 
    UserTaskEndSchema, 
    UserPointDetailSchema, 
    BillQueryParams,
    UserTaskDocument,
    UserPointDetailDocument,
    PyObjectId
)
from app.models.user import User, UserInDB
from app.models.response import ResponseModel
from app.utils.utils import *
from app.services.admin_service import AdminService

class BillsService:
          
    @staticmethod
    async def create_user_task(user: User):
        """
        创建新的用户任务
        """
        db = get_database()
        
        # 生成新的任务ID
        task_id = await generate_unique_task_id(db)

        # 先检查是否有未完成的任务
        current_tasks = await db.current_task.find({"username": user.username}).to_list(length=None)
        for current_task in current_tasks:
            # 如果存在未完成任务，先结束之前的任务
            if current_task and current_task.get("current_task_id"):
                await BillsService.end_user_task(user.username, current_task.get("current_task_id"))

        # 创建新的任务文档
        task_document = UserTaskDocument(
            username=user.username,
            task_id=task_id,
            start_time=get_current_timestamp(),
            current_points=user.points
        )

        # 创建当前任务记录
        current_task_document = CurrentTaskDocument(
            username=user.username,
            current_task_id=task_id,
        )

        # 插入当前任务和用户任务记录
        await db.current_task.insert_one(current_task_document.dict(by_alias=True))
        result = await db.user_tasks.insert_one(task_document.dict(by_alias=True))
        inserted_id = result.inserted_id  
        inserted_document = await db.user_tasks.find_one({"_id": inserted_id})
        return inserted_document
        

    @staticmethod
    async def end_user_task(username: str, current_task_id: str):
        """
        结束用户任务并更新统计信息
        """
        db = get_database()
        
        # 如果结束的任务是当前任务，则先清空当前任务
        current_task = await db.current_task.find_one({"username": username,"current_task_id":current_task_id})
  
        if current_task:
            await db.current_task.delete_one({"username": username,"current_task_id":current_task_id})
    
        #  获取任务相关详情      
        task_point_details = await db.point_details.find({"task_id": current_task_id}).to_list(length=None)
        user = await db.users.find_one({"username": username})
        # 在数据库查找任务
        user_task = await db.user_tasks.find_one({"username": username, "task_id": current_task_id})
        if not user_task:
            new_task_id = await generate_unique_task_id(db)
            task_document = UserTaskDocument(
            username=user.get("username",""),
            task_id=new_task_id,
            start_time= get_current_timestamp(),
            current_points=user.get("points","")
            )
            result = await db.user_tasks.insert_one(task_document.dict(by_alias=True)) 
            inserted_id = result.inserted_id  
            user_task = await db.user_tasks.find_one({"_id": inserted_id})
            

        current_points=user.get("points",0)
        consumed_points=0
        game_count = 0
        total_up_points= 0
        total_down_points= 0
        
        #  统计任务数据
        for task_point_detail in task_point_details:
            game_count += 1
            game_detail = task_point_detail.get("game_detail",{})
            if game_detail.get("is_up",False):
                total_up_points += game_detail.get("records",0)
            else:
                total_down_points += game_detail.get("records",0)   
            consumed_points += task_point_detail.get("consumed_points",0)

        #  更新任务数据库
        user_task_data = {
            'username':username,
            'task_id':current_task_id,
            'current_points':current_points,
            'consumed_points':consumed_points,
            'game_count':game_count,
            'total_up_points':total_up_points,
            'total_down_points':total_down_points
        }
        await db.user_tasks.update_one({"_id": user_task["_id"]},{"$set": user_task_data})
        result = await db.user_tasks.find_one({"task_id": current_task_id})
        
        if total_up_points==0 and total_down_points==0:
            await db.user_tasks.delete_one({"_id": user_task["_id"]})  
            
        return result
        
        


    @staticmethod
    async def upload_point_detail(user: User, point_detail: UserPointDetailSchema) -> UserPointDetailDocument:
        """
        上传用户点数使用明细
        """
        db = get_database()
        
        # 验证关联的任务是否存在且未结束
        task = await db.user_tasks.find_one({
            "username": user.username, 
            "task_id": point_detail.task_id,
        })
        
        if not task:
            raise ValueError("没有任务id，请重新启动任务")
        
        # 计算消耗的点数
        consumed_points = 0 if point_detail.game_detail.is_up else point_detail.game_detail.records

        try:
            # 变更用户点数
            change_points_result = await BillsService.change_user_points(user, point_detail)
            
            if not change_points_result:
                raise Exception("Failed to change user points")

            point_detail_document = UserPointDetailDocument(
                username=user.username,
                timestamp=get_current_timestamp(),
                game_detail=point_detail.game_detail,
                consumed_points=consumed_points,
                task_id=point_detail.task_id
            )
            
            # 插入点数明细
            result = await db.point_details.insert_one(point_detail_document.dict(by_alias=True))

            return point_detail_document

        except Exception as e:
            logger.error(f"Error in upload_point_detail: {str(e)}")
            raise

    @staticmethod
    async def change_user_points(user: User, point_detail: UserPointDetailSchema):
        """
        变更用户点数
        """
        db = get_database()
        
        # 验证用户ID格式
        if not ObjectId.is_valid(user.id):
            logger.error(f"Invalid user ID format: {user.id}")
            return None
        
        # 查询用户最新信息
        user_document = await db.users.find_one({
            "_id": ObjectId(user.id)
        })
        
        if not user_document:
            logger.error(f"User not found: {user.id}")
            return None

        points_to_add = point_detail.game_detail.records
        
        try:
            # 根据游戏类型更新点数
            if point_detail.game_detail.is_up:   
                total_up_points = points_to_add
                total_down_points = 0
                points = 0
            else:
                total_up_points = 0
                total_down_points = points_to_add
                points = points_to_add
            
            # 更新用户总点数
            result = await db.users.update_one(
                {"_id": ObjectId(user.id)},
                {
                    "$inc": {
                        "points": points,
                        "current_total_up_points": total_up_points,
                        "current_total_down_points": total_down_points
                    }
                }
            )
            user = await db.users.find_one({"_id": ObjectId(user.id)})
            return user

        except Exception as e:
            logger.error(f"Error in change_user_points: {str(e)}")
            return None
    
    @staticmethod
    async def get_bill_pages(user: User, query_params: BillQueryParams) -> Dict[str, int]:
        """
        获取账单总页数
        """
        db = get_database()
        
        # 构建查询条件
        query = {"username": user.username}
        
        if query_params.start_time:
            query["start_time"] = {"$gte": query_params.start_time}
        if query_params.end_time:
            query["end_time"] = {"$lte": query_params.end_time}
        if query_params.min_consumed_points is not None:
            query["consumed_points"] = {"$gte": query_params.min_consumed_points}
        if query_params.max_consumed_points is not None:
            query["consumed_points"] = query.get("consumed_points", {})
            query["consumed_points"]["$lte"] = query_params.max_consumed_points
        if query_params.min_down_points is not None:
            query["total_down_points"] = {"$gte": query_params.min_down_points}
        if query_params.max_down_points is not None:
            query["total_down_points"] = query.get("total_down_points", {})
            query["total_down_points"]["$lte"] = query_params.max_down_points
        
        total_tasks = await db.user_tasks.count_documents(query)
        total_pages = (total_tasks + query_params.page_size - 1) // query_params.page_size
        
        return {"total_pages": total_pages, "total_tasks": total_tasks}

    @staticmethod
    async def get_bill_list(user: User, query_params: BillQueryParams) -> List[UserTaskDocument]:
        """
        获取账单列表
        """
        db = get_database()
        
        # 构建查询条件
        query = {"username": user.username}
        
        if query_params.start_time:
            query["start_time"] = {"$gte": query_params.start_time}
        if query_params.end_time:
            query["end_time"] = {"$lte": query_params.end_time}
        if query_params.min_consumed_points is not None:
            query["consumed_points"] = {"$gte": query_params.min_consumed_points}
        if query_params.max_consumed_points is not None:
            query["consumed_points"] = query.get("consumed_points", {})
            query["consumed_points"]["$lte"] = query_params.max_consumed_points
        if query_params.min_down_points is not None:
            query["total_down_points"] = {"$gte": query_params.min_down_points}
        if query_params.max_down_points is not None:
            query["total_down_points"] = query.get("total_down_points", {})
            query["total_down_points"]["$lte"] = query_params.max_down_points
        
        # 分页查询
        skip = (query_params.page - 1) * query_params.page_size
        # tasks = await db.user_tasks.find(query).skip(skip).limit(query_params.page_size).to_list(length=query_params.page_size)
        tasks = await db.user_tasks.find(query).sort("start_time", -1).skip(skip).limit(query_params.page_size).to_list(length=query_params.page_size)
        
        # 转换为 Pydantic 模型，确保正确处理 _id
        return [UserTaskDocument(
            id=task.get('_id'),
            username=task.get('username'),
            task_id=task.get('task_id'),
            start_time=task.get('start_time'),
            current_points=task.get('current_points'),
            consumed_points=task.get('consumed_points'),
            game_count=task.get('game_count'),
            total_up_points=task.get('total_up_points'),
            total_down_points=task.get('total_down_points')
        ) for task in tasks]
