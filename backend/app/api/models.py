"""Pydantic models for API requests and responses."""
from typing import Optional, List
from pydantic import BaseModel, validator


# FMCSA Verification
class CarrierVerifyRequest(BaseModel):
    carrier_mc: str


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
    initial_rate: float
    agreed_rate: Optional[float] = None
    negotiation_rounds: Optional[int] = None
    counter_offer: Optional[float] = None  # Extra field from HappyRobot
    
    class Config:
        extra = "ignore"  # Ignore extra fields
        
    @validator('initial_rate', pre=True)
    def parse_initial_rate(cls, v):
        return float(v)
            
    @validator('agreed_rate', 'counter_offer', pre=True)
    def parse_float_fields(cls, v):
        return float(v) if v is not None and v != "" else None
            
    @validator('negotiation_rounds', pre=True)
    def parse_negotiation_rounds(cls, v):
        return int(v) if v is not None and v != "" else None


class OfferEvaluateResponse(BaseModel):
    decision: str 
    rate: Optional[float] = None
    floor: float
    reason: str


# Call Completion
class CallCompleteRequest(BaseModel):
    call_id: str
    load_id: Optional[str] = None
    carrier_mc: Optional[str] = None
    carrier_name: Optional[str] = None
    transcript: str
    initial_rate: Optional[float] = None
    agreed_rate: Optional[float] = None
    negotiation_rounds: Optional[int] = None
    classification: str
    sentiment: Optional[str] = None
    duration_sec: int
    
    class Config:
        extra = "ignore"  # Ignore extra fields
        
    @validator('load_id', 'carrier_mc', 'carrier_name', 'sentiment', pre=True)
    def parse_optional_strings(cls, v):
        return None if v == "" else v
        
    @validator('transcript', pre=True)
    def parse_transcript(cls, v):
        return "" if v in ["[]", ""] else str(v)
        
    @validator('initial_rate', 'agreed_rate', pre=True)
    def parse_float_fields(cls, v):
        return float(v) if v is not None and v != "" else None
            
    @validator('negotiation_rounds', pre=True)  
    def parse_negotiation_rounds(cls, v):
        return int(v) if v is not None and v != "" else None
        
    @validator('duration_sec', pre=True)
    def parse_duration_sec(cls, v):
        return int(v)


# Health Check
class HealthResponse(BaseModel):
    status: str


# Call Sessions
class CallSessionResponse(BaseModel):
    call_id: str
    carrier_mc: Optional[str] = None
    carrier_name: Optional[str] = None
    load_id: Optional[str] = None
    initial_rate: Optional[float] = None
    agreed_rate: Optional[float] = None
    negotiation_rounds: Optional[int] = None
    classification: Optional[str] = None
    sentiment: Optional[str] = None
    duration_sec: Optional[int] = None
    transcript: Optional[str] = None
    created_at: str


# Metrics
class MetricsResponse(BaseModel):
    total_calls: int
    conversion_rate: float
    avg_negotiation_rounds: float
    outcomes: dict
    sentiment: dict
    total_revenue: float
