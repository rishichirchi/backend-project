from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app import crud, schemas
from app.websocket_manager import manager
from typing import List
import json
import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    db = SessionLocal()
    try:
        print(f"WebSocket connection attempt for user {user_id}")
        user = crud.get_user(db, user_id)
        if not user:
            print(f"User {user_id} not found, closing connection")
            await websocket.close(code=4004, reason="User not found")
            return

        print(f"Accepting WebSocket connection for user {user_id}")
        await manager.connect(websocket, user_id)
        print(f"User {user_id} connected successfully")
        
        try:
            while True:
                print(f"Waiting for message from user {user_id}")
                data = await websocket.receive_text()
                print(f"Received message from user {user_id}: {data}")
                message_data = json.loads(data)
                
                if "receiver_id" not in message_data or "content" not in message_data:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid message format. Required fields: receiver_id, content"
                    }))
                    continue
                
                receiver_id = message_data["receiver_id"]
                content = message_data["content"].strip()
                
                if not content:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Message content cannot be empty"
                    }))
                    continue
                
                if not crud.check_users_connected(db, user_id, receiver_id):
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "You can only chat with connected users"
                    }))
                    continue
                
                message = crud.create_message(db, user_id, receiver_id, content)
                print(f"Message saved to DB with ID: {message.id}")
                
                sender = crud.get_user(db, user_id)
                if not manager.is_user_online(receiver_id):
                    notification = crud.create_notification(
                        db=db,
                        user_id=receiver_id,
                        notification_type=schemas.NotificationType.new_message,
                        title=f"New message from {sender.username}",
                        message=content[:50] + "..." if len(content) > 50 else content,
                        related_user_id=user_id,
                        related_message_id=message.id
                    )
                
                print(f"Sending WebSocket message from {user_id} to {receiver_id}")
                await manager.send_chat_message(user_id, receiver_id, content, message.id)
                print(f"WebSocket message sent successfully")
                
        except WebSocketDisconnect:
            print(f"User {user_id} disconnected normally")
            manager.disconnect(user_id)
            
    except Exception as e:
        print(f"WebSocket error for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        manager.disconnect(user_id)
    finally:
        print(f"Closing database connection for user {user_id}")
        db.close()

@router.get("/history/{other_user_id}", response_model=schemas.ChatHistoryResponse)
def get_chat_history(
    other_user_id: int,
    current_user_id: int = Query(..., description="Current user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Messages per page"),
    db: Session = Depends(get_db)
):
    
    current_user = crud.get_user(db, current_user_id)
    other_user = crud.get_user(db, other_user_id)
    
    if not current_user:
        raise HTTPException(status_code=404, detail="Current user not found")
    if not other_user:
        raise HTTPException(status_code=404, detail="Other user not found")
    
    if not crud.check_users_connected(db, current_user_id, other_user_id):
        raise HTTPException(status_code=403, detail="You can only view chat history with connected users")
    
    skip = (page - 1) * limit
    
    messages = crud.get_chat_history(db, current_user_id, other_user_id, skip=skip, limit=limit)
    
    all_messages = crud.get_chat_history(db, current_user_id, other_user_id, skip=0, limit=10000)
    total_count = len(all_messages)
    
    return schemas.ChatHistoryResponse(
        messages=messages,
        total_count=total_count,
        page=page,
        limit=limit
    )

@router.get("/connected-users/{user_id}", response_model=List[schemas.UserOut])
def get_connected_users_for_chat(user_id: int, db: Session = Depends(get_db)):
    
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    connected_users = crud.get_user_connected_users(db, user_id)
    return connected_users

@router.post("/send", response_model=schemas.MessageOut)
def send_message_http(
    message_data: schemas.MessageCreate,
    sender_id: int = Query(..., description="Sender user ID"),
    db: Session = Depends(get_db)
):
    
    sender = crud.get_user(db, sender_id)
    receiver = crud.get_user(db, message_data.receiver_id)
    
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    if not crud.check_users_connected(db, sender_id, message_data.receiver_id):
        raise HTTPException(status_code=403, detail="You can only send messages to connected users")
    
    message = crud.create_message(db, sender_id, message_data.receiver_id, message_data.content)
    
    if manager.is_user_online(message_data.receiver_id):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(manager.send_chat_message(
                sender_id, message_data.receiver_id, message_data.content, message.id
            ))
        except:
            pass
    
    return message
