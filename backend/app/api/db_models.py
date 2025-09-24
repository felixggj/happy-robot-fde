"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from app.database import Base


class Load(Base):
    """Loads model for the database."""
    __tablename__ = "loads"

    load_id = Column(String(50), primary_key=True)
    origin = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    pickup_datetime = Column(String(50), nullable=False)
    delivery_datetime = Column(String(50), nullable=False)
    equipment_type = Column(String(50), nullable=False)
    loadboard_rate = Column(Float, nullable=False)
    notes = Column(Text)
    weight = Column(Float)
    commodity_type = Column(String(100))
    num_of_pieces = Column(Integer)
    miles = Column(Float)
    dimensions = Column(String(100))
    status = Column(String(20), default="available")
    created_at = Column(DateTime, server_default=func.current_timestamp())


class CallSession(Base):
    """Call session for tracking negotiations and outcomes."""
    __tablename__ = "call_sessions"

    call_id = Column(String(100), primary_key=True)
    carrier_mc = Column(String(20))
    carrier_name = Column(String(100))
    load_id = Column(String(50))
    initial_rate = Column(Float)
    agreed_rate = Column(Float)
    negotiation_rounds = Column(Integer)
    classification = Column(String(50))
    sentiment = Column(String(20))
    duration_sec = Column(Integer)
    transcript = Column(Text)
    created_at = Column(DateTime, server_default=func.current_timestamp())
