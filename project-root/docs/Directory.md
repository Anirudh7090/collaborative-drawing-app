project-root/
├── backend/ # FastAPI backend
│ ├── app/
│ │ ├── models/
│ │ │ ├── db.py # Database models (User, Room, CanvasSnapshot)
│ │ │ └── users.py # User model
│ │ └── routers/
│ │ ├── auth.py # Authentication endpoints
│ │ ├── rooms.py # Room management endpoints
│ │ ├── drawings.py # Canvas save/load/snapshot endpoints
│ │ ├── websockets.py # WebSocket connection handler
│ │ └── home.py # Root endpoint
│ ├── main.py # FastAPI app entry point
│ ├── init_db.py # Database initialization script
│ ├── requirements.txt # Python dependencies
│ └── .env.example # Environment variables template
├── frontend/ # React frontend
│ ├── src/
│ │ ├── App.js # Main app component with routing logic
│ │ ├── Login.js # Login form component
│ │ ├── Register.js # Registration form component
│ │ ├── RoomSelection.js # Room management interface
│ │ ├── DrawingCanvas.js # Collaborative canvas component
│ │ ├── App.css # Global styles
│ │ ├── index.js # React entry point
│ │ └── index.css # Base styles
│ └── package.json # Node dependencies
└── docs/ # Documentation
├── API_DOC.md # API endpoints reference
├── DB_DIAGRAM.md # Database schema
├── SETUP.md # Installation guide
├── USER_GUIDE.md # User manual
└── WEBSOCKET_SPEC.md # WebSocket protocol specification