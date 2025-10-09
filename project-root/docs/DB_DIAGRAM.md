# Database Schema & Entity Relationship Diagram

This document describes the PostgreSQL database schema used by the Real-Time Collaborative Drawing Application.

## Overview

The application uses **PostgreSQL** with **SQLAlchemy ORM** for data persistence. The schema consists of four main entities that handle user authentication, room management, membership tracking, and canvas state persistence.

---

## Database Tables

### 1. User

Stores user account information and authentication credentials.

**Table Name**: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique user identifier |
| `email` | STRING (VARCHAR) | UNIQUE, NOT NULL | User email address (login username) |
| `hashed_password` | STRING (VARCHAR) | NOT NULL | Bcrypt hashed password |
| `full_name` | STRING (VARCHAR) | NULLABLE | User's full name (optional) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status (for soft deletion) |

**Indexes**:
- Primary key on `id`
- Unique index on `email`

**Relationships**:
- One user can **own many rooms** (`Room.owner_id`)
- One user can **join many rooms** (via `UserRoom`)
- One user can **create many canvas snapshots**

---

### 2. Room

Represents collaborative drawing rooms where users can work together.

**Table Name**: `rooms`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | STRING (VARCHAR) | PRIMARY KEY | Custom room ID (e.g., "room-abc123") |
| `name` | STRING (VARCHAR) | NOT NULL | Human-readable room name |
| `description` | TEXT | NULLABLE | Optional room description |
| `owner_id` | INTEGER | FOREIGN KEY → `users.id`, NOT NULL | User who created the room |
| `max_users` | INTEGER | DEFAULT 10 | Maximum users allowed in room |
| `created_at` | DATETIME (with timezone) | DEFAULT NOW() | Room creation timestamp |
| `is_active` | BOOLEAN | DEFAULT TRUE | Room status (for soft deletion) |

**Indexes**:
- Primary key on `id`
- Foreign key index on `owner_id`

**Relationships**:
- Room belongs to **one owner** (User)
- Room has **many members** (via `UserRoom`)
- Room has **many canvas snapshots**

**Business Logic**:
- Room ID is generated as UUID-based string (e.g., `room-{uuid4()[0:8]}`)
- Owner has full control (clear canvas, remove members, delete room)
- Members can draw and view but have limited permissions

---

### 3. UserRoom

Junction table that maps users to rooms and tracks membership details.

**Table Name**: `userrooms`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique membership record ID |
| `user_id` | INTEGER | FOREIGN KEY → `users.id`, NOT NULL | User in the room |
| `room_id` | STRING (VARCHAR) | FOREIGN KEY → `rooms.id`, NOT NULL | Room the user belongs to |
| `role` | ENUM | NOT NULL, DEFAULT 'MEMBER' | User role: 'OWNER' or 'MEMBER' |
| `joined_at` | DATETIME (with timezone) | DEFAULT NOW() | When user joined room |
| `is_active` | BOOLEAN | DEFAULT TRUE | Membership status (for leave/removal) |

**Indexes**:
- Primary key on `id`
- Foreign key indexes on `user_id` and `room_id`
- Composite unique constraint on (`user_id`, `room_id`, `is_active`)

**Enum Values**:
```

class UserRole(enum.Enum):
OWNER = "owner"    \# Room creator with full permissions
MEMBER = "member"  \# Regular participant

```

**Relationships**:
- Belongs to **one user**
- Belongs to **one room**

**Business Logic**:
- Room owner automatically gets `OWNER` role when room is created
- Members joining via `/rooms/join` get `MEMBER` role
- Soft deletion via `is_active = False` when user leaves or is removed

---

### 4. CanvasSnapshot

Stores serialized canvas state for persistence and version history.

**Table Name**: `canvassnapshots`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique snapshot ID |
| `room_id` | STRING (VARCHAR) | FOREIGN KEY → `rooms.id`, NOT NULL | Associated room |
| `state_json` | TEXT | NOT NULL | Full canvas state as JSON string |
| `created_at` | DATETIME (with timezone) | DEFAULT NOW() | Snapshot creation time |
| `creator_id` | INTEGER | FOREIGN KEY → `users.id`, NULLABLE | User who saved snapshot (optional) |

**Indexes**:
- Primary key on `id`
- Foreign key indexes on `room_id` and `creator_id`
- Index on `created_at` for efficient sorting

**Relationships**:
- Belongs to **one room**
- Created by **one user** (nullable for system-generated snapshots)

**Business Logic**:
- `state_json` contains array of drawing strokes/shapes in JSON format:
```

[
{"type": "brush", "fromX": 10, "fromY": 20, "toX": 15, "toY": 25, "color": "\#3182ce", "thickness": 4},
{"type": "rectangle", "fromX": 50, "fromY": 60, "toX": 100, "toY": 120, "color": "\#e53e3e", "thickness": 2}
]

```
- Latest snapshot is loaded when users join a room
- Snapshots enable version history and rollback functionality
- Owner clearing canvas creates a new snapshot with empty array

---

## Entity Relationship Diagram

### ASCII Diagram

```

┌──────────────┐
│     User     │
│──────────────│
│ id (PK)      │◄────────┐
│ email        │         │
│ hashed_pwd   │         │ Owner
│ full_name    │         │
│ is_active    │         │
└──────┬───────┘         │
│                 │
│ Members         │
│                 │
▼                 │
┌──────────────┐         │
│   UserRoom   │         │
│──────────────│         │
│ id (PK)      │         │
│ user_id (FK) │         │
│ room_id (FK) │─────┐   │
│ role (ENUM)  │     │   │
│ joined_at    │     │   │
│ is_active    │     │   │
└──────────────┘     │   │
▼   │
┌──────────────────┐
│       Room       │
│──────────────────│
│ id (PK)          │──┐
│ name             │  │
│ description      │  │
│ owner_id (FK)    │──┘
│ max_users        │
│ created_at       │
│ is_active        │
└────────┬─────────┘
│
│ Snapshots
│
▼
┌──────────────────┐
│ CanvasSnapshot   │
│──────────────────│
│ id (PK)          │
│ room_id (FK)     │
│ state_json       │
│ created_at       │
│ creator_id (FK)  │
└──────────────────┘

```

### Relationship Summary

**One-to-Many Relationships**:
1. **User → Room** (as owner)
   - One user can own multiple rooms
   - Each room has exactly one owner
   - Foreign key: `Room.owner_id` → `User.id`

2. **Room → CanvasSnapshot**
   - One room can have multiple canvas snapshots (version history)
   - Each snapshot belongs to one room
   - Foreign key: `CanvasSnapshot.room_id` → `Room.id`

3. **User → CanvasSnapshot** (as creator)
   - One user can create multiple snapshots
   - Each snapshot optionally references its creator
   - Foreign key: `CanvasSnapshot.creator_id` → `User.id` (nullable)

**Many-to-Many Relationship**:
1. **User ↔ Room** (via UserRoom)
   - Users can join multiple rooms
   - Rooms can have multiple users
   - Junction table: `UserRoom` with additional metadata (role, joined_at)

---

## Database Constraints

### Foreign Key Constraints

All foreign keys enforce referential integrity:

```

-- Room ownership
ALTER TABLE rooms
ADD CONSTRAINT fk_room_owner
FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE;

-- UserRoom memberships
ALTER TABLE userrooms
ADD CONSTRAINT fk_userroom_user
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE userrooms
ADD CONSTRAINT fk_userroom_room
FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE;

-- Canvas snapshots
ALTER TABLE canvassnapshots
ADD CONSTRAINT fk_snapshot_room
FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE;

ALTER TABLE canvassnapshots
ADD CONSTRAINT fk_snapshot_creator
FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE SET NULL;

```

### Unique Constraints

```

-- Ensure unique email addresses
ALTER TABLE users ADD CONSTRAINT unique_user_email UNIQUE (email);

-- Prevent duplicate active memberships
ALTER TABLE userrooms ADD CONSTRAINT unique_active_membership
UNIQUE (user_id, room_id, is_active);

```

---

## SQLAlchemy Models

The database schema is defined in `backend/app/models/db.py` using SQLAlchemy ORM:

```

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

# User Role Enum

class UserRole(enum.Enum):
OWNER = "owner"
MEMBER = "member"

# User Model

class User(Base):
__tablename__ = "users"
id = Column(Integer, primary_key=True, index=True)
email = Column(String, unique=True, nullable=False)
hashed_password = Column(String, nullable=False)
full_name = Column(String, nullable=True)
is_active = Column(Boolean, default=True)

    # Relationships
    owned_rooms = relationship("Room", back_populates="owner")
    room_memberships = relationship("UserRoom", back_populates="user")
    
# Room Model

class Room(Base):
__tablename__ = "rooms"
id = Column(String, primary_key=True, index=True)
name = Column(String, nullable=False)
description = Column(Text, nullable=True)
owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
max_users = Column(Integer, default=10)
created_at = Column(DateTime(timezone=True), server_default=func.now())
is_active = Column(Boolean, default=True)

    # Relationships
    owner = relationship("User", back_populates="owned_rooms")
    members = relationship("UserRoom", back_populates="room")
    snapshots = relationship("CanvasSnapshot", back_populates="room")
    
# UserRoom Junction Model

class UserRoom(Base):
__tablename__ = "userrooms"
id = Column(Integer, primary_key=True, index=True)
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
room_id = Column(String, ForeignKey("rooms.id"), nullable=False)
role = Column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
joined_at = Column(DateTime(timezone=True), server_default=func.now())
is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="room_memberships")
    room = relationship("Room", back_populates="members")
    
# Canvas Snapshot Model

class CanvasSnapshot(Base):
__tablename__ = "canvassnapshots"
id = Column(Integer, primary_key=True, index=True)
room_id = Column(String, ForeignKey("rooms.id"), nullable=False, index=True)
state_json = Column(Text, nullable=False)
created_at = Column(DateTime(timezone=True), server_default=func.now())
creator_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    room = relationship("Room", back_populates="snapshots")
    creator = relationship("User")
    ```

---

## Database Initialization

To create all tables, run the initialization script:

```

cd backend/
python init_db.py

```

**Script contents** (`init_db.py`):
```

from app.models.db import Base, engine

# Create all tables

Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")

```

---

## Data Flow Examples

### User Registration Flow

1. User submits registration form with email and password
2. Backend hashes password using bcrypt
3. New record inserted into `users` table
4. JWT token generated and returned

### Room Creation Flow

1. Authenticated user sends room creation request
2. New record inserted into `rooms` table with generated UUID ID
3. User automatically added to `userrooms` table with `OWNER` role
4. Empty canvas snapshot created in `canvassnapshots` table

### Drawing Collaboration Flow

1. User joins room via WebSocket with JWT token
2. Latest canvas snapshot loaded from `canvassnapshots` table
3. User draws → stroke broadcast via WebSocket to all room members
4. Periodically, canvas state saved to `canvassnapshots` table
5. On room exit, final state persisted for next session

---

## Performance Considerations

### Indexes

The following indexes optimize query performance:

- **Primary keys**: All tables have indexed primary keys
- **Foreign keys**: Automatic indexes on all foreign key columns
- **Email lookup**: Unique index on `users.email` for fast authentication
- **Room queries**: Index on `rooms.owner_id` and `rooms.is_active`
- **Snapshot retrieval**: Index on `canvassnapshots.room_id` and `created_at` for latest state queries

### Query Optimization

**Most Frequent Queries**:

1. **Load Canvas State** (optimized):
```

SELECT state_json FROM canvassnapshots
WHERE room_id = ?
ORDER BY created_at DESC
LIMIT 1;

```

2. **List User Rooms** (optimized):
```

SELECT r.* FROM rooms r
JOIN userrooms ur ON r.id = ur.room_id
WHERE ur.user_id = ? AND ur.is_active = true;

```

3. **Check Room Membership** (optimized):
```

SELECT role FROM userrooms
WHERE user_id = ? AND room_id = ? AND is_active = true;

```

---

## Backup and Migration

### Database Backup

```


# Backup entire database

pg_dump -U username -d canvas_db > backup.sql

# Restore from backup

psql -U username -d canvas_db < backup.sql

```

### Schema Migrations

For production, consider using **Alembic** for database migrations:

```

pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

```

---

## Security Considerations

1. **Password Storage**: Never store plain text passwords; always use bcrypt hashing
2. **SQL Injection**: SQLAlchemy ORM prevents SQL injection via parameterized queries
3. **Soft Deletion**: Use `is_active` flags instead of hard deletes to maintain data integrity
4. **Foreign Key Constraints**: Enforce referential integrity to prevent orphaned records

---

## Summary

The database schema efficiently supports:
- **User authentication** with secure password storage
- **Multi-user room management** with role-based access control
- **Real-time collaboration** with WebSocket state synchronization
- **Canvas persistence** with version history and rollback capabilities

All relationships are properly constrained with foreign keys, and indexes ensure optimal query performance for the most common operations.

---

For implementation details, see:
- [API_DOC.md](./API_DOC.md) - REST endpoint specifications
- [WEBSOCKET_SPEC.md](./WEBSOCKET_SPEC.md) - Real-time protocol
- [SETUP.md](./SETUP.md) - Database configuration guide
```



