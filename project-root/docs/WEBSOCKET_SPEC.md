# WebSocket Protocol Specification

Documentation for real-time communication protocol used in the collaborative drawing application.

## Overview

The application uses WebSockets for real-time bidirectional communication between clients and the server. This enables instant synchronization of drawing actions, cursor movements, and user presence across all connected users in a room.

---

## Connection

### WebSocket Endpoint

```

ws://localhost:8000/ws/{room_id}?token={jwt_token}

```

**Parameters**:
- `room_id` (path): The unique identifier of the room to join
- `token` (query): JWT authentication token obtained from login

**Example**:
```

ws://localhost:8000/ws/room-a1b2c3d4?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

```

---

## Authentication

The WebSocket connection requires a valid JWT token for authentication.

**JavaScript Example**:
```

const roomId = "room-a1b2c3d4";
const token = localStorage.getItem("token");
const ws = new WebSocket(`ws://localhost:8000/ws/${roomId}?token=${token}`);

```

**Authentication Flow**:
1. Client initiates WebSocket connection with JWT token in query parameter
2. Server validates token and extracts user information
3. If valid, connection is accepted and user is added to room's connection pool
4. If invalid, connection is rejected with error message

---

## Message Types

All messages are sent as JSON strings. Each message has a `type` field that determines how it should be handled.

### Client → Server Messages

#### 1. Draw Action

Sent when a user draws on the canvas (brush, eraser, shapes, text).

**Message Structure**:
```

{
"type": "draw",
"data": {
"action": "brush",
"fromX": 100,
"fromY": 150,
"toX": 105,
"toY": 155,
"color": "\#3182ce",
"thickness": 4
}
}

```

**Fields**:
- `type`: Always `"draw"`
- `data.action`: Drawing tool type (`"brush"`, `"eraser"`, `"rectangle"`, `"ellipse"`, `"text"`)
- `data.fromX`: Starting X coordinate
- `data.fromY`: Starting Y coordinate
- `data.toX`: Ending X coordinate
- `data.toY`: Ending Y coordinate
- `data.color`: Color hex code (e.g., `"#3182ce"`)
- `data.thickness`: Line thickness (2-12)
- `data.text` (optional): Text content for text tool

**Example - Rectangle**:
```

{
"type": "draw",
"data": {
"action": "rectangle",
"fromX": 50,
"fromY": 60,
"toX": 150,
"toY": 120,
"color": "\#e53e3e",
"thickness": 2
}
}

```

---

#### 2. Cursor Movement

Sent periodically to update cursor position for other users.

**Message Structure**:
```

{
"type": "cursor",
"data": {
"x": 250,
"y": 300,
"user_id": 1,
"user_email": "user@example.com"
}
}

```

**Fields**:
- `type`: Always `"cursor"`
- `data.x`: Current X coordinate of cursor
- `data.y`: Current Y coordinate of cursor
- `data.user_id`: User identifier
- `data.user_email`: User email (for display)

---

#### 3. Canvas Clear

Sent by room owner to clear the entire canvas.

**Message Structure**:
```

{
"type": "clear",
"data": {
"user_id": 1,
"timestamp": "2025-10-09T15:00:00Z"
}
}

```

**Fields**:
- `type`: Always `"clear"`
- `data.user_id`: Owner's user ID
- `data.timestamp`: ISO 8601 timestamp

---

### Server → Client Messages

#### 1. Draw Broadcast

Server broadcasts drawing actions to all other users in the room.

**Message Structure**:
```

{
"type": "draw",
"data": {
"action": "brush",
"fromX": 100,
"fromY": 150,
"toX": 105,
"toY": 155,
"color": "\#3182ce",
"thickness": 4,
"user_id": 2,
"user_email": "other@example.com"
}
}

```

**Fields**: Same as client message plus:
- `data.user_id`: ID of user who performed the action
- `data.user_email`: Email of user who performed the action

---

#### 2. Cursor Update

Server broadcasts cursor positions to all other users.

**Message Structure**:
```

{
"type": "cursor",
"data": {
"x": 250,
"y": 300,
"user_id": 2,
"user_email": "other@example.com"
}
}

```

---

#### 3. Members Update

Sent when a user joins or leaves the room.

**Message Structure**:
```

{
"type": "members",
"data": {
"members": [
{
"user_id": 1,
"user_email": "user1@example.com"
},
{
"user_id": 2,
"user_email": "user2@example.com"
}
],
"count": 2
}
}

```

**Fields**:
- `type`: Always `"members"`
- `data.members`: Array of currently connected users
- `data.count`: Total number of connected users

---

#### 4. Clear Broadcast

Server broadcasts canvas clear action to all users.

**Message Structure**:
```

{
"type": "clear",
"data": {
"user_id": 1,
"user_email": "owner@example.com",
"timestamp": "2025-10-09T15:00:00Z"
}
}

```

---

#### 5. Error Message

Sent when an error occurs (e.g., authentication failure, invalid message).

**Message Structure**:
```

{
"type": "error",
"message": "Invalid authentication token"
}

```

**Common Error Messages**:
- `"Invalid authentication token"`: JWT token is invalid or expired
- `"Room not found"`: Specified room does not exist
- `"Not a member of this room"`: User is not authorized to join
- `"Invalid message format"`: Malformed JSON or missing required fields

---

## Connection Lifecycle

### 1. Connection Established

**Client**:
```

ws.onopen = () => {
console.log("Connected to room");
};

```

**Server Actions**:
- Validates JWT token
- Adds user to room's active connections
- Broadcasts updated members list to all users

---

### 2. Sending Messages

**Client**:
```

// Send draw action
ws.send(JSON.stringify({
type: "draw",
data: {
action: "brush",
fromX: 100,
fromY: 150,
toX: 105,
toY: 155,
color: "\#3182ce",
thickness: 4
}
}));

// Send cursor position
ws.send(JSON.stringify({
type: "cursor",
data: {
x: 250,
y: 300,
user_id: 1,
user_email: "user@example.com"
}
}));

```

---

### 3. Receiving Messages

**Client**:
```

ws.onmessage = (event) => {
const message = JSON.parse(event.data);

switch (message.type) {
case "draw":
// Render drawing action on canvas
drawOnCanvas(message.data);
break;

    case "cursor":
      // Update other user's cursor position
      updateCursor(message.data);
      break;
      
    case "members":
      // Update members list UI
      updateMembersList(message.data.members);
      break;
      
    case "clear":
      // Clear local canvas
      clearCanvas();
      break;
      
    case "error":
      console.error("WebSocket error:", message.message);
      break;
    }
};

```

---

### 4. Connection Closed

**Client**:
```

ws.onclose = () => {
console.log("Disconnected from room");
};

```

**Server Actions**:
- Removes user from room's active connections
- Broadcasts updated members list to remaining users

---

### 5. Error Handling

**Client**:
```

ws.onerror = (error) => {
console.error("WebSocket error:", error);
};

```

---

## Implementation Example

### Complete Client Implementation

```

class RoomConnection {
constructor(roomId, token) {
this.roomId = roomId;
this.token = token;
this.ws = null;
this.userId = null;
this.userEmail = null;
}

connect() {
const wsUrl = `ws://localhost:8000/ws/${this.roomId}?token=${this.token}`;
this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log("Connected to room:", this.roomId);
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
    
    this.ws.onclose = () => {
      console.log("Disconnected from room");
    };
    
    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
    }

handleMessage(message) {
switch (message.type) {
case "draw":
this.onDraw(message.data);
break;
case "cursor":
this.onCursorMove(message.data);
break;
case "members":
this.onMembersUpdate(message.data);
break;
case "clear":
this.onClear();
break;
case "error":
this.onError(message.message);
break;
}
}

sendDraw(drawData) {
this.send({
type: "draw",
data: drawData
});
}

sendCursor(x, y) {
this.send({
type: "cursor",
data: {
x: x,
y: y,
user_id: this.userId,
user_email: this.userEmail
}
});
}

send(message) {
if (this.ws \&\& this.ws.readyState === WebSocket.OPEN) {
this.ws.send(JSON.stringify(message));
}
}

disconnect() {
if (this.ws) {
this.ws.close();
}
}

// Callback methods (override these)
onDraw(data) {}
onCursorMove(data) {}
onMembersUpdate(data) {}
onClear() {}
onError(message) {}
}

// Usage
const connection = new RoomConnection("room-a1b2c3d4", authToken);
connection.onDraw = (data) => {
console.log("Received draw action:", data);
// Render on canvas
};
connection.connect();

```

---

## Performance Considerations

### Message Throttling

For cursor movements, implement client-side throttling to avoid overwhelming the server:

```

let lastCursorSend = 0;
const CURSOR_THROTTLE_MS = 50; // Send at most every 50ms

canvas.addEventListener("mousemove", (e) => {
const now = Date.now();
if (now - lastCursorSend > CURSOR_THROTTLE_MS) {
connection.sendCursor(e.offsetX, e.offsetY);
lastCursorSend = now;
}
});

```

### Batch Drawing Actions

For smooth brush strokes, batch multiple small movements:

```

let drawBuffer = [];
const BATCH_INTERVAL_MS = 100;

function addToDrawBuffer(drawData) {
drawBuffer.push(drawData);
}

setInterval(() => {
if (drawBuffer.length > 0) {
connection.sendDraw({
action: "batch",
strokes: drawBuffer
});
drawBuffer = [];
}
}, BATCH_INTERVAL_MS);

```

---

## Security

### Token Validation

- JWT tokens are validated on connection
- Expired tokens are rejected immediately
- User must be a member of the room to connect

### Message Validation

- All incoming messages are validated for structure
- Invalid messages are rejected with error response
- Room ownership is verified for privileged actions (clear canvas)

---

## Testing

### Manual Testing with Browser Console

```

// Connect
const ws = new WebSocket("ws://localhost:8000/ws/room-a1b2c3d4?token=YOUR_TOKEN");

// Listen for messages
ws.onmessage = (e) => console.log(JSON.parse(e.data));

// Send draw action
ws.send(JSON.stringify({
type: "draw",
data: {
action: "brush",
fromX: 10,
fromY: 10,
toX: 20,
toY: 20,
color: "\#000000",
thickness: 4
}
}));

```

### Testing with wscat

```


# Install wscat

npm install -g wscat

# Connect

wscat -c "ws://localhost:8000/ws/room-a1b2c3d4?token=YOUR_TOKEN"

# Send message

{"type":"draw","data":{"action":"brush","fromX":10,"fromY":10,"toX":20,"toY":20,"color":"\#000000","thickness":4}}

```

---

## Troubleshooting

### Connection Issues

**Problem**: WebSocket fails to connect

**Solutions**:
- Verify backend server is running
- Check JWT token is valid and not expired
- Ensure room ID exists and user is a member
- Check browser console for error messages

### Message Not Received

**Problem**: Messages sent but not received by other clients

**Solutions**:
- Verify WebSocket connection is open (`ws.readyState === 1`)
- Check message format is valid JSON
- Ensure message has required fields
- Check server logs for errors

### Performance Issues

**Problem**: Lag or stuttering during drawing

**Solutions**:
- Implement cursor movement throttling
- Batch drawing actions
- Reduce message frequency
- Check network latency

---

## Related Documentation

- [API_DOC.md](./API_DOC.md) - REST API endpoints
- [SETUP.md](./SETUP.md) - Installation and configuration
- [USER_GUIDE.md](./USER_GUIDE.md) - End-user instructions
- [DB_DIAGRAM.md](./DB_DIAGRAM.md) - Database schema
```
