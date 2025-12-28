"""
WebSocket Manager for Real-time Chat Features
Handles WebSocket connections, message broadcasting, and real-time updates
"""

import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from models import User, Conversation, Message
from database import get_db

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time chat"""
    
    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Conversation subscriptions: {conversation_id: {user_id: connection_ids}}
        self.conversation_subscriptions: Dict[str, Dict[str, Set[str]]] = {}
        # Typing indicators: {conversation_id: {user_id: timestamp}}
        self.typing_indicators: Dict[str, Dict[str, datetime]] = {}
        # Message delivery status: {message_id: {user_id: status}}
        self.message_status: Dict[str, Dict[str, str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        self.active_connections[user_id][connection_id] = websocket
        
        logger.info(f"WebSocket connected: user={user_id}, connection={connection_id}")
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "user_id": user_id,
            "connection_id": connection_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, websocket)
    
    def disconnect(self, user_id: str, connection_id: str):
        """Remove a WebSocket connection"""
        try:
            if user_id in self.active_connections:
                if connection_id in self.active_connections[user_id]:
                    del self.active_connections[user_id][connection_id]
                
                # Clean up empty user entry
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from conversation subscriptions
            for conv_id in list(self.conversation_subscriptions.keys()):
                if user_id in self.conversation_subscriptions[conv_id]:
                    if connection_id in self.conversation_subscriptions[conv_id][user_id]:
                        self.conversation_subscriptions[conv_id][user_id].discard(connection_id)
                    
                    # Clean up empty entries
                    if not self.conversation_subscriptions[conv_id][user_id]:
                        del self.conversation_subscriptions[conv_id][user_id]
                    
                    if not self.conversation_subscriptions[conv_id]:
                        del self.conversation_subscriptions[conv_id]
            
            # Clear typing indicators
            for conv_id in list(self.typing_indicators.keys()):
                if user_id in self.typing_indicators[conv_id]:
                    del self.typing_indicators[conv_id][user_id]
                    if not self.typing_indicators[conv_id]:
                        del self.typing_indicators[conv_id]
            
            logger.info(f"WebSocket disconnected: user={user_id}, connection={connection_id}")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
    
    async def send_to_user(self, message: dict, user_id: str):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected_connections = []
            
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send to user {user_id}, connection {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
            
            # Clean up disconnected connections
            for connection_id in disconnected_connections:
                self.disconnect(user_id, connection_id)
    
    async def subscribe_to_conversation(self, user_id: str, connection_id: str, conversation_id: str):
        """Subscribe a connection to conversation updates"""
        if conversation_id not in self.conversation_subscriptions:
            self.conversation_subscriptions[conversation_id] = {}
        
        if user_id not in self.conversation_subscriptions[conversation_id]:
            self.conversation_subscriptions[conversation_id][user_id] = set()
        
        self.conversation_subscriptions[conversation_id][user_id].add(connection_id)
        
        logger.info(f"User {user_id} subscribed to conversation {conversation_id}")
    
    async def unsubscribe_from_conversation(self, user_id: str, connection_id: str, conversation_id: str):
        """Unsubscribe a connection from conversation updates"""
        if (conversation_id in self.conversation_subscriptions and 
            user_id in self.conversation_subscriptions[conversation_id]):
            
            self.conversation_subscriptions[conversation_id][user_id].discard(connection_id)
            
            # Clean up empty entries
            if not self.conversation_subscriptions[conversation_id][user_id]:
                del self.conversation_subscriptions[conversation_id][user_id]
            
            if not self.conversation_subscriptions[conversation_id]:
                del self.conversation_subscriptions[conversation_id]
        
        logger.info(f"User {user_id} unsubscribed from conversation {conversation_id}")
    
    async def broadcast_to_conversation(self, message: dict, conversation_id: str, exclude_user: str = None):
        """Broadcast message to all subscribers of a conversation"""
        if conversation_id not in self.conversation_subscriptions:
            return
        
        for user_id, connection_ids in self.conversation_subscriptions[conversation_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            if user_id in self.active_connections:
                disconnected_connections = []
                
                for connection_id in connection_ids:
                    if connection_id in self.active_connections[user_id]:
                        try:
                            websocket = self.active_connections[user_id][connection_id]
                            await websocket.send_text(json.dumps(message))
                        except Exception as e:
                            logger.error(f"Failed to broadcast to {user_id}/{connection_id}: {e}")
                            disconnected_connections.append(connection_id)
                
                # Clean up disconnected connections
                for connection_id in disconnected_connections:
                    self.disconnect(user_id, connection_id)
    
    async def set_typing_indicator(self, user_id: str, conversation_id: str, is_typing: bool):
        """Set typing indicator for a user in a conversation"""
        if conversation_id not in self.typing_indicators:
            self.typing_indicators[conversation_id] = {}
        
        if is_typing:
            self.typing_indicators[conversation_id][user_id] = datetime.now(timezone.utc)
        else:
            if user_id in self.typing_indicators[conversation_id]:
                del self.typing_indicators[conversation_id][user_id]
        
        # Broadcast typing status to conversation subscribers
        await self.broadcast_to_conversation({
            "type": "typing_indicator",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "is_typing": is_typing,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, conversation_id, exclude_user=user_id)
    
    async def update_message_status(self, message_id: str, user_id: str, status: str):
        """Update message delivery/read status"""
        if message_id not in self.message_status:
            self.message_status[message_id] = {}
        
        self.message_status[message_id][user_id] = status
        
        # Broadcast status update
        await self.send_to_user({
            "type": "message_status_update",
            "message_id": message_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, user_id)
    
    async def broadcast_new_message(self, message: Message, conversation_id: str):
        """Broadcast new message to conversation subscribers"""
        message_data = {
            "type": "new_message",
            "conversation_id": conversation_id,
            "message": {
                "id": message.id,
                "content": message.content,
                "sender": message.sender,
                "timestamp": message.timestamp.isoformat(),
                "sequence_number": message.sequence_number,
                "ai_model": message.ai_model,
                "confidence_score": message.confidence_score,
                "emergency_flag": message.emergency_flag or False,
                "medical_analysis": message.medical_analysis
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast_to_conversation(message_data, conversation_id)
    
    async def broadcast_conversation_update(self, conversation: Conversation):
        """Broadcast conversation status updates"""
        update_data = {
            "type": "conversation_update",
            "conversation": {
                "id": conversation.id,
                "status": conversation.status,
                "last_message_at": conversation.last_message_at.isoformat(),
                "urgency_level": conversation.urgency_level,
                "emergency_detected": conversation.emergency_detected or False,
                "crisis_level": conversation.crisis_level,
                "total_messages": conversation.total_messages or 0
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await self.broadcast_to_conversation(update_data, conversation.id)
    
    def get_active_users(self) -> List[str]:
        """Get list of currently active user IDs"""
        return list(self.active_connections.keys())
    
    def get_conversation_subscribers(self, conversation_id: str) -> List[str]:
        """Get list of users subscribed to a conversation"""
        if conversation_id in self.conversation_subscriptions:
            return list(self.conversation_subscriptions[conversation_id].keys())
        return []
    
    async def cleanup_stale_typing_indicators(self):
        """Clean up old typing indicators (run periodically)"""
        current_time = datetime.now(timezone.utc)
        stale_threshold = 30  # seconds
        
        for conv_id in list(self.typing_indicators.keys()):
            for user_id in list(self.typing_indicators[conv_id].keys()):
                last_typing = self.typing_indicators[conv_id][user_id]
                if (current_time - last_typing).total_seconds() > stale_threshold:
                    # Remove stale typing indicator
                    del self.typing_indicators[conv_id][user_id]
                    
                    # Broadcast typing stopped
                    await self.broadcast_to_conversation({
                        "type": "typing_indicator",
                        "conversation_id": conv_id,
                        "user_id": user_id,
                        "is_typing": False,
                        "timestamp": current_time.isoformat()
                    }, conv_id, exclude_user=user_id)
            
            # Clean up empty conversation entries
            if not self.typing_indicators[conv_id]:
                del self.typing_indicators[conv_id]


# Global connection manager instance
connection_manager = ConnectionManager()


async def handle_websocket_message(websocket: WebSocket, user_id: str, connection_id: str, data: dict):
    """Handle incoming WebSocket messages"""
    try:
        message_type = data.get("type")
        
        if message_type == "subscribe_conversation":
            conversation_id = data.get("conversation_id")
            if conversation_id:
                await connection_manager.subscribe_to_conversation(user_id, connection_id, conversation_id)
                await connection_manager.send_personal_message({
                    "type": "subscription_confirmed",
                    "conversation_id": conversation_id
                }, websocket)
        
        elif message_type == "unsubscribe_conversation":
            conversation_id = data.get("conversation_id")
            if conversation_id:
                await connection_manager.unsubscribe_from_conversation(user_id, connection_id, conversation_id)
        
        elif message_type == "typing_start":
            conversation_id = data.get("conversation_id")
            if conversation_id:
                await connection_manager.set_typing_indicator(user_id, conversation_id, True)
        
        elif message_type == "typing_stop":
            conversation_id = data.get("conversation_id")
            if conversation_id:
                await connection_manager.set_typing_indicator(user_id, conversation_id, False)
        
        elif message_type == "message_read":
            message_id = data.get("message_id")
            if message_id:
                await connection_manager.update_message_status(message_id, user_id, "read")
        
        elif message_type == "ping":
            await connection_manager.send_personal_message({
                "type": "pong",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, websocket)
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await connection_manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, websocket)
    
    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": "Failed to process message"
        }, websocket)


# Background task to clean up stale typing indicators
async def cleanup_task():
    """Background task to clean up stale data"""
    while True:
        try:
            await connection_manager.cleanup_stale_typing_indicators()
            await asyncio.sleep(30)  # Run every 30 seconds
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.sleep(60)  # Wait longer on error