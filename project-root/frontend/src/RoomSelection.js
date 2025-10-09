import React, { useState, useEffect } from 'react';

function RoomSelection({ token, currentUser, onRoomSelected, onLogout }) {
  const [activeTab, setActiveTab] = useState('myRooms');
  const [rooms, setRooms] = useState([]);
  const [loading, setLoading] = useState(false);

  // Create room form
  const [createData, setCreateData] = useState({ name: '', description: '', maxUsers: 10 });

  // Join room form
  const [joinData, setJoinData] = useState({ roomId: '' });

  const fetchMyRooms = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/rooms/my', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRooms(data);
      } else {
        console.error('Failed to fetch rooms');
      }
    } catch (error) {
      console.error('Error fetching rooms:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchMyRooms();
    // eslint-disable-next-line
  }, []);

  const handleCreateRoom = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/rooms/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(createData)
      });
      if (response.ok) {
        const newRoom = await response.json();
        alert(`Room created: ${newRoom.name}`);
        setCreateData({ name: '', description: '', maxUsers: 10 });
        fetchMyRooms(); // Refresh room list
      } else {
        const error = await response.json();
        alert(`Failed to create room: ${error.detail}`);
      }
    } catch (error) {
      alert('Error creating room');
    }
  };

  const handleJoinRoom = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/rooms/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ room_id: joinData.roomId })
      });
      if (response.ok) {
        alert('Successfully joined room!');
        setJoinData({ roomId: '' });
        fetchMyRooms(); // Refresh room list
      } else {
        const error = await response.json();
        alert(`Failed to join room: ${error.detail}`);
      }
    } catch (error) {
      alert('Error joining room');
    }
  };

  const handleEnterRoom = (room) => {
    onRoomSelected(room.room_id, room.name, room.role);
  };

  // === OWNER-ONLY ACTIONS ===

  // Delete Room
  const handleDeleteRoom = async (roomId) => {
    if (!window.confirm('Are you sure you want to delete this room? This cannot be undone.')) return;
    try {
      const response = await fetch(`http://localhost:8000/rooms/${roomId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        alert('Room deleted.');
        fetchMyRooms();
      } else {
        const error = await response.json();
        alert(`Failed to delete room: ${error.detail}`);
      }
    } catch (error) {
      alert('Error deleting room');
    }
  };

  // Remove Member (owner only)
  const handleRemoveMember = async (roomId, userId) => {
    if (!window.confirm('Remove this member from the room?')) return;
    try {
      const response = await fetch('http://localhost:8000/rooms/remove_member', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ room_id: roomId, user_id: userId })
      });
      if (response.ok) {
        alert('Member removed.');
        fetchMyRooms();
      } else {
        const error = await response.json();
        alert(`Failed to remove member: ${error.detail}`);
      }
    } catch (error) {
      alert('Error removing member');
    }
  };

  // Helper to see if current user is owner of a room
  const isOwner = (room) => (currentUser && currentUser.user_id && room.owner_id === currentUser.user_id);

  return (
    <div className="room-selection">
      <div className="room-header">
        <h1>🏠 Room Management</h1>
        <div className="user-info">
          <span>Welcome, {currentUser?.full_name || currentUser?.email}</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </div>

      <div className="room-content">
        <div className="room-tabs">
          <button className={`tab-btn ${activeTab === 'myRooms' ? 'active' : ''}`} onClick={() => setActiveTab('myRooms')}>
            My Rooms
          </button>
          <button className={`tab-btn ${activeTab === 'create' ? 'active' : ''}`} onClick={() => setActiveTab('create')}>
            Create Room
          </button>
          <button className={`tab-btn ${activeTab === 'join' ? 'active' : ''}`} onClick={() => setActiveTab('join')}>
            Join Room
          </button>
        </div>

        <div className="room-tab-content">
          {activeTab === 'myRooms' && (
            <div className="my-rooms">
              <div className="section-header">
                <h2>Your Rooms</h2>
                <button onClick={fetchMyRooms} disabled={loading} className="refresh-btn">
                  {loading ? 'Loading...' : 'Refresh'}
                </button>
              </div>
              {rooms.length === 0 ? (
                <p>No rooms yet. Create a new room or join an existing one!</p>
              ) : (
                <div className="rooms-grid">
                  {rooms.map((room) => (
                    <div key={room.room_id} className="room-card">
                      <div className="room-info">
                        <h3>{room.name}</h3>
                        <p>Room ID: <code>{room.room_id}</code></p>
                        <p>Role: <span className={`role-badge ${room.role}`}>{room.role}</span></p>
                      </div>
                      <div style={{display:'flex', flexDirection: 'column', alignItems:'center'}}>
                        <button onClick={() => handleEnterRoom(room)} className="enter-room-btn">
                          Enter Room
                        </button>
                        {isOwner(room) && (
                          <button
                            style={{marginTop: 8, background: '#da3448', color: '#fff', border: 'none', borderRadius: 7, padding: '6px 14px', fontWeight: 600, cursor: 'pointer'}}
                            onClick={() => handleDeleteRoom(room.room_id)}
                          >Delete Room</button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'create' && (
            <div className="create-room">
              <h2>Create New Room</h2>
              <form onSubmit={handleCreateRoom} className="room-form">
                <input
                  type="text"
                  placeholder="Room Name"
                  value={createData.name}
                  onChange={(e) => setCreateData({...createData, name: e.target.value})}
                  required
                />
                <textarea
                  placeholder="Room Description (optional)"
                  value={createData.description}
                  onChange={(e) => setCreateData({...createData, description: e.target.value})}
                  rows="3"
                />
                <input
                  type="number"
                  placeholder="Max Users"
                  value={createData.maxUsers}
                  onChange={(e) => setCreateData({...createData, maxUsers: parseInt(e.target.value)})}
                  min="2"
                  max="50"
                />
                <button type="submit">Create Room</button>
              </form>
            </div>
          )}

          {activeTab === 'join' && (
            <div className="join-room">
              <h2>Join Existing Room</h2>
              <form onSubmit={handleJoinRoom} className="room-form">
                <input
                  type="text"
                  placeholder="Room ID (e.g., room-abc123)"
                  value={joinData.roomId}
                  onChange={(e) => setJoinData({...joinData, roomId: e.target.value})}
                  required
                />
                <button type="submit">Join Room</button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default RoomSelection;
