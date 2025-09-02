import React, { useState, useEffect } from 'react';
import axios from 'axios';
import UserManager from './components/UserManager';
import ConnectionManager from './components/ConnectionManager';
import ChatInterface from './components/ChatInterface';
import NotificationCenter from './components/NotificationCenter';
import './App.css';

const API_BASE = 'http://localhost:8000/api/v1';

function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [connections, setConnections] = useState([]);
  const [activeTab, setActiveTab] = useState('users');

  // Fetch all users
  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE}/users/`);
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  // Fetch user connections
  const fetchConnections = async (userId) => {
    if (!userId) return;
    try {
      const response = await axios.get(`${API_BASE}/users/${userId}/connections`);
      setConnections(response.data);
    } catch (error) {
      console.error('Error fetching connections:', error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchConnections(currentUser.id);
    }
  }, [currentUser]);

  return (
    <div className="App">
      <header className="App-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <h1>🚀 BCommune Test Interface</h1>
          <div style={{ position: 'relative' }}>
            <NotificationCenter currentUser={currentUser} />
          </div>
        </div>
        <div className="user-selector">
          <label>Current User: </label>
          <select 
            value={currentUser?.id || ''} 
            onChange={(e) => {
              const userId = parseInt(e.target.value);
              const user = users.find(u => u.id === userId);
              setCurrentUser(user || null);
            }}
          >
            <option value="">Select a user</option>
            {users.map(user => (
              <option key={user.id} value={user.id}>
                {user.username} (ID: {user.id})
              </option>
            ))}
          </select>
        </div>
      </header>

      <nav className="tab-nav">
        <button 
          className={activeTab === 'users' ? 'active' : ''} 
          onClick={() => setActiveTab('users')}
        >
          👥 User Management
        </button>
        <button 
          className={activeTab === 'connections' ? 'active' : ''} 
          onClick={() => setActiveTab('connections')}
        >
          🤝 Connections
        </button>
        <button 
          className={activeTab === 'chat' ? 'active' : ''} 
          onClick={() => setActiveTab('chat')}
          disabled={!currentUser}
        >
          💬 Chat
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'users' && (
          <UserManager 
            users={users} 
            onUsersChange={fetchUsers}
            currentUser={currentUser}
          />
        )}
        
        {activeTab === 'connections' && (
          <ConnectionManager 
            currentUser={currentUser}
            users={users}
            connections={connections}
            onConnectionsChange={() => fetchConnections(currentUser?.id)}
          />
        )}
        
        {activeTab === 'chat' && currentUser && (
          <ChatInterface 
            currentUser={currentUser}
            connections={connections}
          />
        )}
      </main>
    </div>
  );
}

export default App;
