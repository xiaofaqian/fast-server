import json
from app.utils.douzero.deep_agent import DeepAgent


class InfoSet(object):

    def __init__(self, player_position):
        self.player_position = player_position
        self.player_hand_cards = None
        self.num_cards_left_dict = None
        self.three_landlord_cards = None
        self.card_play_action_seq = None
        self.other_hand_cards = None
        self.legal_actions = None
        self.last_move = None
        self.last_two_moves = None
        self.last_move_dict = None
        self.played_cards = None
        self.all_handcards = None
        self.last_pid = None
        self.bomb_num = None
        self.init_card = None
        
    # 方法用于从字典更新对象属性
    def from_dict(self, data):
        for key, value in data.items():
            setattr(self, key, value)


json_data = """
{
    "player_position": "landlord",
    "player_hand_cards": [4, 5, 5, 7, 7, 8, 8, 9, 9, 9, 11, 11, 12, 13, 14, 14, 17, 20, 30],
    "num_cards_left_dict": {
        "landlord": 19,
        "landlord_up": 16,
        "landlord_down": 16
    },
    "three_landlord_cards": [4, 5, 7],
    "card_play_action_seq": [[3], [4], [12]],
    "other_hand_cards": [3, 3, 4, 4, 5, 5, 6, 8, 10, 11, 11, 13, 13, 17, 17, 17, 3, 6, 6, 6, 7, 7, 8, 9, 10, 10, 10, 12, 12, 13, 14, 14],
    "legal_actions": [[13], [14], [17], [20], [30], [20, 30], []],
    "last_move": [12],
    "last_two_moves": [[12], [4]],
    "last_move_dict": {
        "landlord": [3],
        "landlord_up": [12],
        "landlord_down": []
    },
    "played_cards": {
        "landlord": [3],
        "landlord_up": [12],
        "landlord_down": []
    },
    "all_handcards": {
        "landlord": [4, 5, 5, 7, 7, 8, 8, 9, 9, 9, 11, 11, 12, 13, 14, 14, 17, 20, 30],
        "landlord_up": [],
        "landlord_down": []
    },
    "last_pid": "landlord",
    "bomb_num": 0,
    "init_card": {
        "landlord": [4, 5, 5, 7, 7, 8, 8, 9, 9, 9, 11, 11, 12, 13, 14, 14, 17, 20, 30],
        "landlord_up": [],
        "landlord_down": [],
        "three_landlord_cards": [4, 5, 7]
    }
}
"""

model_path =  {
    "landlord": './douzero_checkpoints/landlord_weights_4379446400.ckpt',
    "landlord_up": './douzero_checkpoints/landlord_up_weights_4379446400.ckpt',
    "landlord_down": './douzero_checkpoints/landlord_down_weights_4379446400.ckpt'
}



def get_info_set(json_data):
    data = json.loads(json_data)
    info_set = InfoSet(data["player_position"])
    info_set.from_dict(data)
    print(info_set.player_position)
    return info_set

def get_best_action(info_set):
    agent = DeepAgent(info_set.player_position,model_path[info_set.player_position])
    best_action = agent.act(info_set)
    return best_action

info_set = get_info_set(json_data)
best_action = get_best_action(info_set)

print("best_action: ",best_action)

