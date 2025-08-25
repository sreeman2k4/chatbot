import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import FaceRecognition from './components/FaceRecognition';
import TextExtraction from './components/TextExtraction';
import './App.css';

// Main App component - serves as the root component
// Manages global state and renders the main layout
function App() {
  // State for managing chat history and application settings
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showFaceRecognition, setShowFaceRecognition] = useState(false);
  const [showTextExtraction, setShowTextExtraction] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [settings, setSettings] = useState({
    model: 'mistral:7b',
    temperature: 0.7,
    maxTokens: 1000,
    enableRAG: true
  });

  // Load chat history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('chatHistory');
    if (savedHistory) {
      setChatHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
  }, [chatHistory]);

  // Function to add a new message to chat history
  const addMessage = (message) => {
    setChatHistory(prev => [...prev, message]);
  };

  // Function to clear chat history
  const clearChat = () => {
    setChatHistory([]);
    localStorage.removeItem('chatHistory');
  };

  // Function to update application settings
  const updateSettings = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  // Face recognition handlers
  const handleFaceLogin = (username) => {
    setCurrentUser(username);
    setShowFaceRecognition(false);
    addMessage({
      type: 'assistant',
      content: `Welcome back, ${username}! You are now logged in with face recognition.`,
      timestamp: new Date().toISOString()
    });
  };

  const handleFaceRegister = (username) => {
    setCurrentUser(username);
    setShowFaceRecognition(false);
    addMessage({
      type: 'assistant',
      content: `Welcome, ${username}! Your face has been registered successfully. You are now logged in.`,
      timestamp: new Date().toISOString()
    });
  };

  const handleLogout = () => {
    setCurrentUser(null);
    addMessage({
      type: 'assistant',
      content: 'You have been logged out. Please use face recognition to login again.',
      timestamp: new Date().toISOString()
    });
  };

  return (
    <div className="App min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header component with navigation and branding */}
      <Header 
        sidebarOpen={sidebarOpen} 
        setSidebarOpen={setSidebarOpen}
        clearChat={clearChat}
        currentUser={currentUser}
        onLogout={handleLogout}
        onShowFaceRecognition={() => setShowFaceRecognition(true)}
        onShowTextExtraction={() => setShowTextExtraction(true)}
      />
      
      <div className="flex h-screen pt-16">
        {/* Sidebar component for settings and chat history */}
        <Sidebar 
          isOpen={sidebarOpen}
          chatHistory={chatHistory}
          settings={settings}
          updateSettings={updateSettings}
          clearChat={clearChat}
          setSidebarOpen={setSidebarOpen}
        />
        
        {/* Main chat interface component */}
        <div className="flex-1 flex flex-col">
          {showFaceRecognition ? (
            <div className="flex-1 flex items-center justify-center p-4">
              <FaceRecognition
                onLogin={handleFaceLogin}
                onRegister={handleFaceRegister}
              />
            </div>
          ) : showTextExtraction ? (
            <div className="flex-1 flex items-center justify-center p-4">
              <TextExtraction onBack={() => setShowTextExtraction(false)} />
            </div>
          ) : (
            <ChatInterface 
              chatHistory={chatHistory}
              addMessage={addMessage}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
              settings={settings}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
