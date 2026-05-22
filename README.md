# 🎧 SupportDesk — Customer Support & Ticketing Platform

A production-ready multi-tenant customer support system built 
with FastAPI and React.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue)
![Tests](https://img.shields.io/badge/Tests-22%20passing-brightgreen)

---

## 🚀 Tech Stack

### Backend
| Tool | Purpose |
|------|---------|
| FastAPI | Python web framework |
| PostgreSQL | Relational database |
| SQLModel | ORM (SQLAlchemy + Pydantic) |
| Alembic | Database migrations |
| JWT | Authentication tokens |
| WebSockets | Real-time chat |
| Passlib/Bcrypt | Password hashing |
| Pytest | API testing |

### Frontend
| Tool | Purpose |
|------|---------|
| React + Vite | Frontend framework |
| Tailwind CSS | Utility-first styling |
| React Router | Page navigation |
| Axios | HTTP client |
| WebSocket API | Real-time chat |

---

## 🏗️ Architecture

support-platform/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── security.py      # JWT + password hashing
│   │   │   └── dependencies.py  # Route protection
│   │   ├── models/
│   │   │   ├── organization.py  # Tenant model
│   │   │   ├── user.py          # User model
│   │   │   ├── ticket.py        # Ticket model
│   │   │   ├── message.py       # Chat message model
│   │   │   └── activity_log.py  # Audit log model
│   │   ├── routers/
│   │   │   ├── auth.py          # Auth endpoints
│   │   │   ├── organizations.py # Org endpoints
│   │   │   ├── users.py         # User endpoints
│   │   │   ├── tickets.py       # Ticket endpoints
│   │   │   └── messages.py      # Chat endpoints
│   │   ├── services/
│   │   │   ├── auth_service.py  # Auth logic
│   │   │   ├── ticket_service.py# Ticket logic
│   │   │   └── message_service.py# Chat logic
│   │   └── websockets/
│   │       └── chat.py          # WebSocket manager
│   ├── tests/
│   │   ├── test_auth.py         # Auth tests
│   │   ├── test_tickets.py      # Ticket tests
│   │   ├── test_roles.py        # Role tests
│   │   └── test_chat.py         # Chat tests
│   ├── alembic/                 # DB migrations
│   ├── .env.example
│   └── requirements.txt
└── frontend/
├── src/
│   ├── context/
│   │   └── AuthContext.jsx  # Global auth state
│   ├── pages/
│   │   ├── admin/
│   │   │   └── AdminDashboard.jsx
│   │   ├── agent/
│   │   │   ├── AgentDashboard.jsx
│   │   │   └── AgentChat.jsx
│   │   ├── customer/
│   │   │   ├── CustomerDashboard.jsx
│   │   │   └── CustomerChat.jsx
│   │   ├── shared/
│   │   │   └── Navbar.jsx
│   │   ├── Login.jsx
│   │   └── Register.jsx
│   └── services/
│       └── api.js           # Axios instance
└── .env.example

---

## 👥 System Roles

| Role | Permissions |
|------|------------|
| **Admin** | View all tickets, assign agents, monitor stats, close tickets |
| **Agent** | View assigned tickets, chat with customers, update status |
| **Customer** | Create tickets, chat with agents, track status |

---

## 🎫 Ticket Lifecycle

Customer creates ticket
│
▼
[OPEN] ──────────────────── Auto-assigned to agent
│                        Auto-response sent
│ Admin assigns agent
▼
[IN_PROGRESS] ──────────────── Agent starts working
│
│ Agent resolves
▼
[RESOLVED] ───────────────── Issue fixed
│
│ Admin closes
▼
[CLOSED] ────────────────── Ticket archived
❌ Cannot skip steps
❌ Cannot go backwards

---

## 💬 WebSocket Implementation

Real-time chat uses WebSockets with a ConnectionManager:

```python
# Connect to ticket chat room
ws://localhost:8000/ws/{ticket_id}?token=YOUR_JWT_TOKEN

# Send message
ws.send(JSON.stringify({ content: "Hello!" }))

# Receive message
{
  "type": "message",
  "id": 1,
  "ticket_id": 1,
  "sender_id": 2,
  "sender_name": "John Customer",
  "content": "Hello!",
  "created_at": "2024-01-01T10:00:00"
}
```

### How It Works:
1. User connects with JWT token
2. Token verified → user added to ticket's chat room
3. User sends message → saved to DB
4. Message broadcast to ALL users in same ticket room
5. User disconnects → removed from room

---

## ⚙️ Automation Features

| Feature | Description |
|---------|-------------|
| **Auto-assign** | New tickets assigned to agent with fewest active tickets |
| **Auto-response** | Customer gets instant confirmation on ticket creation |
| **Status validation** | Enforces open→in_progress→resolved→closed flow |
| **Activity logging** | Every action logged with timestamp and user |

---

## 🔐 Security Features

- JWT tokens with configurable expiry
- Bcrypt password hashing
- Role-based access control (RBAC)
- Multi-tenant data isolation
- CORS configuration
- Protected WebSocket connections

---

## 📦 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 13+
- Git

---

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/support-platform.git
cd support-platform
```

---

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your database credentials

# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE support_platform;"

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start development server
npm run dev
```

Frontend: `http://localhost:5173`

---

### 4. Run Tests
```bash
cd backend
pytest tests/ -v
# 22 tests should pass
```

---

## 🧪 Test Credentials

Register these users after setup:

| Role | Email | Password | Notes |
|------|-------|----------|-------|
| Admin | admin@test.com | admin123 | Create with organization_name |
| Customer | customer@test.com | customer123 | Join with organization_id |
| Agent | agent@test.com | agent123 | Created by admin via POST /users/agents |

---

## 📊 API Reference

### Authentication

POST /auth/register     Register new user
POST /auth/login        Login → returns JWT
GET  /auth/me           Get current user

### Organizations
GET  /organizations/              List all orgs
POST /organizations/              Create org (admin)
GET  /organizations/{id}          Get org by ID
GET  /organizations/{id}/members  Get org members

### Tickets
POST   /tickets/                Create ticket
GET    /tickets/                List tickets (role-based)
GET    /tickets/dashboard       Get statistics
GET    /tickets/{id}            Get single ticket
PATCH  /tickets/{id}            Update ticket
POST   /tickets/{id}/assign     Assign to agent (admin)
PATCH  /tickets/{id}/status     Update status
GET    /tickets/{id}/activity   Get audit log

### Users
GET    /users/agents     List agents in org
POST   /users/agents     Create agent (admin only)
GET    /users/{id}       Get user by ID
PATCH  /users/{id}       Update user
DELETE /users/{id}       Deactivate user (admin)

### Chat
GET /tickets/{id}/messages    Get chat history
POST /tickets/{id}/messages   Send message (HTTP)
WS  /ws/{ticket_id}?token=   WebSocket real-time chat

---

## 🧪 Testing Coverage
test_auth.py    (7 tests)  — Registration, login, JWT, protection
test_tickets.py (7 tests)  — CRUD, assignment, transitions, stats
test_roles.py   (4 tests)  — RBAC, org isolation, access control
test_chat.py    (4 tests)  — Messages, auto-response, access control
Total: 22 tests — All Passing ✅


---

## 🔥 Features Implemented

### Core Requirements
- ✅ Multi-tenant architecture
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Ticket lifecycle management
- ✅ Real-time WebSocket chat
- ✅ Status transition validation
- ✅ Role-based dashboards
- ✅ Activity logging
- ✅ Database migrations

### Bonus Features
- ✅ Ticket priority system
- ✅ Auto-assign tickets to agents
- ✅ Auto-response on ticket creation
- ✅ Dashboard statistics
- ✅ Filter tickets by status
- ✅ Comprehensive API testing