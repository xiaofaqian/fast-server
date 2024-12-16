

from typing import List

from pydantic import BaseModel


class PlayableCardsModel(BaseModel):
    cards: str
    seat: int
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
           cards = data.get('cards', ''),
           seat = data.get('seat', 0),
        ) 


class PredictPutCardModel(BaseModel):
    init_card: str
    current_hand: str
    opponent_hands: str
    fundcards: str
    other_hands: str
    current_multiplier: int
    self_seat: int
    landlord_seat: int
    pk_status: int
    self_win_card_num:int
    oppo_win_card_num:int
    playables: List[PlayableCardsModel]

    @classmethod
    def from_dict(cls, data: dict):
        """
        将字典转换为 PredictPutCardModel 对象的类方法
        
        Args:
            data (dict): 包含模型所需数据的字典
            
        Returns:
            PredictPutCardModel: 转换后的对象
        """
        # 确保 playables 字段正确转换
        playables = []
        if 'playables' in data:
            for playable in data['playables']:
                if isinstance(playable, dict):
                    # 假设 PlayableCardsModel 也有一个 from_dict 方法
                    playables.append(PlayableCardsModel.from_dict(playable))
                else:
                    playables.append(playable)
        
        return cls(
            init_card=data.get('init_card', ''),
            current_hand=data.get('current_hand', ''),
            opponent_hands=data.get('opponent_hands', ''),
            fundcards=data.get('fundcards', ''),
            other_hands=data.get('other_hands', ''),
            current_multiplier=data.get('current_multiplier', 0),
            self_seat=data.get('self_seat', 0),
            landlord_seat=data.get('landlord_seat', 0),
            pk_status=data.get('pk_status', 0),
            self_win_card_num=data.get('self_win_card_num', 0),
            oppo_win_card_num=data.get('oppo_win_card_num', 0),
            playables=playables
        )


