# BCommune Test Interface

A clean React UI to test both Task 1 (Connection Requests) and Task 2 (Real-time Chat).

## 🚀 Quick Setup

### 1. Install Node.js dependencies
```bash
cd frontend
npm install
```

### 2. Start the React app
```bash
npm start
```
The frontend will be available at http://localhost:3000

### 3. Start the FastAPI backend (in another terminal)
```bash
cd ..
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing Guide

### Task 1 - Connection Requests Testing:

1. **Create Users**: 
   - Go to "User Management" tab
   - Create 2-3 users (e.g., "alice", "bob", "charlie")

2. **Select Current User**: 
   - Use the dropdown in header to select current user

3. **Send Connection Requests**: 
   - Go to "Connections" tab
   - Select a user from dropdown and click "Send Request"

4. **Accept/Reject Requests**: 
   - Switch to the other user in header dropdown
   - Go to "Connections" tab
   - Accept or reject received requests

### Task 2 - Real-time Chat Testing:

1. **Prerequisites**: 
   - Must have accepted connections between users

2. **Start Chat**: 
   - Select a user as current user
   - Go to "Chat" tab
   - Click on a connected user in sidebar

3. **Test WebSocket**: 
   - Type a message and click "Send (WS)"
   - Open multiple browser tabs/windows with different users
   - See real-time message delivery

4. **Test HTTP Fallback**: 
   - Use "Send (HTTP)" button as alternative

5. **Test Chat History**: 
   - Messages persist in database
   - Click "Refresh History" to reload

## ✨ Features

### Task 1 Features:
- ✅ Create users
- ✅ Send connection requests  
- ✅ Accept/reject requests
- ✅ View connections and request status
- ✅ Real-time status updates

### Task 2 Features:
- ✅ Real-time WebSocket chat
- ✅ Chat only between connected users
- ✅ Message persistence 
- ✅ Chat history loading
- ✅ HTTP fallback for messages
- ✅ Connection status indicators
- ✅ Multiple chat windows support

## 🔧 UI Components

1. **User Management**: Create and view users
2. **Connection Manager**: Send/accept/reject connection requests
3. **Chat Interface**: Real-time messaging with WebSocket support

## 📱 Responsive Design

- Clean, modern interface
- Mobile-friendly layout
- Real-time status indicators
- Error handling and user feedback

## 🌐 API Endpoints Tested

### Task 1:
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/` - List users  
- `POST /api/v1/connections/send` - Send request
- `POST /api/v1/connections/{id}/accept` - Accept request
- `POST /api/v1/connections/{id}/reject` - Reject request

### Task 2:
- `ws://localhost:8000/api/v1/chat/ws/{user_id}` - WebSocket chat
- `GET /api/v1/chat/history/{user_id}` - Chat history
- `POST /api/v1/chat/send` - Send message (HTTP)

This React interface provides a complete testing environment for both tasks with a professional UI! 🎉
