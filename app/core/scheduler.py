from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.user_service import UserService

async def update_inactive_users_job():
    """定时任务：更新不活跃用户状态"""
    user_service = UserService()
    updated_count = await user_service.update_inactive_users()
    print(f"Updated {updated_count} inactive users")

def start_scheduler():
    """启动定时任务调度器"""
    scheduler = AsyncIOScheduler()
    
    # 添加更新不活跃用户状态的任务，每小时执行一次
    scheduler.add_job(update_inactive_users_job, 'interval', hours=1)
    
    # 启动调度器
    scheduler.start()
    print("Scheduler started...")
