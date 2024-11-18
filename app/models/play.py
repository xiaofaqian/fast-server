

from typing import List

from pydantic import BaseModel


class PlayableCardsModel(BaseModel):
    cards: str
    seat: int

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


