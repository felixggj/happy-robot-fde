"""Negotiation rules and offer evaluation logic."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from .db_models import Load


def evaluate_offer(
    db: Session,
    load_id: str,
    initial_rate: float,
    agreed_rate: Optional[float] = None,
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
            "floor": 0.0,
            "reason": "Load not found"
        }

    loadboard_rate = load.loadboard_rate
    floor_price = max(loadboard_rate * 0.9, loadboard_rate - 150)

    # If agreed_rate is provided, evaluate final offer
    if agreed_rate is not None:
        if agreed_rate < floor_price:
            return {
                "decision": "reject",
                "rate": None,
                "floor": floor_price,
                "reason": f"Final offer ${agreed_rate:.2f} below minimum floor price of ${floor_price:.2f}"
            }
        
        return {
            "decision": "accept",
            "rate": agreed_rate,
            "floor": floor_price,
            "reason": f"Final offer accepted at ${agreed_rate:.2f}"
        }

    # No agreed rate - we're in negotiation mode
    # Calculate counter offer based on negotiation rounds
    round_number = negotiation_rounds if negotiation_rounds is not None else 1
    
    if round_number <= 3:
        # Progressive counter offers: 92%, 89%, 87% of loadboard rate
        counter_multipliers = [0.92, 0.89, 0.87]
        multiplier = counter_multipliers[min(round_number - 1, 2)]
        counter_offer = loadboard_rate * multiplier
        counter_offer = max(counter_offer, floor_price)
        
        return {
            "decision": "counter",
            "rate": round(counter_offer, 2),
            "floor": floor_price,
            "reason": f"Counter offer round {round_number}: ${counter_offer:.2f}"
        }
    
    # After 3 rounds, give floor price
    return {
        "decision": "counter",
        "rate": round(floor_price, 2),
        "floor": floor_price,
        "reason": f"Final counter offer: ${floor_price:.2f}"
    }
