import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';
import { chatService } from '../services/chatService';

// Main ChatInterface component - handles the core chat functionality
// Manages message display, input handling, and API communication
const ChatInterface = ({ chatHistory, addMessage, isLoading, setIsLoading, settings }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  // Handle sending a new message
  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Add user message to chat history
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    addMessage(userMessage);

    // Clear input and show typing indicator
    setInputMessage('');
    setIsTyping(true);
    setIsLoading(true);
    
    // Add a processing message to show progress
    const processingMessage = {
      id: Date.now() + 0.5,
      type: 'processing',
      content: 'Processing your request...',
      timestamp: new Date().toISOString()
    };
    addMessage(processingMessage);

    try {
      // Send message to RAG service
      const response = await chatService.sendMessage(message, chatHistory, settings);
      
      // Remove processing message and add bot response
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.content,
        sources: response.sources || [],
        timestamp: new Date().toISOString()
      };
      addMessage(botMessage);
    } catch (error) {
      // Handle error and add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      addMessage(errorMessage);
      console.error('Chat error:', error);
    } finally {
      setIsTyping(false);
      setIsLoading(false);
    }
  };



  return (
    <div className="flex flex-col h-full bg-white">
      {/* Chat messages area */}
      <div className="flex-1 overflow-y-auto chat-container">
        <MessageList messages={chatHistory} />
        
        {/* Typing indicator */}
        {isTyping && <TypingIndicator />}
        
        {/* Auto-scroll anchor */}
        <div ref={messagesEndRef} />
      </div>

      {/* Message input area */}
      <div className="border-t border-gray-200 bg-white p-4">
        <MessageInput
          value={inputMessage}
          onChange={setInputMessage}
          onSend={handleSendMessage}
          disabled={isLoading}
        />
      </div>
    </div>
  );
};

export default ChatInterface;






