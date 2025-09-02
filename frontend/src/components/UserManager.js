import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

function UserManager({ users, onUsersChange, currentUser }) {
  const [newUsername, setNewUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const createUser = async (e) => {
    e.preventDefault();
    if (!newUsername.trim()) return;

    setLoading(true);
    try {
      await axios.post(`${API_BASE}/users/`, {
        username: newUsername.trim()
      });
      setNewUsername('');
      setMessage('User created successfully!');
      onUsersChange();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Error creating user');
      setTimeout(() => setMessage(''), 3000);
    }
    setLoading(false);
  };

  return (
    <div className="component-card">
      <h2>👥 User Management</h2>
      
      <form onSubmit={createUser}>
        <div className="form-group">
          <input
            type="text"
            placeholder="Enter username"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating...' : 'Create User'}
          </button>
        </div>
      </form>

      {message && (
        <div className={message.includes('Error') ? 'error-message' : 'success-message'}>
          {message}
        </div>
      )}

      <div className="users-grid">
        {users.map(user => (
          <div 
            key={user.id} 
            className={`user-card ${currentUser?.id === user.id ? 'current' : ''}`}
          >
            <h3>{user.username}</h3>
            <p>ID: {user.id}</p>
            {currentUser?.id === user.id && (
              <span className="status-badge status-accepted">Current User</span>
            )}
          </div>
        ))}
      </div>

      {users.length === 0 && (
        <p style={{ textAlign: 'center', color: '#666', marginTop: '2rem' }}>
          No users yet. Create some users to get started!
        </p>
      )}
    </div>
  );
}

export default UserManager;
