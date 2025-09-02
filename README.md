# Becommune - Backend Assignment

A full-stack application implementing a connection request system and real-time chat functionality using FastAPI and React.

## 🚀 Features

### Task 1 - API & Database Design
- **User Management**: Create and manage user profiles
- **Connection Requests**: Send, accept, and reject connection requests
- **Status Tracking**: Track pending, accepted, and rejected requests
- **Database Schema**: Complete SQLAlchemy models with proper relationships
<img width="1920" height="1200" alt="Screenshot from 2025-09-02 17-24-03" src="https://github.com/user-attachments/assets/cf519adb-ddf6-4b2a-93ea-32ee6bde1bbe" />

### Task 2 - Real-time Chat
- **WebSocket Integration**: Real-time bidirectional messaging
- **Message Persistence**: Chat history stored in database
- **Connection Validation**: Only connected users can chat
- **Live Status**: Real-time connection status indicators
<img width="1926" height="1153" alt="Screenshot from 2025-09-02 17-23-43" src="https://github.com/user-attachments/assets/83780077-8f2b-4684-a3e2-77f4b9959fcb" />


### Bonus Features
- **Notification System**: Real-time notifications for requests and messages
- **React Frontend**: Complete testing interface
- **Professional UI**: Modern design with responsive layout
<img width="1920" height="1048" alt="Screenshot from 2025-09-02 17-23-09" src="https://github.com/user-attachments/assets/19f1cb25-9dfc-420d-ad68-f8be98541476" />


## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM with PostgreSQL support
- **Alembic**: Database migration management
- **WebSockets**: Real-time communication
- **Pydantic v2**: Request/response validation

### Frontend
- **React 18**: Modern React with hooks
- **Axios**: HTTP client for API requests
- **WebSocket API**: Native WebSocket integration
- **CSS3**: Responsive styling

### Database
- **PostgreSQL**: Production database
- **SQLite**: Development fallback

## 📁 Project Structure

```
bcommune/
├── app/
│   ├── api/v1/endpoints/        # API route handlers
│   │   ├── users.py            # User management
│   │   ├── connections.py      # Connection requests
│   │   ├── chat.py            # Chat endpoints
│   │   └── notifications.py   # Notification system
│   ├── core/
│   │   └── database.py        # Database configuration
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas
│   ├── crud.py                # Database operations
│   ├── websocket_manager.py   # WebSocket management
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
├── frontend/                  # React application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
└── README.md               # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+ (for frontend)
- PostgreSQL (optional, SQLite works for development)

### Backend Setup

1. **Clone and navigate to project**
   ```bash
   git clone <repository-url>
   cd bcommune
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your database URL if using PostgreSQL
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the backend server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 API Documentation

### Interactive Testing
Visit **http://localhost:8000/docs** for comprehensive API testing with Swagger UI.

### Key Endpoints

#### Users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - List all users
- `GET /api/v1/users/{user_id}` - Get user details

#### Connection Requests
- `POST /api/v1/connections/send` - Send connection request
- `POST /api/v1/connections/{request_id}/accept` - Accept request
- `POST /api/v1/connections/{request_id}/reject` - Reject request

#### Chat
- `GET /api/v1/chat/{user1_id}/{user2_id}/history` - Get chat history
- `WebSocket /api/v1/chat/ws/{user_id}` - Real-time messaging

#### Notifications
- `GET /api/v1/notifications/{user_id}` - Get user notifications
- `POST /api/v1/notifications/{notification_id}/read` - Mark as read

## 🧪 Testing

### API Testing
1. **Swagger UI**: http://localhost:8000/docs
2. **Frontend Interface**: Complete testing workflow
3. **Manual Testing**: Use curl or Postman

### Test Workflow
1. Create users via `/api/v1/users/`
2. Send connection requests via `/api/v1/connections/send`
3. Accept/reject requests
4. Test real-time chat between connected users
5. Verify notifications system

## 🐳 Docker Deployment

### Build and run with Docker
```bash
# Build the image
docker build -t bcommune-backend .

# Run the container
docker run -p 8000:8000 bcommune-backend
```

### Docker Compose (with database)
```bash
docker-compose up -d
```

## 🌐 Deployment

### Railway (Recommended)
1. Connect your GitHub repository to Railway
2. Add PostgreSQL database service
3. Set environment variables
4. Deploy automatically on push

### AWS ECS
1. Build and push Docker image to ECR
2. Create ECS task definition
3. Deploy to ECS cluster

### Manual Deployment
Files included for various platforms:
- `railway.json` - Railway configuration
- `Dockerfile` - Container setup
- `docker-compose.yml` - Multi-service setup

## 📊 Database Schema

### Core Models
- **User**: User profiles and authentication
- **ConnectionRequest**: Friend/connection requests
- **Message**: Chat messages between users
- **Notification**: System notifications

### Relationships
- Users can send/receive multiple connection requests
- Connected users can exchange messages
- Users receive notifications for requests and messages

## 🔧 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bcommune
# Or for SQLite: sqlite:///./bcommune.db

# Application
SECRET_KEY=your-secret-key-here
DEBUG=True

# CORS (for production)
FRONTEND_URL=https://your-frontend-domain.com
```


## 📝 License

This project is licensed under the MIT License.

## 📧 Contact

For questions or support, please contact [your-email@example.com]

---

## 🎯 Assignment Notes

I have built a full-stack solution with both a backend and a frontend—so you can test everything end-to-end. Due to a bit of a time crunch, I couldn't deploy them live yet, but I will update both with proper deployments soon. Meanwhile, you can fully test all the APIs using the interactive Swagger docs at `/docs`. The React frontend is also ready and will make testing the workflows even easier once deployed!
