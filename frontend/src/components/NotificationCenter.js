import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

function NotificationCenter({ currentUser }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch notifications
  const fetchNotifications = async () => {
    if (!currentUser) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/notifications/`, {
        params: { user_id: currentUser.id, limit: 20 }
      });
      setNotifications(response.data.notifications);
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
    setLoading(false);
  };

  // Mark notifications as read
  const markAsRead = async (notificationIds) => {
    if (!currentUser || notificationIds.length === 0) return;
    
    try {
      await axios.put(`${API_BASE}/notifications/mark-read`, 
        { notification_ids: notificationIds },
        { params: { user_id: currentUser.id } }
      );
      
      // Update local state
      setNotifications(prev => 
        prev.map(notif => 
          notificationIds.includes(notif.id) 
            ? { ...notif, is_read: true }
            : notif
        )
      );
      setUnreadCount(prev => Math.max(0, prev - notificationIds.length));
    } catch (error) {
      console.error('Error marking notifications as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    if (!currentUser) return;
    
    try {
      await axios.put(`${API_BASE}/notifications/mark-all-read`, null, {
        params: { user_id: currentUser.id }
      });
      
      setNotifications(prev => prev.map(notif => ({ ...notif, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId) => {
    if (!currentUser) return;
    
    try {
      await axios.delete(`${API_BASE}/notifications/${notificationId}`, {
        params: { user_id: currentUser.id }
      });
      
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
      setUnreadCount(prev => {
        const notification = notifications.find(n => n.id === notificationId);
        return notification && !notification.is_read ? prev - 1 : prev;
      });
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  // Format time
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffMinutes < 1) return 'Just now';
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return date.toLocaleDateString();
  };

  // Fetch notifications on component mount and user change
  useEffect(() => {
    fetchNotifications();
  }, [currentUser]);

  // Auto-refresh notifications every 30 seconds
  useEffect(() => {
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, [currentUser]);

  if (!currentUser) {
    return null;
  }

  return (
    <div className="notification-center">
      {/* Notification Bell */}
      <div className="notification-bell" onClick={() => setShowNotifications(!showNotifications)}>
        <span style={{ fontSize: '1.5rem', cursor: 'pointer' }}>🔔</span>
        {unreadCount > 0 && (
          <span className="notification-badge" style={{
            position: 'absolute',
            top: '-5px',
            right: '-5px',
            backgroundColor: '#ff4757',
            color: 'white',
            borderRadius: '50%',
            padding: '2px 6px',
            fontSize: '0.7rem',
            minWidth: '18px',
            textAlign: 'center'
          }}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </div>

      {/* Notification Panel */}
      {showNotifications && (
        <div className="notification-panel" style={{
          position: 'absolute',
          top: '100%',
          right: '0',
          width: '350px',
          maxHeight: '400px',
          backgroundColor: 'white',
          border: '1px solid #ddd',
          borderRadius: '8px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          zIndex: 1000,
          overflow: 'hidden'
        }}>
          {/* Header */}
          <div style={{
            padding: '1rem',
            borderBottom: '1px solid #eee',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <h3 style={{ margin: 0, fontSize: '1rem' }}>Notifications</h3>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {unreadCount > 0 && (
                <button 
                  onClick={markAllAsRead}
                  style={{
                    fontSize: '0.7rem',
                    padding: '0.25rem 0.5rem',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Mark all read
                </button>
              )}
              <button 
                onClick={fetchNotifications}
                style={{
                  fontSize: '0.7rem',
                  padding: '0.25rem 0.5rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Refresh
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {loading ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
                Loading...
              </div>
            ) : notifications.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
                No notifications yet
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  style={{
                    padding: '0.75rem',
                    borderBottom: '1px solid #f0f0f0',
                    backgroundColor: notification.is_read ? 'white' : '#f8f9fa',
                    cursor: 'pointer'
                  }}
                  onClick={() => !notification.is_read && markAsRead([notification.id])}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ 
                        fontWeight: notification.is_read ? 'normal' : 'bold',
                        fontSize: '0.9rem',
                        marginBottom: '0.25rem'
                      }}>
                        {notification.title}
                      </div>
                      <div style={{ 
                        fontSize: '0.8rem',
                        color: '#666',
                        marginBottom: '0.25rem'
                      }}>
                        {notification.message}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: '#999' }}>
                        {formatTime(notification.created_at)}
                        {notification.related_user_username && (
                          <span> • from {notification.related_user_username}</span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNotification(notification.id);
                      }}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#999',
                        cursor: 'pointer',
                        fontSize: '1rem',
                        padding: '0.25rem'
                      }}
                    >
                      ×
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationCenter;
