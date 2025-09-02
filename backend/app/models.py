from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
import enum
import datetime
from app.core.database import Base

class RequestStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class NotificationType(str, enum.Enum):
    connection_request = "connection_request"
    connection_accepted = "connection_accepted"
    connection_rejected = "connection_rejected"
    new_message = "new_message"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

    sent_requests = relationship("ConnectionRequest", foreign_keys="ConnectionRequest.sender_id")
    received_requests = relationship("ConnectionRequest", foreign_keys="ConnectionRequest.receiver_id")
    
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    
    notifications = relationship("Notification", foreign_keys="Notification.user_id", back_populates="user")

class ConnectionRequest(Base):
    __tablename__ = "connection_requests"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(RequestStatus), default=RequestStatus.pending)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_request_id = Column(Integer, ForeignKey("connection_requests.id"), nullable=True)
    related_message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    related_user = relationship("User", foreign_keys=[related_user_id])
    related_request = relationship("ConnectionRequest", foreign_keys=[related_request_id])
    related_message = relationship("Message", foreign_keys=[related_message_id])
