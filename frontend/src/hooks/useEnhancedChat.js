import { useState, useEffect, useCallback } from 'react';
import { useChat } from './useChat';
import responseFormatterService from '../services/responseFormatterService';

/**
 * Enhanced Chat Hook
 * Extends the base chat functionality with AI response formatting
 */
export const useEnhancedChat = (options = {}) => {
  const {
    formatResponses = true,
    contextualFormatting = true,
    autoDetectMedicalContext = true,
    ...chatOptions
  } = options;

  // Base chat functionality
  const baseChatHook = useChat(chatOptions);
  
  // Enhanced state
  const [formattedMessages, setFormattedMessages] = useState([]);
  const [responseMetadata, setResponseMetadata] = useState({});
  const [currentContext, setCurrentContext] = useState('general');

  // Process messages with enhanced formatting
  useEffect(() => {
    if (!formatResponses) {
      setFormattedMessages(baseChatHook.messages);
      return;
    }

    const processMessages = async () => {
      const processed = await Promise.all(
        baseChatHook.messages.map(async (message, index) => {
          // Only format AI responses
          if (message.sender === 'user' || message.isTyping) {
            return message;
          }

          try {
            // Detect medical context if enabled
            let context = currentContext;
            if (autoDetectMedicalContext) {
              context = detectMedicalContext(message.text);
              setCurrentContext(context);
            }

            // Format the response
            const formatted = contextualFormatting
              ? responseFormatterService.formatForContext(message.text, context)
              : responseFormatterService.formatResponse(message.text);

            // Store metadata
            setResponseMetadata(prev => ({
              ...prev,
              [index]: formatted.metadata
            }));

            return {
              ...message,
              text: formatted.formatted,
              originalText: message.text,
              sections: formatted.sections,
              metadata: formatted.metadata,
              context: context,
              isFormatted: true
            };
          } catch (error) {
            console.error('Error formatting message:', error);
            return message;
          }
        })
      );

      setFormattedMessages(processed);
    };

    processMessages();
  }, [baseChatHook.messages, formatResponses, contextualFormatting, autoDetectMedicalContext, currentContext]);

  // Detect medical context from message content
  const detectMedicalContext = useCallback((text) => {
    const lowerText = text.toLowerCase();
    
    // Emergency keywords
    if (/\b(emergency|urgent|serious|severe|critical|911|hospital|er)\b/.test(lowerText)) {
      return 'emergency';
    }
    
    // Symptoms keywords
    if (/\b(symptom|symptoms|feel|feeling|pain|ache|hurt|sick)\b/.test(lowerText)) {
      return 'symptoms';
    }
    
    // Treatment keywords
    if (/\b(treatment|medication|medicine|drug|therapy|cure|heal)\b/.test(lowerText)) {
      return 'treatment';
    }
    
    // Prevention keywords
    if (/\b(prevent|prevention|avoid|protect|precaution|prophylaxis)\b/.test(lowerText)) {
      return 'prevention';
    }
    
    return 'general';
  }, []);

  // Enhanced send function with context awareness
  const enhancedSend = useCallback(async (message, options = {}) => {
    const { context, ...sendOptions } = options;
    
    if (context) {
      setCurrentContext(context);
    }
    
    return baseChatHook.handleSend(message, sendOptions);
  }, [baseChatHook.handleSend]);

  // Get message statistics
  const getMessageStats = useCallback((messageIndex) => {
    return responseMetadata[messageIndex] || {};
  }, [responseMetadata]);

  // Get current conversation context
  const getConversationContext = useCallback(() => {
    const recentMessages = formattedMessages.slice(-5);
    const contexts = recentMessages
      .filter(msg => msg.context)
      .map(msg => msg.context);
    
    // Return most common context
    const contextCounts = contexts.reduce((acc, context) => {
      acc[context] = (acc[context] || 0) + 1;
      return acc;
    }, {});
    
    return Object.keys(contextCounts).reduce((a, b) => 
      contextCounts[a] > contextCounts[b] ? a : b
    ) || 'general';
  }, [formattedMessages]);

  // Export original message text
  const exportConversation = useCallback((format = 'markdown') => {
    const messages = formattedMessages.map(msg => ({
      sender: msg.sender,
      text: msg.originalText || msg.text,
      timestamp: msg.timestamp,
      context: msg.context,
      metadata: msg.metadata
    }));

    switch (format) {
      case 'json':
        return JSON.stringify(messages, null, 2);
      case 'markdown':
        return messages.map(msg => 
          `**${msg.sender === 'user' ? 'You' : 'MyDoc AI'}** (${new Date(msg.timestamp).toLocaleString()})\n\n${msg.text}\n\n---\n`
        ).join('\n');
      case 'plain':
        return messages.map(msg => 
          `${msg.sender === 'user' ? 'You' : 'MyDoc AI'}: ${msg.text}`
        ).join('\n\n');
      default:
        return messages;
    }
  }, [formattedMessages]);

  // Toggle formatting on/off
  const toggleFormatting = useCallback(() => {
    setFormattedMessages(
      formatResponses ? baseChatHook.messages : formattedMessages
    );
  }, [formatResponses, baseChatHook.messages, formattedMessages]);

  // Get conversation insights
  const getConversationInsights = useCallback(() => {
    const totalMessages = formattedMessages.length;
    const aiMessages = formattedMessages.filter(msg => msg.sender !== 'user');
    const contexts = [...new Set(formattedMessages.map(msg => msg.context).filter(Boolean))];
    
    const totalWords = aiMessages.reduce((sum, msg) => {
      const metadata = msg.metadata || {};
      return sum + (metadata.wordCount || 0);
    }, 0);

    const avgReadingTime = aiMessages.reduce((sum, msg) => {
      const metadata = msg.metadata || {};
      return sum + (metadata.readingTime || 0);
    }, 0) / Math.max(aiMessages.length, 1);

    const urgentMessages = aiMessages.filter(msg => 
      msg.metadata?.urgencyLevel === 'high'
    ).length;

    return {
      totalMessages,
      aiMessages: aiMessages.length,
      userMessages: totalMessages - aiMessages.length,
      contexts,
      totalWords,
      avgReadingTime: Math.round(avgReadingTime),
      urgentMessages,
      conversationDuration: formattedMessages.length > 0 
        ? Date.now() - new Date(formattedMessages[0].timestamp).getTime()
        : 0
    };
  }, [formattedMessages]);

  return {
    // Enhanced messages and state
    messages: formattedMessages,
    responseMetadata,
    currentContext,
    
    // Original chat functionality
    ...baseChatHook,
    
    // Enhanced functionality
    handleSend: enhancedSend,
    getMessageStats,
    getConversationContext,
    exportConversation,
    toggleFormatting,
    getConversationInsights,
    
    // Formatting controls
    formatResponses,
    contextualFormatting,
    autoDetectMedicalContext,
    
    // Utilities
    detectMedicalContext,
    responseFormatterService
  };
};

export default useEnhancedChat;