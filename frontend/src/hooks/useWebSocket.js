/**
 * React Hook for WebSocket Real-time Features
 * Provides easy integration with WebSocket service in React components
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import websocketService from '../services/websocketService';

/**
 * Hook for managing WebSocket connection
 * @param {string} userId - User ID for the connection
 * @param {object} options - Configuration options
 * @returns {object} WebSocket state and methods
 */
export const useWebSocket = (userId, options = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionError, setConnectionError] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const isInitialized = useRef(false);

  const {
    autoConnect = true,
    enableHeartbeat = true,
    heartbeatInterval = 30000
  } = options;

  // Connect to WebSocket
  const connect = useCallback(async () => {
    if (!userId) {
      console.warn('Cannot connect WebSocket without userId');
      return;
    }

    try {
      setConnectionError(null);
      await websocketService.connect(userId);
      
      if (enableHeartbeat) {
        websocketService.startHeartbeat(heartbeatInterval);
      }
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      setConnectionError(error.message || 'Connection failed');
    }
  }, [userId, enableHeartbeat, heartbeatInterval]);

  // Disconnect from WebSocket
  const disconnect = useCallback(() => {
    websocketService.disconnect();
    websocketService.stopHeartbeat();
  }, []);

  // Setup event listeners
  useEffect(() => {
    const handleConnected = () => {
      setIsConnected(true);
      setConnectionError(null);
      setReconnectAttempts(0);
    };

    const handleDisconnected = () => {
      setIsConnected(false);
    };

    const handleError = (data) => {
      setConnectionError(data.error?.message || 'WebSocket error');
    };

    const handleReconnectFailed = () => {
      setConnectionError('Failed to reconnect after multiple attempts');
    };

    // Add event listeners
    websocketService.on('connected', handleConnected);
    websocketService.on('disconnected', handleDisconnected);
    websocketService.on('error', handleError);
    websocketService.on('reconnect_failed', handleReconnectFailed);

    // Cleanup event listeners
    return () => {
      websocketService.off('connected', handleConnected);
      websocketService.off('disconnected', handleDisconnected);
      websocketService.off('error', handleError);
      websocketService.off('reconnect_failed', handleReconnectFailed);
    };
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect && userId && !isInitialized.current) {
      isInitialized.current = true;
      connect();
    }

    // Cleanup on unmount
    return () => {
      if (isInitialized.current) {
        disconnect();
      }
    };
  }, [userId, autoConnect, connect, disconnect]);

  return {
    isConnected,
    connectionError,
    reconnectAttempts,
    connect,
    disconnect,
    websocketService
  };
};

/**
 * Hook for conversation-specific WebSocket features
 * @param {string} conversationId - Conversation ID
 * @param {object} options - Configuration options
 * @returns {object} Conversation WebSocket state and methods
 */
export const useConversationWebSocket = (conversationId, options = {}) => {
  const [messages, setMessages] = useState([]);
  const [typingUsers, setTypingUsers] = useState(new Set());
  const [conversationUpdates, setConversationUpdates] = useState(null);
  const isSubscribed = useRef(false);

  const {
    autoSubscribe = true,
    onNewMessage,
    onTypingIndicator,
    onConversationUpdate
  } = options;

  // Subscribe to conversation
  const subscribe = useCallback(() => {
    if (conversationId && !isSubscribed.current) {
      websocketService.subscribeToConversation(conversationId);
      isSubscribed.current = true;
    }
  }, [conversationId]);

  // Unsubscribe from conversation
  const unsubscribe = useCallback(() => {
    if (conversationId && isSubscribed.current) {
      websocketService.unsubscribeFromConversation(conversationId);
      isSubscribed.current = false;
    }
  }, [conversationId]);

  // Send typing indicator
  const setTyping = useCallback((isTyping) => {
    if (conversationId) {
      websocketService.setTypingIndicator(conversationId, isTyping);
    }
  }, [conversationId]);

  // Mark message as read
  const markAsRead = useCallback((messageId) => {
    websocketService.markMessageAsRead(messageId);
  }, []);

  // Setup conversation event listeners
  useEffect(() => {
    const handleNewMessage = (data) => {
      if (data.conversation_id === conversationId) {
        const newMessage = data.message;
        setMessages(prev => [...prev, newMessage]);
        
        if (onNewMessage) {
          onNewMessage(newMessage);
        }
      }
    };

    const handleTypingIndicator = (data) => {
      if (data.conversation_id === conversationId) {
        setTypingUsers(prev => {
          const newSet = new Set(prev);
          if (data.is_typing) {
            newSet.add(data.user_id);
          } else {
            newSet.delete(data.user_id);
          }
          return newSet;
        });

        if (onTypingIndicator) {
          onTypingIndicator(data);
        }
      }
    };

    const handleConversationUpdate = (data) => {
      if (data.conversation?.id === conversationId) {
        setConversationUpdates(data.conversation);
        
        if (onConversationUpdate) {
          onConversationUpdate(data.conversation);
        }
      }
    };

    // Add event listeners
    websocketService.on('new_message', handleNewMessage);
    websocketService.on('typing_indicator', handleTypingIndicator);
    websocketService.on('conversation_update', handleConversationUpdate);

    // Cleanup event listeners
    return () => {
      websocketService.off('new_message', handleNewMessage);
      websocketService.off('typing_indicator', handleTypingIndicator);
      websocketService.off('conversation_update', handleConversationUpdate);
    };
  }, [conversationId, onNewMessage, onTypingIndicator, onConversationUpdate]);

  // Auto-subscribe on mount
  useEffect(() => {
    if (autoSubscribe && conversationId) {
      subscribe();
    }

    // Cleanup on unmount or conversation change
    return () => {
      unsubscribe();
    };
  }, [conversationId, autoSubscribe, subscribe, unsubscribe]);

  return {
    messages,
    typingUsers: Array.from(typingUsers),
    conversationUpdates,
    subscribe,
    unsubscribe,
    setTyping,
    markAsRead
  };
};

/**
 * Hook for message reactions and ratings
 * @returns {object} Message interaction methods
 */
export const useMessageInteractions = () => {
  const [reactions, setReactions] = useState(new Map());
  const [ratings, setRatings] = useState(new Map());

  // Setup message interaction event listeners
  useEffect(() => {
    const handleMessageReaction = (data) => {
      setReactions(prev => {
        const newMap = new Map(prev);
        newMap.set(data.message_id, {
          reaction: data.reaction,
          user_id: data.user_id,
          timestamp: data.timestamp
        });
        return newMap;
      });
    };

    const handleMessageRating = (data) => {
      setRatings(prev => {
        const newMap = new Map(prev);
        newMap.set(data.message_id, {
          rating: data.rating,
          feedback: data.feedback,
          user_id: data.user_id,
          timestamp: data.timestamp
        });
        return newMap;
      });
    };

    // Add event listeners
    websocketService.on('message_reaction', handleMessageReaction);
    websocketService.on('message_rating', handleMessageRating);

    // Cleanup event listeners
    return () => {
      websocketService.off('message_reaction', handleMessageReaction);
      websocketService.off('message_rating', handleMessageRating);
    };
  }, []);

  return {
    reactions,
    ratings
  };
};

/**
 * Hook for WebSocket connection status
 * @returns {object} Connection status information
 */
export const useWebSocketStatus = () => {
  const [status, setStatus] = useState(websocketService.getStatus());

  useEffect(() => {
    const updateStatus = () => {
      setStatus(websocketService.getStatus());
    };

    // Update status on connection events
    websocketService.on('connected', updateStatus);
    websocketService.on('disconnected', updateStatus);

    // Periodic status updates
    const interval = setInterval(updateStatus, 5000);

    return () => {
      websocketService.off('connected', updateStatus);
      websocketService.off('disconnected', updateStatus);
      clearInterval(interval);
    };
  }, []);

  return status;
};