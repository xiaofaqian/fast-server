# 假设当前已经打出的牌为 '777888'，表示一个三顺
from app.models.play import PredictPutCardModel
from app.utils.utils import DataTransformer, get_gt_cards,get_landlord_score,playable_cards_from_hand
from app.utils.predict import Predict


# played_cards = '777888'

# current_hand = '999TTTAAKK'

# gt_cards = get_gt_cards(played_cards, current_hand)
# print(gt_cards)
# score = get_landlord_score(current_hand)
# print(score)
# playable_cards = playable_cards_from_hand(current_hand)
# print(list(playable_cards))

if __name__ == "__main__":
    # 构造示例数据
    data = {
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

    predict_model = PredictPutCardModel(**data)
    best_action = Predict.play_cards(predict_model)
    print(best_action)
    # result = DataTransformer.transform(predict_model)

    # # 输出结果
    # import json
    # print(json.dumps(result, ensure_ascii=False, indent=4))