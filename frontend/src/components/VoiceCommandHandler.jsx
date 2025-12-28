import { useEffect, useCallback } from 'react';

/**
 * Voice Command Handler Component
 * Handles voice commands for navigation and actions throughout the app
 */
const VoiceCommandHandler = ({ 
  onClearChat, 
  onNewConversation, 
  onRepeatMessage, 
  onToggleVoice,
  onShowHelp,
  onNavigate,
  lastMessage 
}) => {

  // Handle voice commands
  const handleVoiceCommand = useCallback((event) => {
    const { type, payload } = event.detail;

    switch (type) {
      case 'navigate':
        handleNavigation(payload);
        break;
      case 'action':
        handleAction(payload);
        break;
      default:
        console.warn('Unknown voice command type:', type);
    }
  }, []);

  // Handle navigation commands
  const handleNavigation = useCallback((route) => {
    const routes = {
      '/medical-history': () => {
        onNavigate?.('medical-history');
      },
      '/symptom-checker': () => {
        onNavigate?.('symptom-checker');
      },
      '/health-analytics': () => {
        onNavigate?.('health-analytics');
      },
      '/drug-interactions': () => {
        onNavigate?.('drug-interactions');
      },
      '/profile': () => {
        onNavigate?.('profile');
      },
      '/settings': () => {
        onNavigate?.('settings');
      }
    };

    const routeHandler = routes[route];
    if (routeHandler) {
      routeHandler();
    }
  }, [onNavigate]);

  // Handle action commands
  const handleAction = useCallback((action) => {
    const actions = {
      'clear-chat': () => {
        if (onClearChat) {
          onClearChat();
        }
      },
      'new-conversation': () => {
        if (onNewConversation) {
          onNewConversation();
        }
      },
      'repeat-message': () => {
        if (onRepeatMessage && lastMessage) {
          onRepeatMessage(lastMessage);
        }
      },
      'stop-speech': () => {
        // Stop any current speech synthesis
        if (window.speechSynthesis) {
          window.speechSynthesis.cancel();
        }
      },
      'enable-voice': () => {
        if (onToggleVoice) {
          onToggleVoice(true);
        }
      },
      'disable-voice': () => {
        if (onToggleVoice) {
          onToggleVoice(false);
        }
      },
      'show-help': () => {
        if (onShowHelp) {
          onShowHelp();
        } else {
          showVoiceCommandHelp();
        }
      },
      'emergency-help': () => {
        handleEmergencyCommand();
      },
      'call-emergency': () => {
        handleEmergencyCall();
      }
    };

    const actionHandler = actions[action];
    if (actionHandler) {
      actionHandler();
    }
  }, [onClearChat, onNewConversation, onRepeatMessage, onToggleVoice, onShowHelp, lastMessage]);

  // Show voice command help
  const showVoiceCommandHelp = useCallback(() => {
    const helpMessage = `
Voice Commands Available:

Navigation:
• "Go to medical history" - View your medical records
• "Open symptom checker" - Check your symptoms
• "Show health analytics" - View health insights
• "Check drug interactions" - Check medication interactions

Actions:
• "Clear chat" - Clear current conversation
• "Start new conversation" - Begin new chat
• "Repeat last message" - Repeat AI response
• "Stop speaking" - Stop voice output
• "Enable/Disable voice" - Toggle voice responses
• "Help" - Show this help message

Emergency:
• "Emergency help" - Get emergency guidance
• "Call emergency" - Emergency contact information

Say any command clearly and wait for confirmation.
    `;

    // Voice command help removed - no more announcements
  }, []);

  // Handle emergency commands
  const handleEmergencyCommand = useCallback(() => {
    const emergencyMessage = `
🚨 EMERGENCY GUIDANCE 🚨

If this is a medical emergency:
• Call 911 (US) or your local emergency number
• Go to the nearest emergency room
• Call poison control: 1-800-222-1222

For urgent but non-emergency care:
• Contact your doctor
• Visit urgent care center
• Call nurse hotline

This AI cannot replace emergency medical services.
    `;

    // Emergency message removed - no more announcements

    // Also speak the emergency message
    if (window.speechSynthesis) {
      const utterance = new SpeechSynthesisUtterance(
        'Emergency detected. If this is a medical emergency, call 911 immediately or go to the nearest emergency room. This AI cannot replace emergency medical services.'
      );
      utterance.rate = 1.1;
      utterance.pitch = 1.1;
      window.speechSynthesis.speak(utterance);
    }
  }, []);

  // Handle emergency call command
  const handleEmergencyCall = useCallback(() => {
    // Emergency call message removed - no more announcements
    console.log('Emergency call command triggered');
  }, []);

  // Set up voice command listener
  useEffect(() => {
    window.addEventListener('voice-command', handleVoiceCommand);

    return () => {
      window.removeEventListener('voice-command', handleVoiceCommand);
    };
  }, [handleVoiceCommand]);

  // This component doesn't render anything visible
  return null;
};

export default VoiceCommandHandler;