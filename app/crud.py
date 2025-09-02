from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from . import models, schemas
from typing import List

# User CRUD operations
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_connections(db: Session, user_id: int):
    """Get all users that are connected to the specified user"""
    # Get all accepted connection requests involving this user
    connection_requests = db.query(models.ConnectionRequest).filter(
        and_(
            or_(
                models.ConnectionRequest.sender_id == user_id,
                models.ConnectionRequest.receiver_id == user_id
            ),
            models.ConnectionRequest.status == schemas.RequestStatus.accepted
        )
    ).all()
    
    # Extract the connected user IDs
    connected_user_ids = []
    for request in connection_requests:
        if request.sender_id == user_id:
            connected_user_ids.append(request.receiver_id)
        else:
            connected_user_ids.append(request.sender_id)
    
    # Get the actual user objects
    connected_users = db.query(models.User).filter(
        models.User.id.in_(connected_user_ids)
    ).all()
    
    return connected_users

def get_user_sent_requests(db: Session, user_id: int):
    """Get all connection requests sent by a user"""
    return db.query(models.ConnectionRequest).filter(
        models.ConnectionRequest.sender_id == user_id
    ).all()

def get_user_received_requests(db: Session, user_id: int):
    """Get all connection requests received by a user"""
    return db.query(models.ConnectionRequest).filter(
        models.ConnectionRequest.receiver_id == user_id
    ).all()

# Connection request CRUD operations
def send_request(db: Session, sender_id: int, receiver_id: int):
    existing = db.query(models.ConnectionRequest).filter(
        models.ConnectionRequest.sender_id == sender_id,
        models.ConnectionRequest.receiver_id == receiver_id
    ).first()
    if existing:
        return existing
    
    req = models.ConnectionRequest(sender_id=sender_id, receiver_id=receiver_id)
    db.add(req)
    db.commit()
    db.refresh(req)
    return req

def update_request(db: Session, request_id: int, status: schemas.RequestStatus):
    req = db.query(models.ConnectionRequest).filter(models.ConnectionRequest.id == request_id).first()
    if req:
        req.status = status
        db.commit()
        db.refresh(req)
    return req
