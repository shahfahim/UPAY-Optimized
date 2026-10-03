from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from hishab.ml_engine import predict_intent
except ImportError:
    predict_intent = None

router = APIRouter(tags=["UPAY Integration"])

class PredictRequest(BaseModel):
    query: str

class PredictResponse(BaseModel):
    intent: str
    confidence: float
    extracted_entities: dict

@router.post("/upay/ai/predict", response_model=PredictResponse)
async def predict_upay_ai(request: PredictRequest):
    if predict_intent is None:
        raise HTTPException(status_code=503, detail="ML model is not loaded or available.")
    
    try:
        result = predict_intent(request.query)
        # Assuming result is a dict with intent, confidence, extracted_entities
        return PredictResponse(
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            extracted_entities=result.get("extracted_entities", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
