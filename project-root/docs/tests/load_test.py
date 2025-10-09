"""
Load Testing Script for Real-Time Collaborative Drawing Application

This script performs load testing on the application to measure:
- API endpoint performance
- WebSocket connection handling
- Concurrent user capacity
- Database performance under load
- Response times and throughput

Requirements:
    pip install locust requests websocket-client

Usage:
    # Run with Locust web UI
    locust -f load_test.py --host=http://localhost:8000

    # Run headless mode
    locust -f load_test.py --host=http://localhost:8000 --users 100 --spawn-rate 10 --run-time 5m --headless

    # Generate HTML report
    locust -f load_test.py --host=http://localhost:8000 --users 50 --spawn-rate 5 --run-time 2m --html=report.html --headless
"""

from locust import HttpUser, task, between, events
import json
import random
import time
import websocket
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DrawingAppUser(HttpUser):
    """
    Simulates a user interacting with the drawing application.
    """
    
    # Wait time between tasks (1-3 seconds)
    wait_time = between(1, 3)
    
    def on_start(self):
        """
        Called when a simulated user starts.
        Registers and logs in to get authentication token.
        """
        self.user_id = None
        self.token = None
        self.room_id = None
        self.email = f"loadtest_{random.randint(1000, 999999)}@test.com"
        self.password = "testpassword123"
        
        # Register user
        self.register()
        
        # Login to get token
        self.login()
        
        # Create or join a room
        if random.choice([True, False]):
            self.create_room()
        else:
            # Try to join an existing room (may fail if none exist)
            self.join_existing_room()
    
    def register(self):
        """Register a new user account."""
        response = self.client.post(
            "/register",
            json={
                "email": self.email,
                "password": self.password,
                "full_name": f"Load Test User {random.randint(1, 1000)}"
            },
            name="01_Register"
        )
        
        if response.status_code == 201 or response.status_code == 200:
            logger.info(f"✓ Registered user: {self.email}")
        else:
            logger.error(f"✗ Registration failed: {response.text}")
    
    def login(self):
        """Login and obtain JWT token."""
        response = self.client.post(
            "/login",
            json={
                "email": self.email,
                "password": self.password
            },
            name="02_Login"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user_id")
            logger.info(f"✓ Logged in: {self.email}")
        else:
            logger.error(f"✗ Login failed: {response.text}")
    
    def create_room(self):
        """Create a new drawing room."""
        if not self.token:
            return
        
        response = self.client.post(
            "/rooms/create",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "name": f"Load Test Room {random.randint(1, 1000)}",
                "description": "Automated load testing room",
                "max_users": 10
            },
            name="03_CreateRoom"
        )
        
        if response.status_code == 201:
            data = response.json()
            self.room_id = data.get("id")
            logger.info(f"✓ Created room: {self.room_id}")
        else:
            logger.error(f"✗ Room creation failed: {response.text}")
    
    def join_existing_room(self):
        """Attempt to join an existing room."""
        if not self.token:
            return
        
        # Get list of available rooms
        response = self.client.get(
            "/rooms/my",
            headers={"Authorization": f"Bearer {self.token}"},
            name="04_GetMyRooms"
        )
        
        if response.status_code == 200:
            rooms = response.json()
            if rooms and len(rooms) > 0:
                # Join a random room
                room = random.choice(rooms)
                self.room_id = room.get("id")
                logger.info(f"✓ Joined existing room: {self.room_id}")
    
    @task(3)
    def get_my_rooms(self):
        """Fetch user's rooms (common operation)."""
        if not self.token:
            return
        
        self.client.get(
            "/rooms/my",
            headers={"Authorization": f"Bearer {self.token}"},
            name="04_GetMyRooms"
        )
    
    @task(5)
    def save_canvas(self):
        """Save canvas state to database."""
        if not self.token or not self.room_id:
            return
        
        # Generate random drawing data
        canvas_state = self.generate_random_canvas_state()
        
        self.client.post(
            "/canvas/save",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "room_id": self.room_id,
                "state_json": json.dumps(canvas_state)
            },
            name="05_SaveCanvas"
        )
    
    @task(4)
    def load_canvas(self):
        """Load canvas state from database."""
        if not self.token or not self.room_id:
            return
        
        self.client.get(
            f"/canvas/load/{self.room_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            name="06_LoadCanvas"
        )
    
    @task(2)
    def create_snapshot(self):
        """Create a canvas snapshot."""
        if not self.token or not self.room_id:
            return
        
        canvas_state = self.generate_random_canvas_state()
        
        self.client.post(
            "/canvas/snapshot",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "room_id": self.room_id,
                "state_json": json.dumps(canvas_state)
            },
            name="07_CreateSnapshot"
        )
    
    @task(1)
    def get_snapshots(self):
        """Retrieve all snapshots for a room."""
        if not self.token or not self.room_id:
            return
        
        self.client.get(
            f"/canvas/snapshots/{self.room_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            name="08_GetSnapshots"
        )
    
    @task(1)
    def get_room_details(self):
        """Get detailed information about a room."""
        if not self.token or not self.room_id:
            return
        
        self.client.get(
            f"/rooms/{self.room_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            name="09_GetRoomDetails"
        )
    
    def generate_random_canvas_state(self):
        """Generate random drawing data for testing."""
        colors = ["#e53e3e", "#3182ce", "#38a169", "#f6ad55", "#2d3748"]
        actions = ["brush", "eraser", "rectangle", "ellipse"]
        
        state = []
        num_strokes = random.randint(5, 20)
        
        for _ in range(num_strokes):
            stroke = {
                "type": random.choice(actions),
                "fromX": random.randint(0, 800),
                "fromY": random.randint(0, 600),
                "toX": random.randint(0, 800),
                "toY": random.randint(0, 600),
                "color": random.choice(colors),
                "thickness": random.choice([2, 4, 6, 8, 12])
            }
            state.append(stroke)
        
        return state
    
    def on_stop(self):
        """Called when the user stops (optional cleanup)."""
        logger.info(f"✓ User stopped: {self.email}")


class WebSocketUser(HttpUser):
    """
    Simulates a user connecting via WebSocket for real-time collaboration.
    """
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Setup WebSocket connection."""
        self.ws = None
        self.token = None
        self.room_id = None
        self.email = f"ws_user_{random.randint(1000, 999999)}@test.com"
        self.password = "testpassword123"
        
        # Register and login
        self.register()
        self.login()
        self.create_room()
        
        # Connect to WebSocket
        if self.token and self.room_id:
            self.connect_websocket()
    
    def register(self):
        """Register user."""
        self.client.post(
            "/register",
            json={
                "email": self.email,
                "password": self.password,
                "full_name": "WebSocket Test User"
            },
            name="WS_01_Register"
        )
    
    def login(self):
        """Login user."""
        response = self.client.post(
            "/login",
            json={
                "email": self.email,
                "password": self.password
            },
            name="WS_02_Login"
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
    
    def create_room(self):
        """Create room."""
        if not self.token:
            return
        
        response = self.client.post(
            "/rooms/create",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "name": f"WS Test Room {random.randint(1, 1000)}",
                "description": "WebSocket load test",
                "max_users": 10
            },
            name="WS_03_CreateRoom"
        )
        
        if response.status_code == 201:
            data = response.json()
            self.room_id = data.get("id")
    
    def connect_websocket(self):
        """Connect to WebSocket endpoint."""
        try:
            ws_url = f"ws://localhost:8000/ws/{self.room_id}?token={self.token}"
            self.ws = websocket.create_connection(ws_url)
            logger.info(f"✓ WebSocket connected for room: {self.room_id}")
        except Exception as e:
            logger.error(f"✗ WebSocket connection failed: {str(e)}")
    
    @task(10)
    def send_draw_action(self):
        """Send drawing action via WebSocket."""
        if not self.ws:
            return
        
        try:
            message = {
                "type": "draw",
                "data": {
                    "action": random.choice(["brush", "eraser", "rectangle"]),
                    "fromX": random.randint(0, 800),
                    "fromY": random.randint(0, 600),
                    "toX": random.randint(0, 800),
                    "toY": random.randint(0, 600),
                    "color": random.choice(["#e53e3e", "#3182ce", "#38a169"]),
                    "thickness": random.choice([2, 4, 6, 8])
                }
            }
            
            start_time = time.time()
            self.ws.send(json.dumps(message))
            elapsed = (time.time() - start_time) * 1000
            
            # Report to Locust
            events.request.fire(
                request_type="WebSocket",
                name="WS_SendDraw",
                response_time=elapsed,
                response_length=len(json.dumps(message)),
                exception=None,
                context={}
            )
        except Exception as e:
            logger.error(f"✗ WebSocket send failed: {str(e)}")
            events.request.fire(
                request_type="WebSocket",
                name="WS_SendDraw",
                response_time=0,
                response_length=0,
                exception=e,
                context={}
            )
    
    @task(5)
    def send_cursor_position(self):
        """Send cursor position via WebSocket."""
        if not self.ws:
            return
        
        try:
            message = {
                "type": "cursor",
                "data": {
                    "x": random.randint(0, 800),
                    "y": random.randint(0, 600),
                    "user_id": 1,
                    "user_email": self.email
                }
            }
            
            self.ws.send(json.dumps(message))
        except Exception as e:
            logger.error(f"✗ WebSocket cursor send failed: {str(e)}")
    
    def on_stop(self):
        """Cleanup WebSocket connection."""
        if self.ws:
            try:
                self.ws.close()
                logger.info(f"✓ WebSocket closed for: {self.email}")
            except:
                pass


# Custom event listeners for detailed reporting
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts."""
    logger.info("=" * 60)
    logger.info("🚀 LOAD TEST STARTED")
    logger.info(f"   Target Host: {environment.host}")
    logger.info(f"   Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops."""
    logger.info("=" * 60)
    logger.info("🏁 LOAD TEST COMPLETED")
    logger.info(f"   End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)


# Optional: Custom statistics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track custom statistics for each request."""
    if exception:
        logger.warning(f"✗ Request failed: {name} - {str(exception)}")


if __name__ == "__main__":
    """
    Entry point for running the load test.
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Real-Time Collaborative Drawing App - Load Test          ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Usage:
        locust -f load_test.py --host=http://localhost:8000
        
    Then open: http://localhost:8089
    
    Recommended test scenarios:
    
    1. Light Load Test:
       - Users: 10-20
       - Spawn Rate: 2-5 users/sec
       - Duration: 2 minutes
    
    2. Medium Load Test:
       - Users: 50-100
       - Spawn Rate: 5-10 users/sec
       - Duration: 5 minutes
    
    3. Heavy Load Test:
       - Users: 200-500
       - Spawn Rate: 10-20 users/sec
       - Duration: 10 minutes
    
    4. Stress Test:
       - Users: 1000+
       - Spawn Rate: 50 users/sec
       - Duration: 15 minutes
    """)
