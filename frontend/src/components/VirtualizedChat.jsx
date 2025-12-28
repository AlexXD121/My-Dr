import { memo, useMemo } from 'react';
import { motion } from 'framer-motion';

// Memoized message component for better performance
const MemoizedMessage = memo(({ message, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="message-item"
    >
      {/* Message content */}
    </motion.div>
  );
});

MemoizedMessage.displayName = 'MemoizedMessage';

// Virtual scrolling for large chat histories
export const VirtualizedChat = ({ messages, renderMessage }) => {
  const visibleMessages = useMemo(() => {
    // Only render last 50 messages for performance
    return messages.slice(-50);
  }, [messages]);

  return (
    <div className="chat-container">
      {visibleMessages.map((message, index) => (
        <MemoizedMessage
          key={`${message.timestamp}-${index}`}
          message={message}
          index={index}
        />
      ))}
    </div>
  );
};

export default VirtualizedChat;