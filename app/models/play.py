

from typing import List

from pydantic import BaseModel


class PlayableCardsModel(BaseModel):
    cards: str
    seat: int

class PredictPutCardModel(BaseModel):
    init_card: str
    current_hand: str
    fundcards: str
    other_hands: str
    current_multiplier: int
    self_seat: int
    landlord_seat: int
    playables: List[PlayableCardsModel]

