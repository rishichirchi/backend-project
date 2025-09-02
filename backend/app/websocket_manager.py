from fastapi import WebSocket
from typing import Dict, List
import json
import datetime
from app import schemas


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User {user_id} connected to WebSocket")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_text(message)
                return True
            except Exception as e:
                print(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
                return False
        return False

    async def send_chat_message(self, sender_id: int, receiver_id: int, content: str, message_id: int):
        message_data = {
            "type": "message",
            "message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        
        message_json = json.dumps(message_data)
        
        receiver_sent = await self.send_personal_message(message_json, receiver_id)
        
        sender_sent = await self.send_personal_message(message_json, sender_id)
        
        confirmation_data = {
            "type": "message_sent",
            "message_id": message_id,
            "status": "delivered" if receiver_sent else "offline"
        }
        await self.send_personal_message(json.dumps(confirmation_data), sender_id)

    async def send_notification(self, user_id: int, notification_data: dict):
        notification_json = json.dumps({
            "type": "notification",
            **notification_data
        })
        
        return await self.send_personal_message(notification_json, user_id)

    def is_user_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    def get_online_users(self) -> List[int]:
        return list(self.active_connections.keys())


manager = ConnectionManager()
