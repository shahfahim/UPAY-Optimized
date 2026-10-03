from fastapi import APIRouter, Query, Path
from pydantic import BaseModel
import random
import uuid

router = APIRouter(tags=["Agents"])

class AgentInfo(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    distance_m: int
    ai_liquidity_score: float
    predicted_status: str

@router.get("/users/{uid}/agents/nearby", response_model=list[AgentInfo])
def get_nearby_agents(
    uid: str = Path(...),
    lat: float = Query(...),
    lng: float = Query(...)
):
    base_agents = [
        ("Rahim Store", 0.85, 120),
        ("Karim Telecom", 0.45, 450),
        ("Bhai Bhai Traders", 0.15, 800),
        ("Sumi Enterprise", 0.92, 1200),
        ("Molla Pharmacy", 0.60, 2500)
    ]
    
    selected = random.sample(base_agents, random.randint(3, 5))
    results = []
    
    for name, score, dist in selected:
        # Determine color based on score to match frontend expectations
        if score >= 0.8:
            status = 'green'
        elif score >= 0.4:
            status = 'amber'
        else:
            status = 'red'
            
        results.append(AgentInfo(
            id=str(uuid.uuid4()),
            name=name,
            lat=lat + random.uniform(-0.01, 0.01),
            lng=lng + random.uniform(-0.01, 0.01),
            distance_m=dist,
            ai_liquidity_score=score,
            predicted_status=status
        ))
        
    return results
