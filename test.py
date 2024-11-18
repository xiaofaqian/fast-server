from app.utils.pklord_ai import PklordAI
from app.models.play import PredictPutCardModel, PlayableCardsModel

def test_play_cards():
    # 准备测试数据
    test_data = {
        "current_hand": "77889TTQ22B",
        "fundcards": "9TJ",
        "init_card": "577889TTQQKKKK22B",
        "other_hands": "",
        "current_multiplier": 54,
        "playables": [
            {"cards": "56789", "seat": 0},
            {"cards": "KKKK", "seat": 1},
            {"cards": "", "seat": 0},
            {"cards": "5", "seat": 1},
            {"cards": "J", "seat": 0},
            {"cards": "Q", "seat": 1},
            {"cards": "R", "seat": 0},
            {"cards": "", "seat": 1},
            {"cards": "AAAA", "seat": 0},
            {"cards": "", "seat": 1},
            {"cards": "6789TJQ", "seat": 0},
            {"cards": "", "seat": 1},
            {"cards": "22", "seat": 0}
        ],
        "self_seat": 1,
        "landlord_seat": 0
    }

    try:
        # 调用play_cards方法
        result = PklordAI.play_cards(test_data)
        print("测试结果:")
        print(result)
    except Exception as e:
        print(f"测试出错: {e}")

if __name__ == "__main__":
    test_play_cards()
