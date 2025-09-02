from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from . import models, schemas
from typing import List

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
    connection_requests = db.query(models.ConnectionRequest).filter(
        and_(
            or_(
                models.ConnectionRequest.sender_id == user_id,
                models.ConnectionRequest.receiver_id == user_id
            ),
            models.ConnectionRequest.status == schemas.RequestStatus.accepted
        )
    ).all()
    
    connected_user_ids = []
    for request in connection_requests:
        if request.sender_id == user_id:
            connected_user_ids.append(request.receiver_id)
        else:
            connected_user_ids.append(request.sender_id)
    
    connected_users = db.query(models.User).filter(
        models.User.id.in_(connected_user_ids)
    ).all()
    
    return connected_users

def get_user_sent_requests(db: Session, user_id: int):
    return db.query(models.ConnectionRequest).filter(
        models.ConnectionRequest.sender_id == user_id
    ).all()

def get_user_received_requests(db: Session, user_id: int):
    return db.query(models.ConnectionRequest).filter(
        models.ConnectionRequest.receiver_id == user_id
    ).all()

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

def get_connection_request(db: Session, request_id: int):
    return db.query(models.ConnectionRequest).filter(models.ConnectionRequest.id == request_id).first()

def update_request(db: Session, request_id: int, status: schemas.RequestStatus):
    req = db.query(models.ConnectionRequest).filter(models.ConnectionRequest.id == request_id).first()
    if req:
        req.status = status
        db.commit()
        db.refresh(req)
    return req

def create_message(db: Session, sender_id: int, receiver_id: int, content: str):
    message = models.Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_chat_history(db: Session, user1_id: int, user2_id: int, skip: int = 0, limit: int = 50):
    messages = db.query(models.Message).filter(
        or_(
            and_(
                models.Message.sender_id == user1_id,
                models.Message.receiver_id == user2_id
            ),
            and_(
                models.Message.sender_id == user2_id,
                models.Message.receiver_id == user1_id
            )
        )
    ).order_by(models.Message.created_at.asc()).offset(skip).limit(limit).all()
    
    return messages

def check_users_connected(db: Session, user1_id: int, user2_id: int) -> bool:
    connection = db.query(models.ConnectionRequest).filter(
        or_(
            and_(
                models.ConnectionRequest.sender_id == user1_id,
                models.ConnectionRequest.receiver_id == user2_id,
                models.ConnectionRequest.status == schemas.RequestStatus.accepted
            ),
            and_(
                models.ConnectionRequest.sender_id == user2_id,
                models.ConnectionRequest.receiver_id == user1_id,
                models.ConnectionRequest.status == schemas.RequestStatus.accepted
            )
        )
    ).first()
    
    return connection is not None

def get_user_connected_users(db: Session, user_id: int):
    connected_users = get_user_connections(db, user_id)
    return connected_users

def create_notification(
    db: Session, 
    user_id: int, 
    notification_type: schemas.NotificationType, 
    title: str, 
    message: str,
    related_user_id: int = None,
    related_request_id: int = None,
    related_message_id: int = None
):
    db_notification = models.Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_user_id=related_user_id,
        related_request_id=related_request_id,
        related_message_id=related_message_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 50, unread_only: bool = False):
    query = db.query(models.Notification).filter(models.Notification.user_id == user_id)
    
    if unread_only:
        query = query.filter(models.Notification.is_read == False)
    
    query = query.order_by(models.Notification.created_at.desc())
    
    return query.offset(skip).limit(limit).all()

def get_notification_count(db: Session, user_id: int):
    total_count = db.query(models.Notification).filter(models.Notification.user_id == user_id).count()
    unread_count = db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.is_read == False
    ).count()
    
    return {"total_count": total_count, "unread_count": unread_count}

def mark_notifications_as_read(db: Session, user_id: int, notification_ids: List[int]):
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id,
        models.Notification.id.in_(notification_ids)
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return True

def mark_all_notifications_as_read(db: Session, user_id: int):
    db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).update({"is_read": True}, synchronize_session=False)
    db.commit()
    return True

def delete_notification(db: Session, notification_id: int, user_id: int):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()
    
    if notification:
        db.delete(notification)
        db.commit()
        return True
    return False
