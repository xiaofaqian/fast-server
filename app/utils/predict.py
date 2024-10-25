
import json
from app.utils import utils
from app.models.play import PredictPutCardModel
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

model_path =  {
        "landlord": './app/utils/douzero_checkpoints/landlord_weights_4379446400.ckpt',
        "landlord_up": './app/utils/douzero_checkpoints/landlord_up_weights_4379446400.ckpt',
        "landlord_down": './app/utils/douzero_checkpoints/landlord_down_weights_4379446400.ckpt'
}

landlord_agent = DeepAgent("landlord",model_path["landlord"])
landlord_up_agent = DeepAgent("landlord_up",model_path["landlord_up"])
class Predict:
        
    @staticmethod
    def get_info_set(json_data):
        info_set = InfoSet(json_data["player_position"])
        info_set.from_dict(json_data)
        return info_set
    
    @staticmethod
    def get_best_action(info_set):
        if info_set.player_position == "landlord":
            agent = landlord_agent
        elif info_set.player_position == "landlord_up":
            agent = landlord_up_agent
        best_action = landlord_agent.act(info_set)
        return best_action

    @staticmethod
    def play_cards(data: PredictPutCardModel) -> str:
        json_data = utils.DataTransformer.transform(data)
        info_set = Predict.get_info_set(json_data)
        best_actions = Predict.get_best_action(info_set)
        result = ''
        if (len(best_actions) == 0):
            return 'pass'
        for best_action in best_actions:
            result += utils.get_reverse_card_map(best_action)
        return result
    
    
    
