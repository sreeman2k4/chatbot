import React from 'react';
import Message from './Message';

// MessageList component - displays all chat messages in a scrollable container
// Handles message rendering and layout for the chat interface
const MessageList = ({ messages }) => {
  // Welcome message to show when no messages exist
  const welcomeMessage = {
    id: 'welcome',
    type: 'bot',
    content: `Hello! I'm your AI assistant powered by RAG (Retrieval-Augmented Generation). I can help you with various tasks and provide information from my knowledge base. 

**What I can do:**
- Answer questions with accurate information
- Provide detailed explanations
- Help with research and analysis
- Assist with coding and technical topics

**How to use:**
- Simply type your question or request
- I'll search through my knowledge base to find relevant information
- You can adjust settings in the sidebar to customize my responses

Feel free to ask me anything!`,
    timestamp: new Date().toISOString()
  };

  // Show welcome message if no messages exist
  const displayMessages = messages.length === 0 ? [welcomeMessage] : messages;

  return (
    <div className="flex flex-col space-y-4 p-4">
      {displayMessages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
    </div>
  );
};

export default MessageList;








