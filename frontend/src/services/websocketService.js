/**
 * WebSocket Service for Real-time Chat Features
 * Handles WebSocket connections, message broadcasting, and real-time updates
 */

class WebSocketService {
  constructor() {
    this.ws = null;
    this.userId = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // Start with 1 second
    this.listeners = new Map();
    this.subscriptions = new Set();
    this.typingTimeout = null;
  }

  /**
   * Connect to WebSocket server
   * @param {string} userId - User ID for the connection
   * @param {string} baseUrl - Base WebSocket URL (optional)
   */
  connect(userId, baseUrl = null) {
    if (this.isConnected && this.userId === userId) {
      console.log('WebSocket already connected for user:', userId);
      return Promise.resolve();
    }

    this.userId = userId;
    
    // Determine WebSocket URL
    const wsUrl = baseUrl || this.getWebSocketUrl();
    const fullUrl = `${wsUrl}/ws/${userId}`;

    console.log('Connecting to WebSocket:', fullUrl);

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(fullUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected successfully');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          
          // Emit connection event
          this.emit('connected', { userId });
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket connection closed:', event.code, event.reason);
          this.isConnected = false;
          
          // Emit disconnection event
          this.emit('disconnected', { code: event.code, reason: event.reason });
          
          // Attempt to reconnect if not a normal closure
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.emit('error', { error });
          
          if (!this.isConnected) {
            reject(error);
          }
        };

      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.ws) {
      this.isConnected = false;
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    // Clear typing timeout
    if (this.typingTimeout) {
      clearTimeout(this.typingTimeout);
      this.typingTimeout = null;
    }
    
    console.log('WebSocket disconnected');
  }

  /**
   * Schedule reconnection attempt
   */
  scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      this.emit('reconnect_failed');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
    
    setTimeout(() => {
      if (!this.isConnected && this.userId) {
        this.connect(this.userId).catch(error => {
          console.error('Reconnection failed:', error);
        });
      }
    }, delay);
  }

  /**
   * Send message to WebSocket server
   * @param {object} message - Message object to send
   */
  send(message) {
    if (!this.isConnected || !this.ws) {
      console.warn('WebSocket not connected, cannot send message:', message);
      return false;
    }

    try {
      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
      return false;
    }
  }

  /**
   * Subscribe to conversation updates
   * @param {string} conversationId - Conversation ID to subscribe to
   */
  subscribeToConversation(conversationId) {
    if (this.subscriptions.has(conversationId)) {
      return; // Already subscribed
    }

    this.send({
      type: 'subscribe_conversation',
      conversation_id: conversationId
    });

    this.subscriptions.add(conversationId);
    console.log('Subscribed to conversation:', conversationId);
  }

  /**
   * Unsubscribe from conversation updates
   * @param {string} conversationId - Conversation ID to unsubscribe from
   */
  unsubscribeFromConversation(conversationId) {
    if (!this.subscriptions.has(conversationId)) {
      return; // Not subscribed
    }

    this.send({
      type: 'unsubscribe_conversation',
      conversation_id: conversationId
    });

    this.subscriptions.delete(conversationId);
    console.log('Unsubscribed from conversation:', conversationId);
  }

  /**
   * Send typing indicator
   * @param {string} conversationId - Conversation ID
   * @param {boolean} isTyping - Whether user is typing
   */
  setTypingIndicator(conversationId, isTyping) {
    this.send({
      type: isTyping ? 'typing_start' : 'typing_stop',
      conversation_id: conversationId
    });

    // Auto-stop typing after 3 seconds of inactivity
    if (isTyping) {
      if (this.typingTimeout) {
        clearTimeout(this.typingTimeout);
      }
      
      this.typingTimeout = setTimeout(() => {
        this.setTypingIndicator(conversationId, false);
      }, 3000);
    }
  }

  /**
   * Mark message as read
   * @param {string} messageId - Message ID to mark as read
   */
  markMessageAsRead(messageId) {
    this.send({
      type: 'message_read',
      message_id: messageId
    });
  }

  /**
   * Send ping to keep connection alive
   */
  ping() {
    this.send({
      type: 'ping'
    });
  }

  /**
   * Handle incoming WebSocket messages
   * @param {object} data - Parsed message data
   */
  handleMessage(data) {
    const { type } = data;

    switch (type) {
      case 'connection_established':
        console.log('Connection established:', data);
        break;

      case 'subscription_confirmed':
        console.log('Subscription confirmed for conversation:', data.conversation_id);
        break;

      case 'new_message':
        this.emit('new_message', data);
        break;

      case 'conversation_update':
        this.emit('conversation_update', data);
        break;

      case 'typing_indicator':
        this.emit('typing_indicator', data);
        break;

      case 'message_reaction':
        this.emit('message_reaction', data);
        break;

      case 'message_rating':
        this.emit('message_rating', data);
        break;

      case 'message_status_update':
        this.emit('message_status_update', data);
        break;

      case 'pong':
        console.log('Pong received');
        break;

      case 'error':
        console.error('WebSocket error message:', data.message);
        this.emit('error', data);
        break;

      default:
        console.log('Unknown message type:', type, data);
    }
  }

  /**
   * Add event listener
   * @param {string} event - Event name
   * @param {function} callback - Callback function
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  /**
   * Remove event listener
   * @param {string} event - Event name
   * @param {function} callback - Callback function
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  /**
   * Emit event to listeners
   * @param {string} event - Event name
   * @param {object} data - Event data
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in event listener:', error);
        }
      });
    }
  }

  /**
   * Get WebSocket URL based on current location
   * @returns {string} WebSocket URL
   */
  getWebSocketUrl() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = process.env.NODE_ENV === 'development' ? ':8000' : '';
    
    return `${protocol}//${host}${port}`;
  }

  /**
   * Get connection status
   * @returns {object} Connection status information
   */
  getStatus() {
    return {
      isConnected: this.isConnected,
      userId: this.userId,
      reconnectAttempts: this.reconnectAttempts,
      subscriptions: Array.from(this.subscriptions)
    };
  }

  /**
   * Start periodic ping to keep connection alive
   */
  startHeartbeat(interval = 30000) {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.ping();
      }
    }, interval);
  }

  /**
   * Stop periodic ping
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

export default websocketService;