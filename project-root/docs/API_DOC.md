# API Documentation

Complete reference for all REST API endpoints in the Real-Time Collaborative Drawing Application.

## Base URL

```

http://localhost:8000

```

## Table of Contents

1. [Authentication](#authentication)
2. [Room Management](#room-management)
3. [Canvas Operations](#canvas-operations)
4. [Response Codes](#response-codes)
5. [Error Handling](#error-handling)

---

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```

Authorization: Bearer <your_jwt_token>

```

### Register User

Create a new user account.

**Endpoint**: `POST /register`

**Request Body**:
```

{
"email": "user@example.com",
"password": "securepassword123",
"full_name": "John Doe"
}

```

**Response** (201 Created):
```

{
"message": "User registered successfully",
"user_id": 1,
"email": "user@example.com"
}

```

**Error Responses**:
- `400 Bad Request`: Email already registered
- `422 Unprocessable Entity`: Invalid input format

---

### Login

Authenticate and receive JWT token.

**Endpoint**: `POST /login`

**Request Body**:
```

{
"email": "user@example.com",
"password": "securepassword123"
}

```

**Response** (200 OK):
```

{
"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
"token_type": "bearer",
"user_id": 1,
"email": "user@example.com"
}

```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `404 Not Found`: User not found

---

### Get Current User

Retrieve authenticated user information.

**Endpoint**: `GET /me`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"user_id": 1,
"email": "user@example.com",
"full_name": "John Doe",
"is_active": true
}

```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token

---

## Room Management

### Create Room

Create a new collaborative drawing room.

**Endpoint**: `POST /rooms/create`

**Headers**:
```

Authorization: Bearer <token>

```

**Request Body**:
```

{
"name": "Design Team Room",
"description": "Collaborative workspace for design team",
"max_users": 10
}

```

**Response** (201 Created):
```

{
"id": "room-a1b2c3d4",
"name": "Design Team Room",
"description": "Collaborative workspace for design team",
"owner_id": 1,
"max_users": 10,
"created_at": "2025-10-09T14:30:00Z",
"is_active": true
}

```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token
- `422 Unprocessable Entity`: Invalid input

---

### Join Room

Join an existing room by room ID.

**Endpoint**: `POST /rooms/join`

**Headers**:
```

Authorization: Bearer <token>

```

**Request Body**:
```

{
"room_id": "room-a1b2c3d4"
}

```

**Response** (200 OK):
```

{
"message": "Successfully joined room",
"room_id": "room-a1b2c3d4",
"role": "MEMBER",
"joined_at": "2025-10-09T14:35:00Z"
}

```

**Error Responses**:
- `404 Not Found`: Room does not exist
- `400 Bad Request`: Already a member or room is full
- `401 Unauthorized`: Missing or invalid token

---

### Get My Rooms

List all rooms the user is a member of.

**Endpoint**: `GET /rooms/my`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

[
{
"id": "room-a1b2c3d4",
"name": "Design Team Room",
"description": "Collaborative workspace",
"owner_id": 1,
"role": "OWNER",
"max_users": 10,
"created_at": "2025-10-09T14:30:00Z",
"member_count": 5
},
{
"id": "room-e5f6g7h8",
"name": "Project Brainstorm",
"description": "Brainstorming session",
"owner_id": 3,
"role": "MEMBER",
"max_users": 8,
"created_at": "2025-10-08T10:00:00Z",
"member_count": 3
}
]

```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid token

---

### Get Room Details

Get detailed information about a specific room.

**Endpoint**: `GET /rooms/{room_id}`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"id": "room-a1b2c3d4",
"name": "Design Team Room",
"description": "Collaborative workspace for design team",
"owner_id": 1,
"owner_email": "owner@example.com",
"max_users": 10,
"created_at": "2025-10-09T14:30:00Z",
"members": [
{
"user_id": 1,
"email": "owner@example.com",
"role": "OWNER",
"joined_at": "2025-10-09T14:30:00Z"
},
{
"user_id": 2,
"email": "member@example.com",
"role": "MEMBER",
"joined_at": "2025-10-09T14:35:00Z"
}
]
}

```

**Error Responses**:
- `404 Not Found`: Room does not exist
- `403 Forbidden`: Not a member of this room
- `401 Unauthorized`: Missing or invalid token

---

### Leave Room

Leave a room (members only, owner cannot leave without deleting room).

**Endpoint**: `POST /rooms/leave/{room_id}`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"message": "Successfully left room",
"room_id": "room-a1b2c3d4"
}

```

**Error Responses**:
- `404 Not Found`: Room does not exist
- `403 Forbidden`: Owner cannot leave room (must delete instead)
- `400 Bad Request`: Not a member of this room
- `401 Unauthorized`: Missing or invalid token

---

### Remove Member

Remove a member from the room (owner only).

**Endpoint**: `DELETE /rooms/{room_id}/member/{user_id}`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"message": "Member removed successfully",
"room_id": "room-a1b2c3d4",
"removed_user_id": 3
}

```

**Error Responses**:
- `403 Forbidden`: Only room owner can remove members
- `404 Not Found`: Room or user not found
- `400 Bad Request`: Cannot remove owner
- `401 Unauthorized`: Missing or invalid token

---

### Delete Room

Delete a room permanently (owner only).

**Endpoint**: `DELETE /rooms/{room_id}`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"message": "Room deleted successfully",
"room_id": "room-a1b2c3d4"
}

```

**Error Responses**:
- `403 Forbidden`: Only room owner can delete room
- `404 Not Found`: Room does not exist
- `401 Unauthorized`: Missing or invalid token

---

## Canvas Operations

### Save Canvas State

Save the current canvas state to database.

**Endpoint**: `POST /canvas/save`

**Headers**:
```

Authorization: Bearer <token>
Content-Type: application/json

```

**Request Body**:
```

{
"room_id": "room-a1b2c3d4",
"state_json": "[{\"type\":\"brush\",\"fromX\":10,\"fromY\":20,\"toX\":15,\"toY\":25,\"color\":\"\#3182ce\",\"thickness\":4}]"
}

```

**Response** (200 OK):
```

{
"message": "Canvas saved successfully",
"snapshot_id": 42,
"room_id": "room-a1b2c3d4",
"saved_at": "2025-10-09T15:00:00Z"
}

```

**Error Responses**:
- `403 Forbidden`: Not a member of this room
- `404 Not Found`: Room does not exist
- `401 Unauthorized`: Missing or invalid token

---

### Load Canvas State

Load the latest canvas state for a room.

**Endpoint**: `GET /canvas/load/{room_id}`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"room_id": "room-a1b2c3d4",
"state_json": "[{\"type\":\"brush\",\"fromX\":10,\"fromY\":20,\"toX\":15,\"toY\":25,\"color\":\"\#3182ce\",\"thickness\":4}]",
"snapshot_id": 42,
"created_at": "2025-10-09T15:00:00Z"
}

```

**Response (Empty Canvas)** (200 OK):
```

{
"room_id": "room-a1b2c3d4",
"state_json": "[]",
"snapshot_id": null,
"created_at": null
}

```

**Error Responses**:
- `403 Forbidden`: Not a member of this room
- `404 Not Found`: Room does not exist
- `401 Unauthorized`: Missing or invalid token

---

### Create Canvas Snapshot

Create a versioned snapshot of the current canvas (manual save point).

**Endpoint**: `POST /canvas/snapshot`

**Headers**:
```

Authorization: Bearer <token>
Content-Type: application/json

```

**Request Body**:
```

{
"room_id": "room-a1b2c3d4",
"state_json": "[{\"type\":\"brush\",\"fromX\":10,\"fromY\":20,\"toX\":15,\"toY\":25,\"color\":\"\#3182ce\",\"thickness\":4}]"
}

```

**Response** (201 Created):
```

{
"message": "Snapshot created successfully",
"snapshot_id": 43,
"room_id": "room-a1b2c3d4",
"created_at": "2025-10-09T15:10:00Z"
}

```

**Error Responses**:
- `403 Forbidden`: Not a member of this room
- `404 Not Found`: Room does not exist
- `401 Unauthorized`: Missing or invalid token

---

### Get All Snapshots

Retrieve all canvas snapshots for a room (version history).

**Endpoint**: `GET /canvas/snapshots/{room_id}`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"room_id": "room-a1b2c3d4",
"snapshots": [
{
"id": 43,
"created_at": "2025-10-09T15:10:00Z",
"creator_id": 1,
"creator_email": "owner@example.com"
},
{
"id": 42,
"created_at": "2025-10-09T15:00:00Z",
"creator_id": 2,
"creator_email": "member@example.com"
}
]
}

```

**Error Responses**:
- `403 Forbidden`: Not a member of this room
- `404 Not Found`: Room does not exist
- `401 Unauthorized`: Missing or invalid token

---

### Clear Canvas

Clear the entire canvas (owner only).

**Endpoint**: `POST /canvas/clear/{room_id}`

**Headers**:
```

Authorization: Bearer <token>

```

**Response** (200 OK):
```

{
"message": "Canvas cleared successfully",
"room_id": "room-a1b2c3d4",
"cleared_at": "2025-10-09T15:20:00Z"
}

```

**Error Responses**:
- `403 Forbidden`: Only room owner can clear canvas
- `404 Not Found`: Room does not exist
- `401 Unauthorized`: Missing or invalid token

---

## Response Codes

| Code | Description |
|------|-------------|
| `200 OK` | Request successful |
| `201 Created` | Resource created successfully |
| `400 Bad Request` | Invalid request data or business logic violation |
| `401 Unauthorized` | Missing, invalid, or expired authentication token |
| `403 Forbidden` | Authenticated but lacking permissions |
| `404 Not Found` | Requested resource does not exist |
| `422 Unprocessable Entity` | Validation error in request body |
| `500 Internal Server Error` | Server-side error |

---

## Error Handling

All error responses follow this format:

```

{
"detail": "Error message describing what went wrong"
}

```

**Examples**:

**Authentication Error**:
```

{
"detail": "Could not validate credentials"
}

```

**Permission Error**:
```

{
"detail": "Only the room owner can clear the canvas"
}

```

**Not Found Error**:
```

{
"detail": "Room not found"
}

```

**Validation Error**:
```

{
"detail": [
{
"loc": ["body", "email"],
"msg": "field required",
"type": "value_error.missing"
}
]
}

```

---

## Authentication Flow

### Step 1: Register
```

curl -X POST http://localhost:8000/register \
-H "Content-Type: application/json" \
-d '{"email":"user@example.com","password":"pass123","full_name":"John Doe"}'

```

### Step 2: Login
```

curl -X POST http://localhost:8000/login \
-H "Content-Type: application/json" \
-d '{"email":"user@example.com","password":"pass123"}'

```

Response:
```

{
"access_token": "eyJhbGci...",
"token_type": "bearer"
}

```

### Step 3: Use Token
```

curl -X GET http://localhost:8000/rooms/my \
-H "Authorization: Bearer eyJhbGci..."

```

---

## Rate Limiting

Currently, no rate limiting is implemented. For production, consider adding rate limiting middleware.

---

## CORS Configuration

The API allows requests from:
- `http://localhost:3000` (React frontend)

To modify allowed origins, update `main.py`:

```

app.add_middleware(
CORSMiddleware,
allow_origins=["http://localhost:3000"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

```

---

## WebSocket Connection

For real-time drawing collaboration, use the WebSocket endpoint:

**Endpoint**: `WS /ws/{room_id}?token=<jwt_token>`

See [WEBSOCKET_SPEC.md](./WEBSOCKET_SPEC.md) for detailed protocol documentation.

---

## Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to test endpoints directly in the browser.

---

## Testing with Postman

1. Import the provided Postman collection (if available)
2. Set up environment variables:
   - `BASE_URL`: `http://localhost:8000`
   - `TOKEN`: Your JWT token after login
3. Test endpoints in the following order:
   - Register → Login → Create Room → Join Room → Save Canvas

---

## Additional Resources

- [SETUP.md](./SETUP.md) - Installation guide
- [DB_DIAGRAM.md](./DB_DIAGRAM.md) - Database schema
- [WEBSOCKET_SPEC.md](./WEBSOCKET_SPEC.md) - WebSocket protocol
- [USER_GUIDE.md](./USER_GUIDE.md) - End-user documentation
```

