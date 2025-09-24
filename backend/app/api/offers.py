"""Negotiation rules and offer evaluation logic."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from .db_models import Load


def evaluate_offer(
    db: Session,
    load_id: str,
    initial_rate: float,
    negotiated_rate: Optional[float] = None,
    negotiation_rounds: Optional[int] = None
) -> Dict[str, Any]:
    """
    Evaluate a carrier's offer against negotiation rules.

    Floor calculation: max(loadboard_rate * 0.9, loadboard_rate - 150)
    """
    # Get load information
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        return {
            "decision": "reject",
            "rate": None,
            "floor": 0,
            "reason": "Load not found"
        }

    loadboard_rate = load.loadboard_rate
    floor_price = max(loadboard_rate * 0.9, loadboard_rate - 150)

    # If no negotiated rate provided, use initial rate
    carrier_offer = negotiated_rate if negotiated_rate is not None else initial_rate

    # Check floor price
    if carrier_offer < floor_price:
        return {
            "decision": "reject",
            "rate": None,
            "floor": floor_price,
            "reason": f"Offer below minimum floor price of ${floor_price:.2f}"
        }

    # Check if offer is acceptable (within 5% of loadboard rate)
    if carrier_offer >= loadboard_rate * 0.95:
        return {
            "decision": "accept",
            "rate": carrier_offer,
            "floor": floor_price,
            "reason": "Offer accepted"
        }

    # Calculate counter offer based on negotiation rounds (if provided)
    if negotiation_rounds is not None and negotiation_rounds <= 3:
        # Progressive counter offers: 92%, 89%, 87% of loadboard rate
        counter_multipliers = [0.92, 0.89, 0.87]
        multiplier = counter_multipliers[min(negotiation_rounds - 1, 2)]
        counter_offer = loadboard_rate * multiplier

        counter_offer = max(counter_offer, floor_price)

        return {
            "decision": "counter",
            "rate": round(counter_offer, 2),
            "floor": floor_price,
            "reason": f"Counter offer: ${counter_offer:.2f}"
        }

    # Default counter offer
    counter_offer = max(loadboard_rate * 0.90, floor_price)
    return {
        "decision": "counter",
        "rate": round(counter_offer, 2),
        "floor": floor_price,
        "reason": f"Counter offer: ${counter_offer:.2f}"
    }
