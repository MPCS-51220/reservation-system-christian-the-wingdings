from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Machine(BaseModel):
    id: int
    name: str
    quantity: str
    cooldown: float
    rate: bool
    
class User(BaseModel):
    username: str
    password: str
    role: Optional[str] = None
    salt: Optional[str] = None

class Reservation(BaseModel):
    id: Optional[int] = None
    customer: str
    machine: Machine
    start_date: datetime
    end_date: datetime
    total_cost: Optional[float] = None
    down_payment: Optional[float] = None
    
class CancelledReservation(BaseModel):
    id: int
    reservation: Reservation
    timestamp: datetime
    refund: float
