"""Nearby agents — demo data only (see hishab.engine.agents)."""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from hishab.api.deps import require_user
from hishab.engine.agents import nearby_agents

router = APIRouter(tags=["Agents"])


class AgentInfo(BaseModel):
    id: str
    name: str
    lat: float
    lng: float
    distance_m: int
    cash_hint: float
    cash_status: str
    is_demo: bool


@router.get("/users/{uid}/agents/nearby", response_model=list[AgentInfo])
def get_nearby_agents(
    uid: str = Depends(require_user),
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
):
    return nearby_agents(lat, lng)
