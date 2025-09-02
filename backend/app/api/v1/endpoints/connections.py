from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app import crud, schemas
from app.websocket_manager import manager
import asyncio

router = APIRouter(prefix="/connections", tags=["Connections"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/send", response_model=schemas.ConnectionRequestOut)
def send_request(sender_id: int, req: schemas.ConnectionRequestCreate, db: Session = Depends(get_db)):
    if sender_id == req.receiver_id:
        raise HTTPException(status_code=400, detail="You cannot send a request to yourself")
    
    connection_request = crud.send_request(db, sender_id, req.receiver_id)
    
    sender = crud.get_user(db, sender_id)
    
    notification = crud.create_notification(
        db=db,
        user_id=req.receiver_id,
        notification_type=schemas.NotificationType.connection_request,
        title="New Connection Request",
        message=f"{sender.username} wants to connect with you",
        related_user_id=sender_id,
        related_request_id=connection_request.id
    )
    
    if manager.is_user_online(req.receiver_id):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(manager.send_notification(req.receiver_id, {
                "notification_id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "related_user_id": sender_id,
                "related_username": sender.username
            }))
        except:
            pass  # If no event loop, notification is still saved in DB
    
    return connection_request

@router.post("/{request_id}/accept", response_model=schemas.ConnectionRequestOut)
def accept_request(request_id: int, db: Session = Depends(get_db)):
    request = crud.get_connection_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    updated = crud.update_request(db, request_id, schemas.RequestStatus.accepted)
    if not updated:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Get receiver info for notification
    receiver = crud.get_user(db, request.receiver_id)
    
    # Create notification for sender
    notification = crud.create_notification(
        db=db,
        user_id=request.sender_id,
        notification_type=schemas.NotificationType.connection_accepted,
        title="Connection Request Accepted",
        message=f"{receiver.username} accepted your connection request",
        related_user_id=request.receiver_id,
        related_request_id=request_id
    )
    
    # Send real-time notification if user is online
    if manager.is_user_online(request.sender_id):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(manager.send_notification(request.sender_id, {
                "notification_id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "related_user_id": request.receiver_id,
                "related_username": receiver.username
            }))
        except:
            pass
    
    return updated

@router.post("/{request_id}/reject", response_model=schemas.ConnectionRequestOut)
def reject_request(request_id: int, db: Session = Depends(get_db)):
    request = crud.get_connection_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Update the request
    updated = crud.update_request(db, request_id, schemas.RequestStatus.rejected)
    if not updated:
        raise HTTPException(status_code=404, detail="Request not found")
    
    receiver = crud.get_user(db, request.receiver_id)
    
    notification = crud.create_notification(
        db=db,
        user_id=request.sender_id,
        notification_type=schemas.NotificationType.connection_rejected,
        title="Connection Request Rejected",
        message=f"{receiver.username} declined your connection request",
        related_user_id=request.receiver_id,
        related_request_id=request_id
    )
    
    # Send real-time notification if user is online
    if manager.is_user_online(request.sender_id):
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(manager.send_notification(request.sender_id, {
                "notification_id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "related_user_id": request.receiver_id,
                "related_username": receiver.username
            }))
        except:
            pass
    
    return updated
