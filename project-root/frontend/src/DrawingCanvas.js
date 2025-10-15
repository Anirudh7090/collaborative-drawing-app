import React, { useRef, useEffect, useState } from "react";

// Use environment variables for API URLs
const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

const COLORS = ['#e53e3e', '#3182ce', '#38a169', '#f6ad55', '#2d3748', '#555'];
const THICKNESS = [2, 4, 6, 8, 12];
const TOOLS = [
  { key: 'brush', label: 'Brush' },
  { key: 'eraser', label: 'Eraser' },
  { key: 'rectangle', label: 'Rectangle' },
  { key: 'ellipse', label: 'Ellipse' },
  { key: 'text', label: 'Text' },
  { key: 'undo', label: 'Undo' }
];
const TOOL_LABELS = {
  brush: "Brush", eraser: "Eraser", rectangle: "Rectangle", ellipse: "Ellipse", text: "Text", undo: "Undo"
};
const CURSORS = {
  brush: "url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32'><circle cx='16' cy='16' r='8' fill='white' stroke='blue' stroke-width='3'/></svg>\") 16 16, crosshair",
  eraser: "url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32'><rect x='7' y='10' width='18' height='8' rx='4' fill='pink' stroke='gray' stroke-width='2'/></svg>\") 16 14, pointer",
  rectangle: "url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32'><rect x='8' y='8' width='16' height='10' stroke='red' fill='white' stroke-width='3'/></svg>\") 16 16, crosshair",
  ellipse: "url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32'><ellipse cx='16' cy='16' rx='8' ry='5' stroke='green' fill='white' stroke-width='3'/></svg>\") 16 16, crosshair",
  text: "url(\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32'><text x='4' y='22' font-size='18' font-family='Arial' fill='black'>T</text></svg>\") 6 22, text",
  undo: "crosshair"
};
const CANVAS_W = 1200;
const CANVAS_H = 700;
const COLLISION_RADIUS = 24; // px collision detection


function DrawingCanvas({ currentUser, roomId, token }) {
  const canvasRef = useRef(null);
  const wsRef = useRef(null);

  const [drawing, setDrawing] = useState(false);
  const [lastPosition, setLastPosition] = useState({ x: null, y: null });
  const [color, setColor] = useState(COLORS[1]);
  const [thickness, setThickness] = useState(4);
  const [tool, setTool] = useState('brush');
  const [shapeStart, setShapeStart] = useState(null);
  const [remoteCursors, setRemoteCursors] = useState({});
  const [myCursor, setMyCursor] = useState({ x: null, y: null, tool: 'brush' });
  const [collision, setCollision] = useState(false);
  const [localStrokes, setLocalStrokes] = useState([]);
  const [snapshots, setSnapshots] = useState([]);
  const [loadingSnapshots, setLoadingSnapshots] = useState(false);
  const [clearing, setClearing] = useState(false);

  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};

  // Owner check helper
  const isOwner = currentUser?.role === 'OWNER' || (currentUser && currentUser.user_id && currentUser.user_id === currentUser.owner_id);

  // Collision detection
  function isColliding(x, y) {
    return Object.values(remoteCursors).some(
      c => c.x !== null && c.y !== null &&
        Math.abs(c.x - x) < COLLISION_RADIUS &&
        Math.abs(c.y - y) < COLLISION_RADIUS
    );
  }

  const clearAndRedraw = (strokes) => {
    const ctx = canvasRef.current.getContext('2d');
    ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
    strokes.forEach(drawStroke);
  };

  useEffect(() => {
    async function loadCanvasState() {
      try {
        const resp = await fetch(`${API_URL}/canvas/load/${roomId}`, {
          headers: { ...authHeaders }
        });
        if (resp.ok) {
          const data = await resp.json();
          const strokes = JSON.parse(data.state_json || "[]");
          setLocalStrokes(strokes);
          clearAndRedraw(strokes);
        } else {
          setLocalStrokes([]);
          clearAndRedraw([]);
        }
      } catch (e) {
        setLocalStrokes([]);
        clearAndRedraw([]);
      }
    }
    loadCanvasState();
  }, [roomId, token, clearing]);

  const fetchSnapshots = async () => {
    setLoadingSnapshots(true);
    try {
      const result = await fetch(`${API_URL}/canvas/snapshots/${roomId}`, {
        headers: { ...authHeaders }
      });
      if (result.ok) {
        const arr = await result.json();
        setSnapshots(arr);
      }
    } catch (e) {}
    setLoadingSnapshots(false);
  };

  useEffect(() => {
    fetchSnapshots();
  }, [roomId, token]);

  const handleSaveSnapshot = async () => {
    try {
      const r = await fetch(`${API_URL}/canvas/snapshot`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders },
        body: JSON.stringify({
          room_id: roomId,
          state_json: JSON.stringify(localStrokes)
        })
      });
      if (r.ok) {
        alert("Snapshot/version saved!");
        fetchSnapshots();
      } else {
        alert("Failed to save snapshot.");
      }
    } catch (e) {
      alert("Failed to save snapshot.");
    }
  };

  const handleRestoreSnapshot = async (snapshot_id) => {
    try {
      const r = await fetch(`${API_URL}/canvas/snapshot/${snapshot_id}`, {
        headers: { ...authHeaders }
      });
      if (r.ok) {
        const snap = await r.json();
        const strokes = JSON.parse(snap.state_json || "[]");
        setLocalStrokes(strokes);
        clearAndRedraw(strokes);
        alert(`Loaded version from ${new Date(snap.created_at).toLocaleString()}`);
      } else {
        alert("Failed to load snapshot.");
      }
    } catch (e) {
      alert("Failed to load snapshot.");
    }
  };

  const handleSaveCanvas = async () => {
    try {
      await fetch(`${API_URL}/canvas/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...authHeaders },
        body: JSON.stringify({
          room_id: roomId,
          state_json: JSON.stringify(localStrokes)
        })
      });
      alert("Canvas state saved!");
    } catch (e) {
      alert("Failed to save canvas state.");
    }
  };

  // ---- OWNER-ONLY CLEAR CANVAS ----
  const handleClearCanvas = async () => {
    if (!window.confirm('Are you sure you want to clear the canvas for everyone?')) return;
    setClearing(true);
    try {
      const response = await fetch(`${API_URL}/canvas/clear/${roomId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        alert('Canvas cleared!');
        setClearing(false);
        const data = await response.json();
        setLocalStrokes([]);
        clearAndRedraw([]);
      } else {
        setClearing(false);
        const error = await response.json();
        alert(`Failed to clear canvas: ${error.detail}`);
      }
    } catch (error) {
      setClearing(false);
      alert('Error clearing canvas');
    }
  };

  useEffect(() => {
    wsRef.current = new window.WebSocket(`${WS_URL}/ws/${roomId}?token=${token}`);
    const ws = wsRef.current;
    ws.onopen = () => {};
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (
        ['draw', 'brush', 'eraser', 'rectangle', 'ellipse', 'text'].includes(msg.type)
      ) {
        drawStroke(msg);
        setLocalStrokes(prev => [...prev, msg]);
      }
      if (msg.type === "undo") {
        clearAndRedraw(msg.shapes || []);
        setLocalStrokes(msg.shapes || []);
      }
      if (msg.type === "cursor" && msg.userId !== (currentUser?.email || "anonymous")) {
        setRemoteCursors(prev => ({
          ...prev,
          [msg.userId]: {
            x: msg.x,
            y: msg.y,
            name: msg.name,
            color: msg.cursorColor,
            tool: msg.tool
          }
        }));
      }
    };
    ws.onclose = () => {};
    return () => ws.close();
  }, [roomId, currentUser]);

  const sendWS = (obj) => {
    if (wsRef.current && wsRef.current.readyState === 1) {
      wsRef.current.send(JSON.stringify(obj));
    }
  };

  const getCanvasCoords = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    return {
      x: Math.round(((e.clientX - rect.left) / rect.width) * CANVAS_W),
      y: Math.round(((e.clientY - rect.top) / rect.height) * CANVAS_H)
    };
  };

  function drawStroke(stroke) {
    const ctx = canvasRef.current.getContext('2d');
    if (['draw', 'brush', 'eraser'].includes(stroke.type)) {
      ctx.beginPath();
      ctx.moveTo(stroke.fromX, stroke.fromY);
      ctx.lineTo(stroke.toX, stroke.toY);
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.thickness;
      ctx.stroke();
    }
    if (stroke.type === 'rectangle') {
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.thickness;
      ctx.strokeRect(
        stroke.fromX, stroke.fromY,
        stroke.toX - stroke.fromX, stroke.toY - stroke.fromY
      );
    }
    if (stroke.type === 'ellipse') {
      ctx.strokeStyle = stroke.color;
      ctx.lineWidth = stroke.thickness;
      ctx.beginPath();
      ctx.ellipse(
        (stroke.fromX + stroke.toX) / 2,
        (stroke.fromY + stroke.toY) / 2,
        Math.abs((stroke.toX - stroke.fromX) / 2),
        Math.abs((stroke.toY - stroke.fromY) / 2),
        0, 0, 2 * Math.PI
      );
      ctx.stroke();
    }
    if (stroke.type === 'text') {
      ctx.fillStyle = stroke.color;
      ctx.font = `${stroke.fontSize || 20}px sans-serif`;
      ctx.fillText(stroke.value, stroke.x, stroke.y);
    }
  }

  const handleUndo = () => {
    const ctx = canvasRef.current.getContext('2d');
    ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
    sendWS({ type: 'undo' });
    setLocalStrokes([]);
  };

  const start = e => {
    const { x, y } = getCanvasCoords(e);
    if (tool === 'undo') {
      handleUndo();
      setTool('brush');
      return;
    }
    if (tool === 'text') {
      const value = window.prompt("Enter your text:");
      if (value) {
        const stroke = { type: 'text', x, y, value, color, fontSize: 20 };
        drawStroke(stroke);
        sendWS(stroke);
        setLocalStrokes(prev => [...prev, stroke]);
      }
      return;
    }
    if (tool === 'rectangle' || tool === 'ellipse') {
      setShapeStart({ x, y });
      setDrawing(true);
      return;
    }
    const ctx = canvasRef.current.getContext('2d');
    ctx.strokeStyle = tool === 'eraser' ? '#f9fafb' : color;
    ctx.lineWidth = thickness;
    ctx.beginPath();
    ctx.moveTo(x, y);
    setDrawing(true);
    setLastPosition({ x, y });
  };

  const move = e => {
    const { x, y } = getCanvasCoords(e);
    setMyCursor({ x, y, tool });

    // --- COLLISION CHECK ---
    if (drawing && isColliding(x, y)) {
      setCollision(true);
      return;
    } else {
      setCollision(false);
    }
    sendWS({
      type: "cursor",
      userId: currentUser?.email || "anonymous",
      name: currentUser?.fullName || currentUser?.email || "anonymous",
      x, y,
      cursorColor: color,
      tool: tool
    });

    if (!drawing) return;
    if (tool === 'rectangle' || tool === 'ellipse') return;

    const ctx = canvasRef.current.getContext('2d');
    const drawColor = tool === 'eraser' ? '#f9fafb' : color;
    ctx.strokeStyle = drawColor;
    ctx.lineWidth = thickness;
    ctx.lineTo(x, y);
    ctx.stroke();
    if (lastPosition.x !== null) {
      const payload = {
        type: tool,
        fromX: lastPosition.x,
        fromY: lastPosition.y,
        toX: x,
        toY: y,
        color: drawColor,
        thickness
      };
      sendWS(payload);
      setLocalStrokes(prev => [...prev, payload]);
    }
    setLastPosition({ x, y });
  };

  useEffect(() => {
    if (myCursor.x !== null && myCursor.y !== null) {
      sendWS({
        type: "cursor",
        userId: currentUser?.email || "anonymous",
        name: currentUser?.fullName || currentUser?.email || "anonymous",
        x: myCursor.x,
        y: myCursor.y,
        cursorColor: color,
        tool: tool
      });
    }
    setMyCursor(cur => ({ ...cur, tool }));
  }, [tool]);

  const stop = e => {
    setDrawing(false);
    setLastPosition({ x: null, y: null });
    if (tool === 'rectangle' || tool === 'ellipse') {
      if (!shapeStart) return;
      const { x, y } = getCanvasCoords(e);

      const newShape = {
        type: tool,
        fromX: shapeStart.x,
        fromY: shapeStart.y,
        toX: x,
        toY: y,
        color,
        thickness
      };
      drawStroke(newShape);
      sendWS(newShape);
      setLocalStrokes(prev => [...prev, newShape]);
      setShapeStart(null);
    }
  };

  // --- Snapshot UI ---
  const renderSnapshots = () => (
    <div style={{
      width: "100%",
      marginBottom: 16,
      background: "#f5f9ff",
      border: "1px solid #a0c4e2",
      borderRadius: 10,
      padding: "8px 16px",
      fontSize: 15
    }}>
      <div style={{ fontWeight: 700, marginBottom: 5 }}>
        Canvas Snapshots / History
        <button
          style={{
            float: "right", marginLeft: 4, borderRadius: 6,
            border: "none", background: "#ddd", padding: "4px 12px",
            fontWeight: 600, fontSize: 14, cursor: "pointer"
          }}
          disabled={loadingSnapshots}
          onClick={fetchSnapshots}
        >Refresh</button>
      </div>
      <div style={{ maxHeight: 120, overflowY: "auto" }}>
        {snapshots.length === 0 ? <div style={{ color: "#666" }}>No snapshots yet.</div> :
          <ul style={{ paddingLeft: 8, margin: "0 0 0 0" }}>
            {snapshots.map(snap =>
              <li key={snap.snapshot_id} style={{ marginBottom: 5 }}>
                <span style={{ color: "#3182ce", fontWeight: 600 }}>{new Date(snap.created_at).toLocaleString()}</span>
                <button style={{
                  marginLeft: 12, background: "#3182ce", color: "#fff",
                  padding: "2px 8px", borderRadius: 6, border: "none", cursor: "pointer", fontWeight: 600
                }} onClick={() => handleRestoreSnapshot(snap.snapshot_id)}>
                  Restore
                </button>
              </li>
            )}
          </ul>
        }
      </div>
      <button
        style={{
          marginTop: 8,
          padding: "5px 20px",
          fontSize: "15px",
          borderRadius: 8,
          background: "#275c9e",
          color: "#fff",
          fontWeight: 600,
          border: "none",
          cursor: "pointer"
        }}
        onClick={handleSaveSnapshot}
      >
        Save as New Snapshot
      </button>
    </div>
  );

  // CLEAR CANVAS BUTTON (owner only)
  const renderOwnerButtons = () => isOwner && (
    <button
      style={{
        margin: "10px 0",
        padding: "6px 20px",
        fontSize: "16px",
        borderRadius: 8,
        background: "#da3448",
        color: "#fff",
        fontWeight: 700,
        border: "none",
        cursor: "pointer"
      }}
      onClick={handleClearCanvas}
    >
      Clear Canvas (Owner Only)
    </button>
  );

  const renderRoomMembers = () => {
    const myName = currentUser?.fullName || currentUser?.email || "anonymous";
    const members = [
      { name: myName, tool: myCursor.tool || 'brush' },
      ...Object.values(remoteCursors)
        .reduce((arr, c) => {
          if (c.name && !arr.some(item => item.name === c.name)) arr.push(c);
          return arr;
        }, [])
        .sort((a, b) => a.name.localeCompare(b.name))
    ];
    return (
      <div style={{
        marginBottom: 10,
        background: '#f7fafc',
        padding: '8px 24px',
        borderRadius: 8,
        fontWeight: 500,
        fontSize: 16,
        minWidth: 200,
        boxShadow: '0 2px 8px #e1e1e1'
      }}>
        <div style={{marginBottom: 8, fontWeight: 700}}>Members online</div>
        <ul style={{listStyle: "none", padding: 0, margin: 0}}>
          {members.map((m, i) => (
            <li key={m.name + i} style={{margin: "3px 0", display: "flex", alignItems: "center"}}>
              <span style={{fontWeight: i === 0 ? 700 : 500, color: i === 0 ? "#2b6cb0" : "#2d3748"}}>
                {m.name}
              </span>
              <span style={{marginLeft: 10, fontSize: 14, color: "#718096"}}>
                {TOOL_LABELS[m.tool] || m.tool}
              </span>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const renderOtherCursors = () =>
    Object.entries(remoteCursors).map(([uid, c]) =>
      c.x != null && c.y != null ? (
        <div
          key={uid}
          style={{
            position: 'absolute',
            left: c.x,
            top: c.y,
            pointerEvents: 'none',
            zIndex: 10,
            transform: 'translate(-50%, -75%)'
          }}
        >
          <div
            style={{
              background: '#fff',
              border: `2px solid ${c.color || '#3182ce'}`,
              borderRadius: 10,
              padding: '1px 8px',
              fontSize: 14,
              minWidth: 24,
              color: '#2d3748',
              boxShadow: '0 0 8px #bbb5'
            }}
          >
            {c.name ? c.name.split('@')[0] : uid} <span style={{marginLeft:7, fontWeight:400, fontSize:13, color:"#718096"}}>{TOOL_LABELS[c.tool] || c.tool}</span>
          </div>
          <div
            style={{
              width: 15,
              height: 15,
              background: c.color || '#3182ce',
              borderRadius: '50%',
              margin: '2px auto 0 auto',
              border: '2px solid #fff'
            }}
          />
        </div>
      ) : null
    );

  // Updated: Show red cursor and tooltip if blocked
  const renderMyCursor = () => (
    myCursor.x !== null && myCursor.y !== null && (
      <div
        style={{
          position: 'absolute',
          left: myCursor.x,
          top: myCursor.y,
          pointerEvents: 'none',
          zIndex: 100,
          transform: 'translate(-50%, -90%)'
        }}
      >
        <div style={{
          background: collision ? '#ffeaea' : '#fff',
          border: '2px solid ' + (collision ? '#ff384b' : color),
          borderRadius: 10,
          padding: '1px 8px',
          fontSize: 14,
          minWidth: 24,
          color: collision ? '#a11' : '#2d3748',
          boxShadow: '0 0 8px #bbb5'
        }}>
          {(currentUser?.fullName || currentUser?.email || "You").split('@')[0]}
          <span style={{marginLeft:7, fontWeight:400, fontSize:13, color:collision?'#a11':"#718096"}}>
            {TOOL_LABELS[myCursor.tool] || myCursor.tool}
          </span>
        </div>
        <div style={{
          width: 15, height: 15,
          background: collision ? '#ff384b' : color,
          borderRadius: '50%',
          margin: '2px auto 0 auto',
          border: '2px solid #fff'
        }}/>
        {collision && (
          <div style={{
            margin: '4px auto 0 auto',
            color: "#fff",
            background: "#ff384be6",
            padding: "2px 15px",
            borderRadius: 6,
            fontWeight: 700,
            fontSize: 13,
            textShadow: "0 1px 4px #9003"
          }}>
            Another user is drawing here!
          </div>
        )}
      </div>
    )
  );

  const renderUserInfo = () => (
    <div style={{
      width: '100%',
      marginBottom: 10,
      background: '#f4f6fa',
      padding: '10px 0',
      borderRadius: 8,
      fontWeight: 600,
      fontSize: 18,
      textAlign: 'center',
      boxShadow: '0 2px 8px #e1e1e1',
    }}>
      Logged in as: {currentUser?.fullName || currentUser?.username || currentUser?.email || 'Guest'}
    </div>
  );

  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18 }}>
      {renderUserInfo()}
      {renderRoomMembers()}
      {renderSnapshots()}
      <button
        style={{
          margin: "10px 0",
          padding: "6px 16px",
          fontSize: "16px",
          borderRadius: 8,
          background: "#3182ce",
          color: "#fff",
          fontWeight: 600,
          border: "none",
          cursor: "pointer",
        }}
        onClick={handleSaveCanvas}
      >
        Save Canvas State
      </button>
      {renderOwnerButtons()}
      <div className="canvas-toolbar">
        <span style={{ fontSize: 14 }}>Tool</span>
        <select
          value={tool}
          style={{ marginLeft: 8, padding: '3px 7px', borderRadius: 8, border: '1px solid #bbb', fontSize: 14 }}
          onChange={e => setTool(e.target.value)}
        >
          {TOOLS.map(t => (
            <option key={t.key} value={t.key}>{t.label}</option>
          ))}
        </select>
        <span style={{ fontSize: 14, marginLeft: 8 }}>Color</span>
        {COLORS.map(c =>
          <button
            key={c}
            className={'canvas-btn-color' + (color === c ? ' selected' : '')}
            style={{ background: c, border: color === c ? '2px solid #000' : '1px solid #bbb', marginLeft: 4, width: 24, height: 24, borderRadius: 6, cursor: 'pointer' }}
            onClick={() => { setColor(c); setTool('brush'); }}
          />
        )}
        <span style={{ fontSize: 14, marginLeft: 8 }}>Line</span>
        <select
          value={thickness}
          style={{ marginLeft: 8, padding: '3px 7px', borderRadius: 8, border: '1px solid #bbb', fontSize: 14 }}
          onChange={e => setThickness(Number(e.target.value))}
        >
          {THICKNESS.map(t =>
            <option key={t} value={t}>{t}px</option>
          )}
        </select>
      </div>
      <div style={{ position: 'relative', width: CANVAS_W, height: CANVAS_H, border: '2px solid #eee', borderRadius: 14, boxShadow: '0 8px 28px #3383f022' }}>
        <canvas
          ref={canvasRef}
          className="canvas-canvas-area"
          width={CANVAS_W}
          height={CANVAS_H}
          style={{ cursor: CURSORS[tool] || 'crosshair', borderRadius: 12, background: '#fcfcfc' }}
          onMouseDown={start}
          onMouseMove={move}
          onMouseUp={stop}
          onMouseLeave={stop}
        />
        {renderMyCursor()}
        {renderOtherCursors()}
      </div>
    </div>
  );
}

export default DrawingCanvas;
