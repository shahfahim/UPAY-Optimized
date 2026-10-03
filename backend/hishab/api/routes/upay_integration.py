from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any

from hishab.security import RateLimiter, PII_Stripper

router = APIRouter(tags=["UPAY Integration"])

class PredictRequest(BaseModel):
    query: str

class PredictResponse(BaseModel):
    intent: str
    confidence: float
    extracted_entities: Dict[str, Any]

# Global rate limiter for this endpoint
upay_rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

def check_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not upay_rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please slow down.")
    return client_ip

def get_ml_engine():
    try:
        from hishab.ml_engine import predict_intent
        if predict_intent is None:
            raise ImportError()
        return predict_intent
    except ImportError:
        raise HTTPException(status_code=503, detail="ML model is not loaded or available.")

@router.post("/upay/ai/predict", response_model=PredictResponse)
async def predict_upay_ai(
    request: PredictRequest, 
    ml_predict = Depends(get_ml_engine),
    client_ip: str = Depends(check_rate_limit)
):
    try:
        # Sanitize PII
        safe_query = PII_Stripper(request.query)
        result = ml_predict(safe_query)
        
        return PredictResponse(
            intent=result.get("intent", "unknown"),
            confidence=result.get("confidence", 0.0),
            extracted_entities=result.get("extracted_entities", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
