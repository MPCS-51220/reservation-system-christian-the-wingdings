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

class Reservation_Req(BaseModel):
    id: Optional[int] = None
    customer: str
    machine: str
    start_date: str
    end_date: str
    total_cost: Optional[float] = None
    down_payment: Optional[float] = None
    
class CancelledReservation(BaseModel):
    id: int
    reservation: Reservation_Req
    timestamp: datetime
    refund: float
