from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.user_service import UserService
import asyncio

from app.utils.pklord_ai import PklordAI,PklordLocal

# 创建一个线程安全的队列，存储请求和对应的Future
request_queue = asyncio.Queue()

# 存储请求结果的字典
request_results = {}

async def update_inactive_users_job():
    """定时任务：更新不活跃用户状态"""
    user_service = UserService()
    updated_count = await user_service.update_inactive_users()
    print(f"Updated {updated_count} inactive users")

# 后台任务：处理请求队列
async def process_request_queue():
    # 从队列中获取请求，如果队列为空则等待
    request_id, request = await request_queue.get()
    try:
        print("使用接口")
        # 处理请求
        playable = PklordAI.play_cards(request)
            
        print(f"请求: {request}")
        print(f"AI出牌: {playable}")
        
        # 将结果存储在结果字典中
        request_results[request_id] = {
            "code": 200, 
            "msg": "success", 
            "data": playable
        }
    except Exception as e:
        print(f"处理请求时发生异常: {e}")
        request_results[request_id] = {
            "code": 500, 
            "msg": str(e), 
            "data": None
        }
    finally:
        # 标记任务完成
        request_queue.task_done()

def start_scheduler():
    """启动定时任务调度器"""
    scheduler = AsyncIOScheduler()
    
    # 添加更新不活跃用户状态的任务，每小时执行一次
    scheduler.add_job(update_inactive_users_job, 'interval', hours=1)
    scheduler.add_job(process_request_queue, 'interval', seconds=0.3, max_instances=1, coalesce=True)
    # 启动调度器
    scheduler.start()
    print("Scheduler started...")

