import React, { useRef, useEffect, useState } from 'react';
import Peer from 'simple-peer';
import './VideoCall.css';

function VideoCall({ roomId, token, currentUser, wsUrl, isMinimized, onToggleMinimize, onClose }) {
  const [peers, setPeers] = useState({});
  const [localStream, setLocalStream] = useState(null);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoOff, setIsVideoOff] = useState(false);
  const [error, setError] = useState(null);
  const [userLeftNotification, setUserLeftNotification] = useState(null);

  const localVideoRef = useRef();
  const peerRefs = useRef({});
  const wsRef = useRef(null);

  useEffect(() => {
    const initVideoCall = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 640, height: 480 },
          audio: true
        });

        setLocalStream(stream);

        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }

        connectToSignaling(stream);
      } catch (err) {
        console.error('Error accessing media devices:', err);
        setError('Camera/microphone access denied. Please allow access and refresh.');
      }
    };

    initVideoCall();

    return () => {
      // Cleanup
      if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
      }
      Object.values(peerRefs.current).forEach(peer => {
        if (peer && peer.destroy) {
          peer.destroy();
        }
      });
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectToSignaling = (stream) => {
    const ws = new WebSocket(
      `${wsUrl}/webrtc/${roomId}?token=${encodeURIComponent(token)}`
    );
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('Connected to WebRTC signaling server');
      // Send join message with user info
      ws.send(JSON.stringify({
        type: 'join',
        userName: currentUser?.fullName || currentUser?.email || 'Anonymous',
        userId: currentUser?.email || currentUser?.user_id || 'anonymous'
      }));
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleSignalingMessage(message, stream);
      } catch (e) {
        console.error('Error parsing signaling message:', e);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please try again.');
    };

    ws.onclose = () => {
      console.log('Signaling connection closed');
    };
  };

  const handleSignalingMessage = (message, stream) => {
    switch (message.type) {
      case 'user-joined':
        createPeer(message.userId, message.userName, true, stream);
        break;

      case 'offer':
        handleOffer(message.fromUserId, message.userName, message.sdp, stream);
        break;

      case 'answer':
        handleAnswer(message.fromUserId, message.sdp);
        break;

      case 'ice-candidate':
        handleIceCandidate(message.fromUserId, message.candidate);
        break;

      case 'user-left':
        if (message.userName) {
          setUserLeftNotification(message.userName);
          setTimeout(() => setUserLeftNotification(null), 4000);
        }
        removePeer(message.userId);
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const createPeer = (userId, userName, initiator, stream) => {
    if (peerRefs.current[userId]) {
      console.log('Peer already exists:', userId);
      return;
    }

    const peer = new Peer({
      initiator,
      trickle: false,
      stream,
      config: {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:global.stun.twilio.com:3478' }
        ]
      }
    });

    peer.on('signal', (signal) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: initiator ? 'offer' : 'answer',
          targetUserId: userId,
          userName: currentUser?.fullName || currentUser?.email || 'Anonymous',
          sdp: signal
        }));
      }
    });

    peer.on('stream', (remoteStream) => {
      console.log('Received stream from user:', userId);
      setPeers(prev => ({
        ...prev,
        [userId]: { 
          stream: remoteStream, 
          userId,
          userName: userName || userId 
        }
      }));
    });

    peer.on('error', (err) => {
      console.error('Peer error:', err);
    });

    peer.on('close', () => {
      console.log('Peer connection closed:', userId);
      removePeer(userId);
    });

    peerRefs.current[userId] = peer;
  };

  const handleOffer = (userId, userName, offerSignal, stream) => {
    const peer = new Peer({
      initiator: false,
      trickle: false,
      stream,
      config: {
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'stun:global.stun.twilio.com:3478' }
        ]
      }
    });

    peer.on('signal', (signal) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'answer',
          targetUserId: userId,
          userName: currentUser?.fullName || currentUser?.email || 'Anonymous',
          sdp: signal
        }));
      }
    });

    peer.on('stream', (remoteStream) => {
      console.log('Received stream from user:', userId);
      setPeers(prev => ({
        ...prev,
        [userId]: { 
          stream: remoteStream, 
          userId,
          userName: userName || userId 
        }
      }));
    });

    peer.on('error', (err) => {
      console.error('Peer error:', err);
    });

    peer.signal(offerSignal);
    peerRefs.current[userId] = peer;
  };

  const handleAnswer = (userId, answerSignal) => {
    const peer = peerRefs.current[userId];
    if (peer) {
      peer.signal(answerSignal);
    }
  };

  const handleIceCandidate = (userId, candidate) => {
    const peer = peerRefs.current[userId];
    if (peer) {
      peer.signal(candidate);
    }
  };

  const removePeer = (userId) => {
    if (peerRefs.current[userId]) {
      if (peerRefs.current[userId].destroy) {
        peerRefs.current[userId].destroy();
      }
      delete peerRefs.current[userId];
    }
    setPeers(prev => {
      const newPeers = { ...prev };
      delete newPeers[userId];
      return newPeers;
    });
  };

  const toggleMute = () => {
    if (localStream) {
      localStream.getAudioTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsMuted(!isMuted);
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      localStream.getVideoTracks().forEach(track => {
        track.enabled = !track.enabled;
      });
      setIsVideoOff(!isVideoOff);
    }
  };

  const handleEndCall = () => {
    // Send leave message with user name
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ 
        type: 'leave',
        userName: currentUser?.fullName || currentUser?.email || 'User'
      }));
    }

    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
    }

    Object.values(peerRefs.current).forEach(peer => {
      if (peer && peer.destroy) {
        peer.destroy();
      }
    });

    onClose();
  };

  if (error) {
    return (
      <div className="video-call-error">
        <div className="error-message">
          <h3>❌ {error}</h3>
          <button onClick={onClose} className="close-error-btn">Close</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`video-call-container ${isMinimized ? 'minimized' : ''}`}>
      <div className="video-header" onClick={onToggleMinimize}>
        <h3>📹 Video Call</h3>
        <button className="toggle-btn">{isMinimized ? '▲' : '▼'}</button>
      </div>

      {userLeftNotification && (
        <div className="user-left-notification">
          {userLeftNotification} left the call
        </div>
      )}

      {!isMinimized && (
        <>
          <div className="video-grid">
            <div className="video-wrapper local-video">
              <video
                ref={localVideoRef}
                autoPlay
                muted
                playsInline
                className="video-element"
              />
              <div className="video-label">
                {currentUser?.fullName || currentUser?.email || 'You'} {isMuted && '🔇'} {isVideoOff && '📷'}
              </div>
            </div>

            {Object.entries(peers).map(([userId, peerData]) => (
              <RemoteVideo key={userId} peerData={peerData} />
            ))}

            {Object.keys(peers).length === 0 && (
              <div className="waiting-message">
                <p>⏳ Waiting for others to join...</p>
              </div>
            )}
          </div>

          <div className="video-controls">
            <button
              onClick={toggleMute}
              className={`control-btn ${isMuted ? 'muted' : ''}`}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? '🔇' : '🔊'} {isMuted ? 'Unmute' : 'Mute'}
            </button>

            <button
              onClick={toggleVideo}
              className={`control-btn ${isVideoOff ? 'video-off' : ''}`}
              title={isVideoOff ? 'Turn Video On' : 'Turn Video Off'}
            >
              {isVideoOff ? '📹' : '📷'} {isVideoOff ? 'Video On' : 'Video Off'}
            </button>

            <button onClick={handleEndCall} className="control-btn end-call-btn">
              ❌ End Call
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function RemoteVideo({ peerData }) {
  const videoRef = useRef();

  useEffect(() => {
    if (videoRef.current && peerData.stream) {
      videoRef.current.srcObject = peerData.stream;
    }
  }, [peerData.stream]);

  return (
    <div className="video-wrapper remote-video">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        className="video-element"
      />
      <div className="video-label">
        {peerData.userName || `User ${peerData.userId}`}
      </div>
    </div>
  );
}

export default VideoCall;
