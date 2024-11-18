import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import asyncio

# 导入主应用和相关模块
from app.main import app
from app.db.mongodb import get_database
from app.services.auth_service import get_current_user
from app.schemas.bills import (
    UserTaskCreateSchema, 
    UserTaskEndSchema, 
    UserPointDetailSchema, 
    BillQueryParams
)

# 创建测试客户端
client = TestClient(app)

# 测试用户信息
TEST_USERNAME = "test_user"
TEST_TOKEN = "test_token"

# 模拟用户认证依赖
async def mock_get_current_user():
    return TEST_USERNAME

# 替换原始的用户认证依赖
app.dependency_overrides[get_current_user] = mock_get_current_user

# 清理测试数据的辅助函数
async def cleanup_test_data():
    db = get_database()
    await db.user_tasks.delete_many({"username": TEST_USERNAME})
    await db.point_details.delete_many({"username": TEST_USERNAME})

@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    asyncio.run(cleanup_test_data())

# 测试用例
@pytest.mark.asyncio
async def test_create_user_task():
    # 准备测试数据
    task_data = {
        "task_id": "test_task_001",
        "start_time": int(datetime.utcnow().timestamp() * 1000),
        "current_points": 100.0
    }

    # 发送创建任务请求
    response = client.post("/api/v1/bills/task/start", json=task_data)
    
    # 验证响应
    assert response.status_code == 200
    task_response = response.json()
    assert task_response["task_id"] == task_data["task_id"]
    assert task_response["current_points"] == task_data["current_points"]

@pytest.mark.asyncio
async def test_end_user_task():
    # 先创建一个任务
    task_data_start = {
        "task_id": "test_task_002",
        "start_time": int(datetime.utcnow().timestamp() * 1000),
        "current_points": 100.0
    }
    client.post("/api/v1/bills/task/start", json=task_data_start)

    # 准备结束任务数据
    task_data_end = {
        "task_id": "test_task_002",
        "end_time": int((datetime.utcnow() + timedelta(hours=1)).timestamp() * 1000),
        "consumed_points": 50.0,
        "game_count": 5,
        "total_up_points": 200.0,
        "total_down_points": 150.0
    }

    # 发送结束任务请求
    response = client.post("/api/v1/bills/task/end", json=task_data_end)
    
    # 验证响应
    assert response.status_code == 200
    task_response = response.json()
    assert task_response["task_id"] == task_data_end["task_id"]
    assert task_response["consumed_points"] == task_data_end["consumed_points"]

@pytest.mark.asyncio
async def test_upload_point_detail():
    # 先创建一个任务
    task_data_start = {
        "task_id": "test_task_003",
        "start_time": int(datetime.utcnow().timestamp() * 1000),
        "current_points": 100.0
    }
    client.post("/api/v1/bills/task/start", json=task_data_start)

    # 准备点数明细数据
    point_detail = {
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
        "game_detail": "测试对局",
        "consumed_points": 10.0,
        "task_id": "test_task_003"
    }

    # 发送上传点数明细请求
    response = client.post("/api/v1/bills/point/detail", json=point_detail)
    
    # 验证响应
    assert response.status_code == 200
    detail_response = response.json()
    assert detail_response["consumed_points"] == point_detail["consumed_points"]
    assert detail_response["game_detail"] == point_detail["game_detail"]

@pytest.mark.asyncio
async def test_get_bill_pages():
    # 先创建多个任务
    for i in range(15):
        task_data = {
            "task_id": f"test_task_page_{i}",
            "start_time": int(datetime.utcnow().timestamp() * 1000),
            "current_points": 100.0
        }
        client.post("/api/v1/bills/task/start", json=task_data)

    # 准备查询参数
    query_params = {
        "page": 1,
        "page_size": 10
    }

    # 发送获取账单页数请求
    response = client.post("/api/v1/bills/bill/pages", json=query_params)
    
    # 验证响应
    assert response.status_code == 200
    pages_response = response.json()
    assert pages_response["total_pages"] >= 2
    assert pages_response["total_tasks"] >= 15

@pytest.mark.asyncio
async def test_get_bill_list():
    # 准备查询参数
    query_params = {
        "page": 1,
        "page_size": 10
    }

    # 发送获取账单列表请求
    response = client.post("/api/v1/bills/bill/list", json=query_params)
    
    # 验证响应
    assert response.status_code == 200
    bill_list = response.json()
    assert isinstance(bill_list, list)
    assert len(bill_list) > 0

# 主测试运行入口
if __name__ == "__main__":
    pytest.main([__file__])
