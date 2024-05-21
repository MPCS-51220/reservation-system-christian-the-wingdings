from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Machine(BaseModel):
    id: int
    name: str
    quantity: str
    cooldown: float
    rate: bool

class UserLogin(BaseModel):
    username: str
    password: str
        
class User(BaseModel):
    username: Optional[str] = None
    password: str
    role: Optional[str] = None
    salt: Optional[str] = None

class Reservation_Req(BaseModel):
    id: Optional[int] = None
    customer: Optional[str] = None
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

class UserRole(BaseModel):
    username: str
    role: str

class BusinessRule(BaseModel):
    rule: str
    value: str

class Activation(BaseModel):
    username:str

class RemoteRequest(BaseModel):
    start_time:str
    end_time:str
    client_name:str
    machine_name:str
    time_zone:str
    blocks:str

