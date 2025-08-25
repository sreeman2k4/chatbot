import React from 'react';
import { Bot } from 'lucide-react';

// TypingIndicator component - shows animated typing indicator
// Displays when the bot is processing and generating a response
const TypingIndicator = () => {
  return (
    <div className="flex justify-start">
      <div className="flex items-start space-x-2 max-w-3xl">
        {/* Bot avatar */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
          <Bot className="w-5 h-5 text-gray-600" />
        </div>

        {/* Typing indicator bubble */}
        <div className="bg-gray-100 rounded-lg px-4 py-2 shadow-sm">
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;







