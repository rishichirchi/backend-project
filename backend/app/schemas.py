from pydantic import BaseModel, ConfigDict
import datetime
from enum import Enum
from typing import List, Optional

class RequestStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class NotificationType(str, Enum):
    connection_request = "connection_request"
    connection_accepted = "connection_accepted"
    connection_rejected = "connection_rejected"
    new_message = "new_message"

class UserCreate(BaseModel):
    username: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str

class ConnectionRequestCreate(BaseModel):
    receiver_id: int

class ConnectionRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sender_id: int
    receiver_id: int
    status: RequestStatus
    created_at: datetime.datetime

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime.datetime

class MessageWithUsers(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: datetime.datetime
    sender_username: str
    receiver_username: str

class ChatHistoryResponse(BaseModel):
    messages: List[MessageOut]
    total_count: int
    page: int
    limit: int

class WSMessageType(str, Enum):
    message = "message"
    user_connected = "user_connected"
    user_disconnected = "user_disconnected"
    error = "error"

class WSMessage(BaseModel):
    type: WSMessageType
    content: str
    sender_id: int
    receiver_id: int
    timestamp: datetime.datetime

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime.datetime
    related_user_id: Optional[int] = None
    related_request_id: Optional[int] = None
    related_message_id: Optional[int] = None

class NotificationWithDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime.datetime
    related_user_id: Optional[int] = None
    related_user_username: Optional[str] = None
    related_request_id: Optional[int] = None
    related_message_id: Optional[int] = None

class NotificationMarkRead(BaseModel):
    notification_ids: List[int]

class NotificationCount(BaseModel):
    total_count: int
    unread_count: int

class NotificationResponse(BaseModel):
    notifications: List[NotificationWithDetails]
    total_count: int
    unread_count: int
