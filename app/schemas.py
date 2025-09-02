from pydantic import BaseModel
import datetime
from enum import Enum

class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class UserCreate(BaseModel):
    username: str

class UserOut(BaseModel):
    id: int
    username: str
    class Config: orm_mode = True

class ConnectionRequestCreate(BaseModel):
    receiver_id: int

class ConnectionRequestOut(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    status: RequestStatus
    created_at: datetime.datetime
    class Config: orm_mode = True
