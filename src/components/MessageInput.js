import React, { useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';

// MessageInput component - handles user message input and sending
// Provides textarea with send button and keyboard shortcuts
const MessageInput = ({ value, onChange, onSend, onKeyPress, disabled }) => {
  const textareaRef = useRef(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [value]);

  // Handle send button click
  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSend(value);
    }
  };

  // Handle key press events
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-end space-x-2">
      {/* File attachment button (placeholder for future functionality) */}
      <button
        className="p-2 text-gray-500 hover:text-gray-700 transition-colors disabled:opacity-50"
        disabled={disabled}
        title="Attach file (coming soon)"
      >
        <Paperclip className="w-5 h-5" />
      </button>

      {/* Message input textarea */}
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
          className="w-full resize-none border border-gray-300 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:bg-gray-100"
          rows={1}
          maxRows={6}
          disabled={disabled}
          style={{ minHeight: '44px', maxHeight: '120px' }}
        />
        
        {/* Character count (optional) */}
        {value.length > 0 && (
          <span className="absolute bottom-1 right-2 text-xs text-gray-400">
            {value.length}
          </span>
        )}
      </div>

      {/* Send button */}
      <button
        onClick={handleSend}
        disabled={!value.trim() || disabled}
        className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:bg-gray-300 disabled:cursor-not-allowed"
        title="Send message"
      >
        <Send className="w-5 h-5" />
      </button>
    </div>
  );
};

export default MessageInput;






