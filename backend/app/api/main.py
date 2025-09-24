"""FastAPI application for HappyRobot Carrier Sales API."""
import os
import logging
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
from .db_models import CallSession, Load

API_KEY = os.getenv("API_KEY")

app = FastAPI(
    title="HappyRobot Carrier Sales API",
    description="API for automated carrier sales negotiations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    init_database()


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
    return await verify_carrier(request.carrier_mc)


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
    logger.info(f"OFFER EVALUATE - load_id: {request.load_id}, initial_rate: {request.initial_rate}, agreed_rate: {request.agreed_rate}, negotiation_rounds: {request.negotiation_rounds}")
    
    return evaluate_offer(
        db=db,
        load_id=request.load_id,
        initial_rate=request.initial_rate,
        agreed_rate=request.agreed_rate,
        negotiation_rounds=request.negotiation_rounds
    )


@app.post("/api/events/call-completed")
async def complete_call(
    request: CallCompleteRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Store completed call data for metrics."""
    logger.info(f"CALL COMPLETED - call_id: {request.call_id}, initial_rate: {request.initial_rate}, agreed_rate: {request.agreed_rate}, classification: {request.classification}")
    
    call_session = CallSession(
        call_id=request.call_id,
        load_id=request.load_id,
        carrier_mc=request.carrier_mc,
        carrier_name=request.carrier_name,
        initial_rate=request.initial_rate,
        agreed_rate=request.agreed_rate,
        negotiation_rounds=request.negotiation_rounds,
        classification=request.classification,
        sentiment=request.sentiment,
        duration_sec=request.duration_sec,
        transcript=request.transcript
    )

    db.add(call_session)
    db.commit()

    return {"status": "recorded"}


@app.get("/api/call-sessions")
async def get_call_sessions(
    limit: int = 20,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get recent call sessions."""
    sessions = db.query(CallSession).order_by(CallSession.created_at.desc()).limit(limit).all()
    
    return [
        {
            "call_id": session.call_id,
            "carrier_mc": session.carrier_mc,
            "carrier_name": session.carrier_name,
            "load_id": session.load_id,
            "initial_rate": session.initial_rate,
            "agreed_rate": session.agreed_rate,
            "negotiation_rounds": session.negotiation_rounds,
            "classification": session.classification,
            "sentiment": session.sentiment,
            "duration_sec": session.duration_sec,
            "transcript": session.transcript,
            "created_at": session.created_at.isoformat() if session.created_at else None
        }
        for session in sessions
    ]


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
        outcome = call.classification or "unknown"
        outcomes[outcome] = outcomes.get(outcome, 0) + 1

        sentiment = call.sentiment or "unknown"
        sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1

    # Calculate conversion rate
    conversion_rate = (outcomes.get("accepted", 0) / total_calls * 100) if total_calls > 0 else 0

    # Calculate average negotiation rounds
    negotiation_rounds = [call.negotiation_rounds for call in calls if call.negotiation_rounds is not None]
    avg_negotiation_rounds = sum(negotiation_rounds) / len(negotiation_rounds) if negotiation_rounds else 0

    # Calculate actual revenue from accepted calls
    total_revenue = 0
    for call in calls:
        if call.classification == "accepted":
            # Use negotiated rate if available, otherwise initial rate
            rate = call.agreed_rate if call.agreed_rate is not None else call.initial_rate
            if rate:
                total_revenue += rate

    return MetricsResponse(
        total_calls=total_calls,
        conversion_rate=round(conversion_rate, 2),
        avg_negotiation_rounds=round(avg_negotiation_rounds, 2),
        outcomes=outcomes,
        sentiment=sentiment_dist,
        total_revenue=round(total_revenue, 2)
    )
