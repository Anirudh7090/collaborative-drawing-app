# Real-Time Collaborative Drawing Application

A full-stack web application for real-time collaborative drawing with multiple users. Built with FastAPI (Python) backend and React frontend, featuring WebSocket-based real-time synchronization, user authentication, room management, and canvas persistence.

## ✨ Features

- **User Authentication**: Secure JWT-based registration and login system
- **Room Management**: Create, join, and manage collaborative drawing rooms with role-based permissions
- **Real-Time Collaboration**: Multi-user drawing with WebSocket connections and live cursor tracking
- **Drawing Tools**: Brush, eraser, shapes (rectangle, ellipse), text, and customizable colors/thickness
- **Collision Detection**: Visual feedback when multiple users draw in close proximity
- **Canvas Persistence**: Save and restore canvas states with snapshot versioning
- **Owner Permissions**: Room owners can clear canvas and remove members
- **Responsive UI**: Modern, intuitive interface with real-time member presence indicators

## 🏗️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **WebSockets**: Real-time bidirectional communication
- **SQLAlchemy**: ORM for PostgreSQL database
- **PostgreSQL**: Relational database for data persistence
- **JWT (python-jose)**: Secure token-based authentication
- **Passlib/Bcrypt**: Password hashing and verification

### Frontend
- **React**: Component-based UI library
- **HTML5 Canvas**: Native drawing functionality
- **WebSocket API**: Real-time communication with backend
- **Fetch API**: HTTP requests for REST endpoints

### Prerequisites

- **Python** 3.9 or higher
- **Node.js** v18 or higher
- **PostgreSQL** database (local or cloud)

### 1. Backend Setup

```


# Navigate to backend directory

cd backend/

# Install Python dependencies

pip install -r requirements.txt

# Create .env file from template

cp .env.example .env

# Edit .env with your PostgreSQL credentials

# DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE

# SECRET_KEY=your_secret_key_here

# Initialize database tables

python init_db.py

# Start FastAPI server

uvicorn main:app --reload

```

Backend will run at `http://localhost:8000`  
API documentation available at `http://localhost:8000/docs`

### 2. Frontend Setup

```


# Navigate to frontend directory

cd frontend/

# Install Node dependencies

npm install

# Start React development server

npm start

```

Frontend will run at `http://localhost:3000`

### 3. Usage

1. Open `http://localhost:3000` in your browser
2. Register a new account or login
3. Create a new room or join an existing room by ID
4. Start drawing collaboratively with other users!

## 📖 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[SETUP.md](docs/SETUP.md)**: Detailed installation and configuration guide
- **[API_DOC.md](docs/API_DOC.md)**: REST API endpoints documentation
- **[WEBSOCKET_SPEC.md](docs/WEBSOCKET_SPEC.md)**: WebSocket message protocol
- **[DB_DIAGRAM.md](docs/DB_DIAGRAM.md)**: Database schema and relationships
- **[USER_GUIDE.md](docs/USER_GUIDE.md)**: End-user instructions

## 🎨 Key Features Explained

### Real-Time Collaboration
Multiple users can draw simultaneously on the same canvas with live updates via WebSockets. Each user sees others' cursors with collision detection to prevent overlapping strokes.

### Role-Based Access
- **Room Owner**: Full control including canvas clearing and member removal
- **Room Member**: Drawing permissions and canvas viewing

### Canvas Persistence
- **Auto-save**: Canvas state automatically persists to database
- **Snapshots**: Create versioned snapshots for rollback/history
- **Load on Join**: Canvas state restored when joining rooms

### Drawing Tools
- **Brush**: Freehand drawing with customizable colors and thickness
- **Eraser**: Remove strokes with variable sizes
- **Shapes**: Rectangle and ellipse tools
- **Text**: Add text annotations
- **Undo**: Clear entire canvas (owner only)

## 🔒 Security

- **JWT Authentication**: All protected endpoints require valid tokens
- **Password Hashing**: Bcrypt hashing for secure password storage
- **WebSocket Authentication**: Token validation on connection
- **CORS Configuration**: Properly configured for frontend-backend communication

## 🛠️ Development

### Running Tests
```


# Backend tests (if available)

cd backend/
pytest tests/

# Frontend tests

cd frontend/
npm test

```

### Environment Variables

**Backend (.env)**:
```

DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DATABASE
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=60

```

## 📝 API Overview

### Authentication Endpoints
- `POST /register` - Create new user account
- `POST /login` - Authenticate and receive JWT token
- `GET /me` - Get current user info (protected)

### Room Endpoints
- `POST /rooms/create` - Create new room
- `POST /rooms/join` - Join existing room
- `GET /rooms/my` - List user's rooms
- `GET /rooms/{roomId}` - Get room details
- `POST /rooms/leave/{roomId}` - Leave room
- `DELETE /rooms/{roomId}` - Delete room (owner only)

### Canvas Endpoints
- `POST /canvas/save` - Save current canvas state
- `GET /canvas/load/{roomId}` - Load latest canvas state
- `POST /canvas/snapshot` - Create snapshot version
- `GET /canvas/snapshots/{roomId}` - List all snapshots
- `POST /canvas/clear/{roomId}` - Clear canvas (owner only)

### WebSocket
- `WS /ws/{roomId}?token=<JWT>` - Real-time drawing connection

For detailed API documentation, see [API_DOC.md](docs/API_DOC.md).

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Connection Errors
- Verify `.env` configuration matches your PostgreSQL credentials
- Ensure PostgreSQL server is running
- Check that both backend and frontend servers are running

### CORS Issues
- Verify FastAPI CORS middleware allows `http://localhost:3000`
- Check that frontend makes requests to correct backend URL

### WebSocket Issues
- Ensure JWT token is valid and not expired
- Check browser console for connection errors
- Verify WebSocket URL format: `ws://localhost:8000/ws/{roomId}?token=<JWT>`

For more troubleshooting tips, see [SETUP.md](docs/SETUP.md).

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI and React**


