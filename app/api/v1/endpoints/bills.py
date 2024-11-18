from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.services.auth_service import get_current_user
from app.services.bills_service import BillsService
from app.schemas.bills import (
    UserPointDetailSchema, 
    BillQueryParams,
    UserTaskID
)
from app.models.user import User, UserInDB
from app.models.response import ResponseModel

router = APIRouter()

@router.post("/task/start")
async def create_user_task(
    current_user: User = Depends(get_current_user)
):
    """
    创建新的用户任务
    """
    try:
        # 检查用户积分
        if current_user.points < 80000:
            raise HTTPException(status_code=400, detail="当前帐户分数低，请联系管理员")
        
        result = await BillsService.create_user_task(current_user)
        if result:
            return ResponseModel(
                    code=200,
                    msg="Success",
                    data= {
                        "task_id":result.get("task_id"),
                    }
                )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/task/end")
async def end_user_task(
    task_id: UserTaskID, 
    current_user: User = Depends(get_current_user)
):
    """
    结束用户任务并更新统计信息
    """
    try:
        result = await BillsService.end_user_task(current_user.username, task_id.task_id)
        if result:
            return ResponseModel(
                    code=200,
                    msg="Success",
                    data= None
                )
        else:
            raise HTTPException(status_code=400, detail="结束任务失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/point/detail")
async def upload_point_detail(
    point_detail: UserPointDetailSchema, 
    current_user: User = Depends(get_current_user)
):
    """
    上传用户点数使用明细
    """
    try:
        result = await BillsService.upload_point_detail(current_user, point_detail)
        if result:
            return ResponseModel(
                    code=200,
                    msg="Success",
                    data= None
                )
        else:
            raise HTTPException(status_code=400, detail="上传点数失败")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/pages")
async def get_bill_pages(
    query_params: BillQueryParams, 
    current_user: User = Depends(get_current_user)
):
    """
    获取账单总页数
    """
    try:
        page_info = await BillsService.get_bill_pages(current_user, query_params)
        print(page_info)
        if page_info:
            return ResponseModel(
                    code=200,
                    msg="Success",
                    data= page_info
                )
        else:
            raise HTTPException(status_code=400, detail="获取账单总页数失败")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/list")
async def get_bill_list(
    query_params: BillQueryParams, 
    current_user: User = Depends(get_current_user)
):
    """
    获取账单列表
    """
    try:
        bill_list = await BillsService.get_bill_list(current_user, query_params)
        # for bill in bill_list:
        #     print(bill)
        if bill_list:
            return ResponseModel(
                    code=200,
                    msg="Success",
                    data= bill_list
                )
        else:
            raise HTTPException(status_code=400, detail="获取账单总页数失败")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


