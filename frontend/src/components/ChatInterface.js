import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE = 'ws://localhost:8000/api/v1';

function ChatInterface({ currentUser, connections }) {
  const [selectedUser, setSelectedUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Use refs to store current values for WebSocket handlers
  const currentUserRef = useRef(currentUser);
  const selectedUserRef = useRef(selectedUser);
  
  // Update refs when state changes
  useEffect(() => {
    currentUserRef.current = currentUser;
  }, [currentUser]);
  
  useEffect(() => {
    selectedUserRef.current = selectedUser;
  }, [selectedUser]);

  // Request notification permission
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket connection
  useEffect(() => {
    if (!currentUser) return;

    console.log('Initializing WebSocket connection for user:', currentUser.id);
    const websocket = new WebSocket(`${WS_BASE}/chat/ws/${currentUser.id}`);
    
    websocket.onopen = () => {
      console.log('WebSocket connected successfully for user:', currentUser.id);
      setIsConnected(true);
      setWs(websocket);
    };

    websocket.onmessage = (event) => {
      console.log('Raw WebSocket message received:', event.data);
      
      try {
        const data = JSON.parse(event.data);
        console.log('Parsed WebSocket message:', data);
        
        if (data.type === 'message') {
          console.log('Processing chat message');
          const currentUserId = currentUserRef.current?.id;
          const selectedUserId = selectedUserRef.current?.id;
          
          console.log('Current user ID:', currentUserId);
          console.log('Selected user ID:', selectedUserId);
          console.log('Message sender ID:', data.sender_id);
          console.log('Message receiver ID:', data.receiver_id);
          
          // Check if this message involves the current user
          const isForCurrentUser = (data.sender_id === currentUserId || data.receiver_id === currentUserId);
          console.log('Is for current user:', isForCurrentUser);
          
          if (isForCurrentUser) {
            const otherUserId = data.sender_id === currentUserId ? data.receiver_id : data.sender_id;
            console.log('Other user ID:', otherUserId);
            console.log('Selected user ID from ref:', selectedUserId);
            
            // If we have a selected user and this message is for that chat, add it
            if (selectedUserId && selectedUserId === otherUserId) {
              console.log('✅ Adding message to current chat');
              
              const newMessage = {
                id: data.message_id,
                sender_id: data.sender_id,
                receiver_id: data.receiver_id,
                content: data.content,
                created_at: data.timestamp
              };
              
              setMessages(prevMessages => {
                const exists = prevMessages.some(msg => msg.id === data.message_id);
                if (exists) {
                  console.log('Message already exists, skipping');
                  return prevMessages;
                }
                
                console.log('Adding new message to chat array');
                return [...prevMessages, newMessage];
              });
            } else {
              console.log('❌ Message rejected - selectedUserId:', selectedUserId, 'otherUserId:', otherUserId);
              console.log('Message is for current user but different chat or no chat selected');
            }
          } else {
            console.log('❌ Message not for current user');
          }
        } else if (data.type === 'message_sent') {
          console.log('Message sent confirmation:', data);
        } else if (data.type === 'notification') {
          console.log('Received notification:', data);
          // Show a simple notification (you could make this more sophisticated)
          if (Notification.permission === 'granted') {
            new Notification(data.title, {
              body: data.message,
              icon: '/favicon.ico'
            });
          }
        } else if (data.type === 'error') {
          console.error('WebSocket error:', data.message);
          alert('Chat error: ' + data.message);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    websocket.onclose = (event) => {
      console.log('WebSocket disconnected. Code:', event.code, 'Reason:', event.reason);
      setIsConnected(false);
      setWs(null);
      
      // Try to reconnect after a delay if it wasn't a clean close
      if (event.code !== 1000 && currentUser) {
        console.log('Unexpected disconnect. Attempting to reconnect in 3 seconds...');
        setTimeout(() => {
          if (currentUser) {
            console.log('Reconnecting WebSocket...');
            // This will trigger a new connection
            const newWebsocket = new WebSocket(`${WS_BASE}/chat/ws/${currentUser.id}`);
            newWebsocket.onopen = () => {
              console.log('WebSocket reconnected successfully');
              setIsConnected(true);
              setWs(newWebsocket);
            };
            newWebsocket.onclose = websocket.onclose;
            newWebsocket.onerror = websocket.onerror;
            newWebsocket.onmessage = websocket.onmessage;
          }
        }, 3000);
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    return () => {
      console.log('Cleaning up WebSocket connection');
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.close(1000, 'Component unmounting');
      }
    };
  }, [currentUser?.id]); // Only depend on currentUser.id to avoid unnecessary reconnections

  // Auto-load chat history when user is selected
  useEffect(() => {
    if (selectedUser && currentUser) {
      loadChatHistory();
    }
  }, [selectedUser, currentUser]);

  const loadChatHistory = async () => {
    if (!selectedUser || !currentUser) return;
    
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_BASE}/chat/history/${selectedUser.id}?current_user_id=${currentUser.id}&limit=50`
      );
      setMessages(response.data.messages.map(msg => ({...msg, isRealTime: false})));
    } catch (error) {
      console.error('Error fetching chat history:', error);
      if (error.response?.status === 403) {
        alert('You can only chat with connected users');
      } else {
        alert('Error loading chat history: ' + (error.response?.data?.detail || error.message));
      }
    }
    setLoading(false);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedUser || !ws || !isConnected) return;

    const messageData = {
      receiver_id: selectedUser.id,
      content: newMessage.trim()
    };

    try {
      console.log('Sending message via WebSocket:', messageData);
      // Send via WebSocket
      ws.send(JSON.stringify(messageData));
      
      // Clear the input immediately
      setNewMessage('');
      
      // Note: We don't add a local message here anymore since the WebSocket 
      // will send it back to us immediately, ensuring consistent message ordering
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message');
    }
  };

  const sendMessageHTTP = async () => {
    if (!newMessage.trim() || !selectedUser) return;

    try {
      const response = await axios.post(
        `${API_BASE}/chat/send?sender_id=${currentUser.id}`,
        {
          receiver_id: selectedUser.id,
          content: newMessage.trim()
        }
      );

      const sentMessage = {
        ...response.data,
        isRealTime: true
      };
      setMessages(prev => [...prev, sentMessage]);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message via HTTP:', error);
      alert('Error sending message: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleUserSelect = (user) => {
    console.log('User selected:', user);
    setSelectedUser(user);
    setMessages([]); // Clear messages when switching users
    console.log('Selected user updated to:', user.id);
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (!currentUser) {
    return (
      <div className="component-card">
        <h2>💬 Chat Interface</h2>
        <p>Please select a current user to start chatting.</p>
      </div>
    );
  }

  return (
    <div className="component-card">
      <h2>💬 Chat Interface for {currentUser.username}</h2>
      
      <div style={{ marginBottom: '1rem' }}>
        <span style={{ 
          color: isConnected ? '#48bb78' : '#f56565',
          fontWeight: 'bold'
        }}>
          WebSocket: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </span>
      </div>

      <div className="chat-container">
        {/* Chat Sidebar */}
        <div className="chat-sidebar">
          <h3>Your Connections</h3>
          {connections.length === 0 ? (
            <p style={{ color: '#666' }}>No connections to chat with.</p>
          ) : (
            connections.map(user => (
              <div
                key={user.id}
                className={`connection-item ${selectedUser?.id === user.id ? 'selected' : ''}`}
                style={{ 
                  cursor: 'pointer',
                  backgroundColor: selectedUser?.id === user.id ? '#e6f3ff' : 'transparent'
                }}
                onClick={() => handleUserSelect(user)}
              >
                <span>
                  <span className="online-indicator"></span>
                  {user.username}
                </span>
              </div>
            ))
          )}
        </div>

        {/* Chat Main */}
        <div className="chat-main">
          {selectedUser ? (
            <>
              <div className="chat-header">
                <h3>Chat with {selectedUser.username}</h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  {loading && <span style={{ color: '#666' }}>Loading...</span>}
                  <button 
                    className="btn btn-secondary"
                    onClick={loadChatHistory}
                    style={{ fontSize: '0.8rem', padding: '0.5rem 1rem' }}
                    disabled={loading}
                  >
                    {loading ? 'Loading...' : 'Refresh'}
                  </button>
                </div>
              </div>

              <div className="chat-messages">
                {messages.length === 0 && !loading ? (
                  <p style={{ color: '#666', textAlign: 'center', marginTop: '2rem' }}>
                    No messages yet. Start the conversation!
                  </p>
                ) : (
                  messages.map((message, index) => {
                    const isSent = message.sender_id === currentUser.id;
                    return (
                      <div
                        key={`${message.id}-${index}`}
                        className={`message ${isSent ? 'sent' : 'received'}`}
                        style={{
                          opacity: message.isLocal ? 0.7 : 1, // Slightly fade local messages until confirmed
                        }}
                      >
                        <div>{message.content}</div>
                        <div className="message-time">
                          {formatTime(message.created_at)}
                          {message.isRealTime && <span> • Live</span>}
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              <form onSubmit={sendMessage} className="chat-input">
                <input
                  type="text"
                  placeholder="Type a message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                />
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={!newMessage.trim() || !isConnected}
                >
                  Send (WS)
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary"
                  onClick={sendMessageHTTP}
                  disabled={!newMessage.trim()}
                >
                  Send (HTTP)
                </button>
              </form>
            </>
          ) : (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              height: '100%',
              color: '#666'
            }}>
              Select a connection to start chatting
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatInterface;
