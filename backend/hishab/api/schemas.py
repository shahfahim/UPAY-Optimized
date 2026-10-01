"""Request bodies. Amounts are validated again in the engine (Bangla error messages)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    mobile: str = Field(min_length=1, max_length=20)
    pin: str = Field(min_length=1, max_length=12)


class RegisterStartIn(BaseModel):
    mobile: str = Field(min_length=1, max_length=20)


class RegisterVerifyIn(BaseModel):
    mobile: str = Field(min_length=1, max_length=20)
    otp: str = Field(min_length=1, max_length=10)
    name: str = Field(min_length=1, max_length=60)
    pin: str = Field(min_length=1, max_length=12)


class SimulateIn(BaseModel):
    action_id: str = Field(min_length=1, max_length=60)


class RespondIn(BaseModel):
    accepted: bool


class TimeTravelIn(BaseModel):
    days: int


class BudgetIn(BaseModel):
    mode: Literal["auto", "manual"]
    manual: dict[str, float] = Field(default_factory=dict)


class PocketMoveIn(BaseModel):
    direction: Literal["in", "out"]
    amount: float | str


class PaisaIn(BaseModel):
    on: bool


class GoalIn(BaseModel):
    target: float | str
    months: int | str
    pocket: str | None = None


class DpsAdviceIn(BaseModel):
    goal_target: float | None = None


class DpsOpenIn(BaseModel):
    monthly: float | str
    tenure_months: int | str


class EmergencyIn(BaseModel):
    amount: float | str


class CategorySuggestIn(BaseModel):
    counterparty_id: str | None = None
    counterparty_type: str = "merchant"
    amount: float | str = 0


class CategoryConfirmIn(BaseModel):
    counterparty_id: str = Field(min_length=1, max_length=60)
    category: str = Field(min_length=1, max_length=30)


class RouteIn(BaseModel):
    amount: float | str
    destination: str = "other_mfs_wallet"


class SendIn(BaseModel):
    type: Literal["send_money", "cash_out", "merchant_pay", "bill_pay", "mobile_recharge", "npsb", "fund_transfer"]
    amount: float | str
    counterparty_id: str | None = None
    counterparty_name: str | None = None
    destination: str | None = None
    category: str | None = None


class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)  # the 500-char rule is enforced with a Bangla message
