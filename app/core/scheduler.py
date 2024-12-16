import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.user_service import UserService
from app.models.play import PredictPutCardModel
from app.db.redis import get_redis
import asyncio

from app.utils.pklord_ai import PklordAI,PklordLocal


async def update_inactive_users_job():
    """定时任务：更新不活跃用户状态"""
    user_service = UserService()
    updated_count = await user_service.update_inactive_users()
    print(f"Updated {updated_count} inactive users")

# 后台任务：处理请求队列
async def process_request_queue():
    redis_client = get_redis()
    result = await redis_client.brpop("REQ", timeout=0)
    if not result:
        return
        
    _, value = result
    request_data = json.loads(value)
    request_id = request_data.get("request_id","")
    request = request_data.get("data","")
    #print(request)
    try:
        request = PredictPutCardModel.from_dict(request)
        playable = PklordAI.play_cards(request)
        
        await redis_client.setex(
            request_id,
            600,
            json.dumps({
                "code": 200,
                "msg": "success",
                "data": playable
            })
        )
    except Exception as e:
        print(f"处理请求异常: {e}")
        await redis_client.setex(
            request_id,
            600,
            json.dumps({
                "code": 500,
                "msg": "success",
                "data": None
            })
        )

def start_scheduler():
    """启动定时任务调度器"""
    scheduler = AsyncIOScheduler()
    
    # 添加更新不活跃用户状态的任务，每小时执行一次
    scheduler.add_job(update_inactive_users_job, 'interval', hours=1)
    #scheduler.add_job(process_request_queue, 'interval', seconds=0.3, max_instances=1, coalesce=True)
    # 启动调度器
    scheduler.start()
    print("Scheduler started...")

