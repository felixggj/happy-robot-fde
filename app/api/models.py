"""Pydantic models for API requests and responses."""
from typing import Optional, List
from pydantic import BaseModel


# FMCSA Verification
class CarrierVerifyRequest(BaseModel):
    mcNumber: str


class CarrierVerifyResponse(BaseModel):
    eligible: bool
    legalName: Optional[str] = None
    status: Optional[str] = None
    riskNotes: List[str] = []


# Load Search
class LoadSearchResponse(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: float
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None
    score: float


# Negotiation
class OfferEvaluateRequest(BaseModel):
    load_id: str
    ask_rate: float
    counter_rate: Optional[float] = None
    carrier_history: Optional[dict] = None


class OfferEvaluateResponse(BaseModel):
    decision: str  # "accept" | "counter" | "reject"
    rate: Optional[float] = None
    floor: float
    reason: str


# Call Completion
class CallCompleteRequest(BaseModel):
    call_id: str
    transcript: str
    extraction: dict
    classification: str
    duration_sec: int


# Health Check
class HealthResponse(BaseModel):
    status: str


# Metrics
class MetricsResponse(BaseModel):
    total_calls: int
    conversion_rate: float
    avg_negotiation_rounds: float
    outcomes: dict
    sentiment: dict
