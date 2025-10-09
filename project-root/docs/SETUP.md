# Setup and Installation Guide

Complete guide for setting up the Real-Time Collaborative Drawing Application locally.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Database Configuration](#database-configuration)
5. [Environment Variables](#environment-variables)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Ensure the following are installed on your system:

### Required Software

- **Python**: Version 3.9 or higher
  - Check: `python --version` or `python3 --version`
  - Download: [python.org](https://www.python.org/downloads/)

- **Node.js**: Version 18 or higher (includes npm)
  - Check: `node --version`
  - Download: [nodejs.org](https://nodejs.org/)

- **PostgreSQL**: Version 12 or higher
  - Check: `psql --version`
  - Download: [postgresql.org](https://www.postgresql.org/download/)
  - Alternative: Use cloud PostgreSQL (e.g., ElephantSQL, Supabase, Heroku Postgres)

- **Git**: For version control
  - Check: `git --version`
  - Download: [git-scm.com](https://git-scm.com/)

### Optional Tools

- **Postman**: For API testing ([download](https://www.postman.com/downloads/))
- **pgAdmin**: GUI for PostgreSQL management

---

## Backend Setup

### 1. Navigate to Backend Directory

```

cd backend/

```

### 2. Create Python Virtual Environment (Recommended)

```


# Create virtual environment

python -m venv venv

# Activate virtual environment

# On Windows:

venv\Scripts\activate

# On macOS/Linux:

source venv/bin/activate

```

### 3. Install Dependencies

```

pip install -r requirements.txt

```

**Dependencies include**:
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `websockets` - WebSocket support
- `sqlalchemy` - ORM for database
- `asyncpg` - PostgreSQL async driver
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT token handling

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```

cp .env.example .env

```

Edit `.env` with your configuration:

```


# Database Configuration

DATABASE_URL=postgresql://username:password@localhost:5432/canvas_db

# Security

SECRET_KEY=your_super_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (for development)

FRONTEND_URL=http://localhost:3000

```

**Important**: Replace `username`, `password`, and `canvas_db` with your PostgreSQL credentials.

### 5. Create Database

Connect to PostgreSQL and create the database:

```


# Connect to PostgreSQL

psql -U postgres

# Create database

CREATE DATABASE canvas_db;

# Exit PostgreSQL

\q

```

### 6. Initialize Database Tables

Run the initialization script to create all required tables:

```

python init_db.py

```

This creates the following tables:
- `users` - User accounts
- `rooms` - Drawing rooms
- `userrooms` - Room membership
- `canvassnapshots` - Canvas state versions

### 7. Start Backend Server

```

uvicorn main:app --reload

```

**Server will start at**: `http://localhost:8000`

**API Documentation available at**:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```

cd frontend/

```

### 2. Install Node Dependencies

```

npm install

```

**Dependencies include**:
- `react` - UI library
- `react-dom` - React rendering
- `react-scripts` - Build tooling

### 3. Configure API Endpoint (if needed)

If your backend runs on a different port, update API URLs in:
- `src/App.js`
- `src/RoomSelection.js`
- `src/DrawingCanvas.js`

Replace `http://localhost:8000` with your backend URL.

### 4. Start Development Server

```

npm start

```

**Application will open at**: `http://localhost:3000`

---

## Database Configuration

### PostgreSQL Connection String Format

```

postgresql://[username]:[password]@[host]:[port]/[database_name]

```

### Local PostgreSQL Example

```

DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/canvas_db

```

### Cloud PostgreSQL Example (ElephantSQL)

```

DATABASE_URL=postgresql://username:password@lucky.db.elephantsql.com:5432/database

```

### Verifying Database Connection

Test the connection in Python:

```

from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))
connection = engine.connect()
print("Database connected successfully!")
connection.close()

```

---

## Environment Variables

### Backend Environment Variables (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `SECRET_KEY` | JWT signing key (use strong random string) | `your_secret_key_here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `60` |

### Generating a Secure SECRET_KEY

```

import secrets
print(secrets.token_urlsafe(32))

```

Or use:
```

openssl rand -hex 32

```

---

## Running the Application

### Development Mode

1. **Start Backend** (Terminal 1):
```

cd backend/
source venv/bin/activate  \# On Windows: venv\Scripts\activate
uvicorn main:app --reload

```

2. **Start Frontend** (Terminal 2):
```

cd frontend/
npm start

```

3. **Open Browser**: Navigate to `http://localhost:3000`

### Production Mode

For production deployment:

**Backend**:
```

uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

```

**Frontend**:
```

npm run build

# Serve the build/ folder with a static file server

```

---

## Testing

### Backend Testing

If test files are available in `backend/tests/`:

```

cd backend/
pytest tests/

```

### API Testing with Postman

1. Import `docs/POSTMAN_COLLECTION.json` (if available)
2. Set environment variable `BASE_URL` to `http://localhost:8000`
3. Test endpoints:
   - Register user
   - Login (save token)
   - Create room
   - Join room
   - Save canvas

### Manual Testing

1. Register two users in separate browsers
2. Create a room with User 1
3. Join the room with User 2 using room ID
4. Draw simultaneously and observe real-time updates

---

## Troubleshooting

### Backend Issues

#### Database Connection Errors

**Error**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions**:
- Verify PostgreSQL is running: `pg_ctl status` or check system services
- Check `DATABASE_URL` in `.env` file
- Ensure database exists: `psql -U postgres -l`
- Test connection: `psql -U username -d canvas_db`

#### Import Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

#### Port Already in Use

**Error**: `Address already in use`

**Solutions**:
```


# Find process on port 8000

lsof -i :8000  \# On macOS/Linux
netstat -ano | findstr :8000  \# On Windows

# Kill the process

kill -9 <PID>  \# On macOS/Linux
taskkill /PID <PID> /F  \# On Windows

```

### Frontend Issues

#### CORS Errors

**Error**: `Access-Control-Allow-Origin header is missing`

**Solutions**:
- Verify FastAPI CORS middleware in `backend/main.py` allows `http://localhost:3000`
- Check browser console for exact origin
- Ensure both servers are running

#### WebSocket Connection Failed

**Error**: `WebSocket connection to 'ws://localhost:8000/ws/...' failed`

**Solutions**:
- Verify backend is running
- Check JWT token is valid (not expired)
- Ensure WebSocket URL format: `ws://localhost:8000/ws/{roomId}?token={JWT}`
- Check browser console for error details

#### Module Not Found

**Error**: `Module not found: Can't resolve './Component'`

**Solutions**:
```


# Clear node_modules and reinstall

rm -rf node_modules package-lock.json
npm install

```

### Database Issues

#### Tables Not Created

**Error**: `relation "users" does not exist`

**Solutions**:
- Run `python init_db.py` to create tables
- Check database connection
- Verify SQLAlchemy models are correct

#### Migration Issues

If you modify database models:

1. Drop existing tables (development only):
```

DROP TABLE canvassnapshots, userrooms, rooms, users CASCADE;

```

2. Re-run initialization:
```

python init_db.py

```

---

## Additional Configuration

### Running on Different Ports

#### Backend (Different Port)

```

uvicorn main:app --reload --port 8080

```

Update frontend API URLs to `http://localhost:8080`

#### Frontend (Different Port)

```

PORT=3001 npm start

```

Update backend CORS to allow `http://localhost:3001`

### Enabling HTTPS (Production)

Use a reverse proxy like **Nginx** or **Caddy** with SSL certificates:

```

server {
listen 443 ssl;
server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    }

```

---

## Next Steps

After successful setup:

1. Read [USER_GUIDE.md](./USER_GUIDE.md) for usage instructions
2. Review [API_DOC.md](./API_DOC.md) for API reference
3. Check [WEBSOCKET_SPEC.md](./WEBSOCKET_SPEC.md) for real-time protocol details
4. Explore [DB_DIAGRAM.md](./DB_DIAGRAM.md) for database schema

---

## Support

If issues persist:
- Check all logs in terminal/console
- Verify all prerequisites are correctly installed
- Review error messages carefully
- Open an issue on GitHub with detailed error information

**Happy Coding!** 🚀

