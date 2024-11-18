#!/usr/bin/env python3
import requests
import uuid
import time
import traceback

BASE_URL = "http://0.0.0.0:8003/api/v1/play"

def test_get_landlord_score():
    """测试获取叫牌分数接口"""
    try:
        url = f"{BASE_URL}/pklord/getLandlordScore"
        params = {
            "current_hand": "577889TTQQKKKK22BR",
            "pk_status": 0,
            "call_time": 1,
            "oppo_call": 0
        }
        
        response = requests.get(url, params=params)
        print("获取叫牌分数测试:")
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}")
        print(f"返回结果: {response.text}")
        return response
    except Exception as e:
        print(f"请求发生错误: {e}")
        traceback.print_exc()
        return None

def test_predict_put_card():
    """测试预测出牌接口"""
    try:
        url = f"{BASE_URL}/pklord/predictPutCard"
        data = {
        "current_hand": "77889TTQ22BR",
        "fundcards": "9TJ",
        "init_card": "577889TTQQKKKK22BR",
        "other_hands": "",
        "current_multiplier": 54,
        "opponent_hands": "",
        "playables": [
            {"cards": "56789", "seat": 0},
            {"cards": "KKKK", "seat": 1},
            {"cards": "", "seat": 0},
            {"cards": "5", "seat": 1},
            {"cards": "J", "seat": 0},
            {"cards": "Q", "seat": 1},
            {"cards": "2", "seat": 0},
            {"cards": "", "seat": 1},
        ],
        "pk_status": 2,
        "self_seat": 1,
        "self_win_card_num": 1,
        "oppo_win_card_num": 0,
        "landlord_seat": 0
    }
        
        response = requests.post(url, json=data)

        print("\n预测出牌测试:")
        print(f"URL: {url}")
        print(f"请求数据: {data}")
        print(f"状态码: {response.status_code}")
        print(f"返回结果: {response.text}")
        return response
    except Exception as e:
        print(f"请求发生错误: {e}")
        traceback.print_exc()
        return None

def test_get_request_result(request_id):
    """测试获取请求结果接口"""
    try:
        url = f"{BASE_URL}/pklord/getRequestResult"
        params = {"request_id": request_id}
        
        # 等待一段时间，让服务器处理请求
        time.sleep(1)
        
        response = requests.get(url, params=params)
        print("\n获取请求结果测试:")
        print(f"URL: {url}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}")
        print(f"返回结果: {response.text}")
        return response
    except Exception as e:
        print(f"请求发生错误: {e}")
        traceback.print_exc()
        return None

def main():
    """主测试函数"""
    # 测试获取叫牌分数
    # landlord_score_response = test_get_landlord_score()
    
    # 测试预测出牌
    predict_response = test_predict_put_card()
    
    # 如果预测出牌成功，获取请求结果
    if predict_response and predict_response.status_code == 200:
        try:
            request_id = predict_response.json().get('data')
            if request_id:
                request_result = test_get_request_result(request_id)
        except Exception as e:
            print(f"获取请求结果时发生错误: {e}")

if __name__ == "__main__":
    main()
