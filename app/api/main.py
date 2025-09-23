"""FastAPI application for HappyRobot Carrier Sales API."""
import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .models import (
    CarrierVerifyRequest, CarrierVerifyResponse,
    LoadSearchResponse, OfferEvaluateRequest, OfferEvaluateResponse,
    CallCompleteRequest, HealthResponse, MetricsResponse
)
from ..database import get_db, init_database, engine
from .fmcsa import verify_carrier
from .loads import search_loads
from .offers import evaluate_offer
from .db_models import CallSession

# API Key authentication
API_KEY = os.getenv("API_KEY")

app = FastAPI(
    title="HappyRobot Carrier Sales API",
    description="API for automated carrier sales negotiations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables and seed data on startup."""
    init_database()
    
    # Auto-seed sample loads if database is empty
    from sqlalchemy.orm import Session
    from .db_models import Load
    
    session = Session(engine)
    if session.query(Load).count() == 0:
        # Add sample loads
        sample_loads = [
            Load(load_id="LOAD001", origin="Chicago, IL", destination="Atlanta, GA", 
                 pickup_datetime="2024-01-15 08:00", delivery_datetime="2024-01-16 18:00",
                 equipment_type="Dry Van", loadboard_rate=2500.00, weight=35000, 
                 commodity_type="General Freight", miles=715),
            Load(load_id="LOAD002", origin="Dallas, TX", destination="Phoenix, AZ",
                 pickup_datetime="2024-01-16 10:00", delivery_datetime="2024-01-17 16:00", 
                 equipment_type="Flatbed", loadboard_rate=2800.00, weight=45000,
                 commodity_type="Steel Coils", miles=887),
            Load(load_id="LOAD003", origin="Miami, FL", destination="New York, NY",
                 pickup_datetime="2024-01-17 06:00", delivery_datetime="2024-01-19 14:00",
                 equipment_type="Reefer", loadboard_rate=3200.00, weight=38000,
                 commodity_type="Frozen Foods", miles=1283)
        ]
        for load in sample_loads:
            session.add(load)
        session.commit()
    session.close()


def verify_api_key(x_api_key: Optional[str] = Header(None, alias="x-api-key")):
    """Verify API key authentication."""
    if not API_KEY:
        return  # Skip auth in development
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")


@app.post("/api/verify", response_model=CarrierVerifyResponse)
async def verify_carrier_endpoint(
    request: CarrierVerifyRequest,
    api_key: str = Depends(verify_api_key)
):
    """Verify carrier eligibility with FMCSA."""
    return await verify_carrier(request.mcNumber)


@app.get("/api/loads/search", response_model=list[LoadSearchResponse])
async def search_loads_endpoint(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
    pickup_from: Optional[str] = None,
    pickup_to: Optional[str] = None,
    max_results: int = 10,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Search for available loads."""
    return search_loads(
        db=db,
        origin=origin,
        destination=destination,
        equipment_type=equipment_type,
        pickup_from=pickup_from,
        pickup_to=pickup_to,
        max_results=max_results
    )


@app.post("/api/offers/evaluate", response_model=OfferEvaluateResponse)
async def evaluate_offer_endpoint(
    request: OfferEvaluateRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Evaluate a carrier's offer."""
    return evaluate_offer(
        db=db,
        load_id=request.load_id,
        ask_rate=request.ask_rate,
        counter_rate=request.counter_rate
    )


@app.post("/api/events/call-completed")
async def complete_call(
    request: CallCompleteRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Store completed call data for metrics."""
    # Create call session record
    sentiment = None
    if request.extraction and isinstance(request.extraction, dict):
        sentiment = request.extraction.get("sentiment")

    call_session = CallSession(
        session_id=request.call_id,
        transcript=request.transcript,
        extracted_data=str(request.extraction),  # Store as JSON string
        outcome=request.classification,
        sentiment=sentiment,
        call_duration=request.duration_sec
    )

    db.add(call_session)
    db.commit()

    return {"status": "recorded"}


@app.get("/api/metrics", response_model=MetricsResponse)
async def get_metrics(
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get call metrics and analytics."""
    # Get total calls
    total_calls = db.query(CallSession).count()

    # Get outcomes distribution
    outcomes = {}
    sentiment_dist = {}

    calls = db.query(CallSession).all()
    for call in calls:
        # Outcomes
        outcome = call.outcome or "unknown"
        outcomes[outcome] = outcomes.get(outcome, 0) + 1

        # Sentiment
        sentiment = call.sentiment or "unknown"
        sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1

    # Calculate conversion rate (accepted calls)
    conversion_rate = (outcomes.get("accepted", 0) / total_calls * 100) if total_calls > 0 else 0

    return MetricsResponse(
        total_calls=total_calls,
        conversion_rate=round(conversion_rate, 2),
        avg_negotiation_rounds=0,
        outcomes=outcomes,
        sentiment=sentiment_dist
    )
