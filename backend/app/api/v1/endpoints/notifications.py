from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app import crud, schemas, models
from typing import List
import datetime

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=schemas.NotificationResponse)
def get_notifications(
    user_id: int = Query(..., description="User ID to get notifications for"),
    skip: int = Query(0, ge=0, description="Number of notifications to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to return"),
    unread_only: bool = Query(False, description="Return only unread notifications"),
    db: Session = Depends(get_db)
):
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    notifications = crud.get_user_notifications(db, user_id, skip, limit, unread_only)
    counts = crud.get_notification_count(db, user_id)
    
    enriched_notifications = []
    for notification in notifications:
        notification_dict = {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "related_user_id": notification.related_user_id,
            "related_request_id": notification.related_request_id,
            "related_message_id": notification.related_message_id,
            "related_user_username": None
        }
        
        if notification.related_user_id:
            related_user = crud.get_user(db, notification.related_user_id)
            if related_user:
                notification_dict["related_user_username"] = related_user.username
        
        enriched_notifications.append(schemas.NotificationWithDetails(**notification_dict))
    
    return schemas.NotificationResponse(
        notifications=enriched_notifications,
        total_count=counts["total_count"],
        unread_count=counts["unread_count"]
    )

@router.get("/count", response_model=schemas.NotificationCount)
def get_notification_count(
    user_id: int = Query(..., description="User ID to get notification count for"),
    db: Session = Depends(get_db)
):
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    counts = crud.get_notification_count(db, user_id)
    return schemas.NotificationCount(**counts)

@router.put("/mark-read")
def mark_notifications_read(
    mark_read_data: schemas.NotificationMarkRead,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = crud.mark_notifications_as_read(db, user_id, mark_read_data.notification_ids)
    
    if success:
        return {"message": f"Marked {len(mark_read_data.notification_ids)} notifications as read"}
    else:
        raise HTTPException(status_code=400, detail="Failed to mark notifications as read")

@router.put("/mark-all-read")
def mark_all_notifications_read(
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = crud.mark_all_notifications_as_read(db, user_id)
    
    if success:
        return {"message": "All notifications marked as read"}
    else:
        raise HTTPException(status_code=400, detail="Failed to mark notifications as read")

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    user_id: int = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = crud.delete_notification(db, notification_id, user_id)
    
    if success:
        return {"message": "Notification deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Notification not found")
