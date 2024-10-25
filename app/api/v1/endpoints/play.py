from fastapi import APIRouter
from app.models.response import ResponseModel
from app.utils.utils import get_landlord_score
from app.models.play import PredictPutCardModel


from app.utils.predict import Predict

router = APIRouter()

@router.get("/play/pklord/getLandlordScore",response_model=ResponseModel)
async def getLandlordScore(current_hand: str):
    score = get_landlord_score(current_hand)
    return ResponseModel(code=200, msg="success",data=score)


@router.post("/play/pklord/predictPutCard", response_model=ResponseModel)
async def predictPutCard(data: PredictPutCardModel):
    playable = Predict.play_cards(data)
    return ResponseModel(code=200, msg="success", data=playable)
