import json
from fastapi import APIRouter,Depends
from app.models.response import ResponseModel
from app.models.play import PredictPutCardModel
from app.utils.utils import get_landlord_score
from app.utils.pklord_ai import PklordAI, PklordLocal
#from app.core.scheduler import request_queue, request_results
from app.services.auth_service import get_current_user
from app.models.user import User, UserInDB
from app.db.redis import get_redis
import uuid
router = APIRouter()

QUEUE_KEY = "pklord_request_queue"
RESULT_KEY = "pklord_results:"

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
async def predictPutCard(data: PredictPutCardModel, current_user: User = Depends(get_current_user)):
    try:
        redis_client = get_redis() 
        # 生成唯一的请求ID
        request_id = str(uuid.uuid4())
        print(f"request.pk_status: {data.pk_status}")
        
        if data.pk_status != 2:
            playable = PklordLocal.play_cards(data)
            # 将结果存储到Redis
            await redis_client.setex(
                request_id,
                600,
                json.dumps({
                    "code": 200,
                    "msg": "success",
                    "data": playable
                })
            )
        else:
            await redis_client.lpush(
                "REQ",
                json.dumps({
                    "request_id":request_id,
                    "data":data.dict()
                })
            )   
        
        # 返回请求ID，客户端可以用这个ID查询结果
        return ResponseModel(code=200, msg="请求已加入处理队列", data=request_id)
    except Exception as e:
        print(f"发生异常: {e}")
        return ResponseModel(code=500, msg="请求处理失败", data=None)

@router.get("/play/pklord/getRequestResult")
async def getRequestResult(request_id: str):

    redis_client = get_redis() 
    result = await redis_client.get(request_id)
    if result:
        result_dict = json.loads(result)
        await redis_client.delete(request_id)
        print(result_dict)
        return result_dict
    else:
        return {
            "code": 404, 
            "msg": "请求结果不存在或已被获取", 
            "data": None
        }
