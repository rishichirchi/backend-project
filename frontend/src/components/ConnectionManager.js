import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

function ConnectionManager({ currentUser, users, connections, onConnectionsChange }) {
  const [selectedUserId, setSelectedUserId] = useState('');
  const [sentRequests, setSentRequests] = useState([]);
  const [receivedRequests, setReceivedRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchRequests = async () => {
    if (!currentUser) return;
    
    try {
      const [sentResponse, receivedResponse] = await Promise.all([
        axios.get(`${API_BASE}/users/${currentUser.id}/sent-requests`),
        axios.get(`${API_BASE}/users/${currentUser.id}/received-requests`)
      ]);
      setSentRequests(sentResponse.data);
      setReceivedRequests(receivedResponse.data);
    } catch (error) {
      console.error('Error fetching requests:', error);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [currentUser]);

  const sendConnectionRequest = async (e) => {
    e.preventDefault();
    if (!selectedUserId || !currentUser) return;

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/connections/send?sender_id=${currentUser.id}`, {
        receiver_id: parseInt(selectedUserId)
      });
      setSelectedUserId('');
      setMessage('Connection request sent!');
      fetchRequests();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Error sending request');
      setTimeout(() => setMessage(''), 3000);
    }
    setLoading(false);
  };

  const handleRequest = async (requestId, action) => {
    try {
      await axios.post(`${API_BASE}/connections/${requestId}/${action}`);
      setMessage(`Connection request ${action}ed!`);
      fetchRequests();
      onConnectionsChange();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(error.response?.data?.detail || `Error ${action}ing request`);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const availableUsers = users.filter(user => 
    user.id !== currentUser?.id && 
    !connections.some(conn => conn.id === user.id) &&
    !sentRequests.some(req => req.receiver_id === user.id && req.status === 'pending') &&
    !receivedRequests.some(req => req.sender_id === user.id && req.status === 'pending')
  );

  if (!currentUser) {
    return (
      <div className="component-card">
        <h2>🤝 Connection Management</h2>
        <p>Please select a current user to manage connections.</p>
      </div>
    );
  }

  return (
    <div className="component-card">
      <h2>🤝 Connection Management for {currentUser.username}</h2>

      {/* Send Connection Request */}
      <form onSubmit={sendConnectionRequest}>
        <div className="form-group">
          <select
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            disabled={loading}
          >
            <option value="">Select user to connect with</option>
            {availableUsers.map(user => (
              <option key={user.id} value={user.id}>
                {user.username} (ID: {user.id})
              </option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary" disabled={loading || !selectedUserId}>
            Send Request
          </button>
        </div>
      </form>

      {message && (
        <div className={message.includes('Error') ? 'error-message' : 'success-message'}>
          {message}
        </div>
      )}

      {/* Current Connections */}
      <h3>✅ Your Connections ({connections.length})</h3>
      <div className="connections-list">
        {connections.map(user => (
          <div key={user.id} className="connection-item">
            <span>
              <span className="online-indicator"></span>
              <strong>{user.username}</strong> (ID: {user.id})
            </span>
            <span className="status-badge status-accepted">Connected</span>
          </div>
        ))}
        {connections.length === 0 && (
          <p style={{ color: '#666' }}>No connections yet.</p>
        )}
      </div>

      {/* Received Requests */}
      <div className="requests-section">
        <h3>📩 Received Requests ({receivedRequests.filter(r => r.status === 'pending').length})</h3>
        {receivedRequests
          .filter(request => request.status === 'pending')
          .map(request => {
            const sender = users.find(u => u.id === request.sender_id);
            return (
              <div key={request.id} className="request-item">
                <span>
                  <strong>{sender?.username || 'Unknown'}</strong> wants to connect
                </span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    className="btn btn-success"
                    onClick={() => handleRequest(request.id, 'accept')}
                  >
                    Accept
                  </button>
                  <button 
                    className="btn btn-danger"
                    onClick={() => handleRequest(request.id, 'reject')}
                  >
                    Reject
                  </button>
                </div>
              </div>
            );
          })}
        {receivedRequests.filter(r => r.status === 'pending').length === 0 && (
          <p style={{ color: '#666' }}>No pending requests.</p>
        )}
      </div>

      {/* Sent Requests */}
      <div className="requests-section">
        <h3>📤 Sent Requests</h3>
        {sentRequests.map(request => {
          const receiver = users.find(u => u.id === request.receiver_id);
          return (
            <div key={request.id} className="request-item">
              <span>
                To <strong>{receiver?.username || 'Unknown'}</strong>
              </span>
              <span className={`status-badge status-${request.status}`}>
                {request.status}
              </span>
            </div>
          );
        })}
        {sentRequests.length === 0 && (
          <p style={{ color: '#666' }}>No sent requests.</p>
        )}
      </div>
    </div>
  );
}

export default ConnectionManager;
