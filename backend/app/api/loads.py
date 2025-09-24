"""Load search and matching logic."""
from typing import List, Optional
from sqlalchemy.orm import Session

from .db_models import Load
from .models import LoadSearchResponse


def search_loads(
    db: Session,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None,
    pickup_from: Optional[str] = None,
    pickup_to: Optional[str] = None,
    max_results: int = 10
) -> List[LoadSearchResponse]:
    """
    Search for loads based on criteria.
    Implements basic matching with scoring.
    """
    query = db.query(Load).filter(Load.status == "available")

    # Apply filters
    if origin:
        query = query.filter(Load.origin.ilike(f"%{origin}%"))

    if destination:
        query = query.filter(Load.destination.ilike(f"%{destination}%"))

    if equipment_type:
        query = query.filter(Load.equipment_type.ilike(f"%{equipment_type}%"))

    # Date filtering (simplified)
    if pickup_from:
        query = query.filter(Load.pickup_datetime >= pickup_from)

    if pickup_to:
        query = query.filter(Load.pickup_datetime <= pickup_to)

    # Get results and calculate scores
    loads = query.limit(max_results * 2).all()  # Get more for scoring

    results = []
    for load in loads:
        score = calculate_match_score(load, origin, destination, equipment_type)
        if score > 0:  # Only include matches with positive scores
            results.append(LoadSearchResponse(
                load_id=load.load_id,
                origin=load.origin,
                destination=load.destination,
                pickup_datetime=load.pickup_datetime,
                delivery_datetime=load.delivery_datetime,
                equipment_type=load.equipment_type,
                loadboard_rate=load.loadboard_rate,
                notes=load.notes,
                weight=load.weight,
                commodity_type=load.commodity_type,
                num_of_pieces=load.num_of_pieces,
                miles=load.miles,
                dimensions=load.dimensions,
                score=score
            ))

    # Sort by score and limit results
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:max_results]


def calculate_match_score(
    load: Load,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    equipment_type: Optional[str] = None
) -> float:
    """
    Calculate match score for a load.
    Simple scoring based on exact and partial matches.
    """
    score = 0.0

    # Equipment type match (highest weight)
    if equipment_type and load.equipment_type.lower() == equipment_type.lower():
        score += 100
    elif equipment_type and equipment_type.lower() in load.equipment_type.lower():
        score += 50

    # Origin/destination matches
    if origin and origin.lower() in load.origin.lower():
        score += 30
    if destination and destination.lower() in load.destination.lower():
        score += 30

    # Base score for available loads
    score += 10

    return score
