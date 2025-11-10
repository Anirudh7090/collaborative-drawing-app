import React, { useState, useEffect, useRef } from 'react';
import './LiveCaptions.css';

const CAPTION_DURATION = 35000; // 35 seconds display time

function LiveCaptions({ websocket, isEnabled, isMicEnabled, currentUser, isMinimized, onToggle }) {
  const [captions, setCaptions] = useState([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const recognitionRef = useRef(null);
  const captionsEndRef = useRef(null);

  
  useEffect(() => {
    if (captionsEndRef.current && !isMinimized) {
      captionsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [captions, currentTranscript, isMinimized]);

  // Auto-remove old captions after 35 seconds
  useEffect(() => {
    if (captions.length === 0) return;

    const timer = setInterval(() => {
      setCaptions(prev => {
        const now = Date.now();
        return prev.filter(caption => {
          const captionTime = new Date(caption.timestamp).getTime();
          return now - captionTime < CAPTION_DURATION;
        });
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [captions]);

  // Initialize speech recognition when mic is enabled
  useEffect(() => {
    if (!isMicEnabled) {
      // Stop recognition if mic disabled
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
      setCurrentTranscript('');
      return;
    }

    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error('Speech Recognition not supported in this browser');
      return;
    }

    // Create new recognition instance
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      setCurrentTranscript(interimTranscript);

      if (finalTranscript && websocket && websocket.readyState === WebSocket.OPEN) {
        const captionData = {
          text: finalTranscript.trim(),
          timestamp: new Date().toISOString()
        };

        setCaptions(prev => [...prev, {
          ...captionData,
          id: Date.now() + Math.random(),
          user: currentUser?.fullName || currentUser?.email || 'You',
          isOwn: true
        }]);

        websocket.send(JSON.stringify({
          type: 'caption',
          text: finalTranscript.trim()
        }));

        setCurrentTranscript('');
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      if (event.error === 'no-speech') {
        console.log('No speech detected, continuing...');
      } else if (event.error === 'aborted') {
        console.log('Recognition aborted, restarting...');
        setTimeout(() => {
          if (isMicEnabled && recognitionRef.current) {
            try {
              recognition.start();
            } catch (e) {
              console.log('Restart error:', e);
            }
          }
        }, 100);
      }
    };

    recognition.onend = () => {
      if (isMicEnabled && recognitionRef.current) {
        try {
          recognition.start();
        } catch (e) {
          console.log('Recognition restart error:', e);
        }
      }
    };

    try {
      recognition.start();
      recognitionRef.current = recognition;
      console.log('Speech recognition started');
    } catch (e) {
      console.error('Error starting recognition:', e);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
    };
  }, [isMicEnabled, websocket, currentUser]);

  // Listen for captions from other users
  useEffect(() => {
    if (!websocket) return;

    const handleMessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'caption' && data.data) {
          setCaptions(prev => [...prev, {
            text: data.data.text,
            user: data.data.user,
            timestamp: data.data.timestamp,
            id: Date.now() + Math.random(),
            isOwn: false
          }]);
        }
      } catch (e) {
        console.error('Error parsing caption:', e);
      }
    };

    websocket.addEventListener('message', handleMessage);

    return () => {
      websocket.removeEventListener('message', handleMessage);
    };
  }, [websocket]);

  // FIXED: Show panel when captions are enabled, regardless of mic status
  if (!isEnabled) return null;

  return (
    <div className={`live-captions-panel ${isMinimized ? 'minimized' : ''}`}>
      <div className="captions-header" onClick={onToggle}>
        <span className="captions-icon">💬</span>
        <h3>Live Captions</h3>
        <button className="toggle-btn">{isMinimized ? '▲' : '▼'}</button>
      </div>

      {!isMinimized && (
        <div className="captions-content">
          <div className="captions-status">
            {isMicEnabled ? (
              <span className="status-listening">🎤 Listening...</span>
            ) : (
              <span className="status-waiting">🔇 Mic is off - Turn on mic to start</span>
            )}
          </div>

          <div className="captions-messages">
            {captions.length === 0 && !currentTranscript ? (
              <div className="no-captions">
                <p>No captions yet</p>
                <p style={{ fontSize: '13px', color: '#a0aec0' }}>
                  {isMicEnabled ? 'Start speaking to see captions' : 'Enable mic to capture captions'}
                </p>
              </div>
            ) : (
              <>
                {captions.map((caption) => (
                  <div 
                    key={caption.id} 
                    className={`caption-message ${caption.isOwn ? 'own' : 'other'}`}
                  >
                    <div className="caption-header">
                      <span className="caption-user">{caption.user}</span>
                      <span className="caption-time">
                        {new Date(caption.timestamp).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </div>
                    <div className="caption-text">{caption.text}</div>
                  </div>
                ))}
                
                {currentTranscript && (
                  <div className="caption-message own interim">
                    <div className="caption-header">
                      <span className="caption-user">You</span>
                      <span className="caption-status">Speaking...</span>
                    </div>
                    <div className="caption-text">{currentTranscript}</div>
                  </div>
                )}
                
                <div ref={captionsEndRef} />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default LiveCaptions;
