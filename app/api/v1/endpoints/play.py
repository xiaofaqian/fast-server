from fastapi import APIRouter,Depends
from app.models.response import ResponseModel
from app.models.play import PredictPutCardModel
from app.utils.utils import get_landlord_score
from app.utils.pklord_ai import PklordAI, PklordLocal
from app.core.scheduler import request_queue, request_results
from app.services.auth_service import get_current_user
from app.models.user import User, UserInDB

import uuid
router = APIRouter()



@router.get("/play/pklord/getLandlordScore", response_model=ResponseModel)
async def getLandlordScore(current_hand: str, pk_status: int, oppo_call: int, current_user: User = Depends(get_current_user)):
    score = get_landlord_score(current_hand)
    
    if oppo_call > 0:
        score = 0
    if pk_status == 0 and pk_status == 1:
        score = 9999
    print(f"叫牌分数: {score}")   
    return ResponseModel(code=200, msg="success", data=score)

# ,current_user: User = Depends(get_current_user)
@router.post("/play/pklord/predictPutCard", response_model=ResponseModel)
async def predictPutCard(data: PredictPutCardModel):
    try:
        # 生成唯一的请求ID
        request_id = str(uuid.uuid4())
        
        print(f"request.pk_status: {data.pk_status}")
        
        if data.pk_status != 2:
            playable = PklordLocal.play_cards(data)
            request_results[request_id] = {
                "code": 200, 
                "msg": "success", 
                "data": playable
            }
        else:    
            # 将请求放入队列
            await request_queue.put((request_id, data))
        
        # 返回请求ID，客户端可以用这个ID查询结果
        return ResponseModel(code=200, msg="请求已加入处理队列", data=request_id)
    except Exception as e:
        print(f"发生异常: {e}")
        return ResponseModel(code=500, msg="请求处理失败", data=None)

@router.get("/play/pklord/getRequestResult")
async def getRequestResult(request_id: str):
    # 检查请求结果是否存在
    result = request_results.get(request_id)
    
    if result:
        # 如果结果存在，删除结果（每个结果只能获取一次）
        del request_results[request_id]
        return result
    else:
        return {
            "code": 404, 
            "msg": "请求结果不存在或已被获取", 
            "data": None
        }
