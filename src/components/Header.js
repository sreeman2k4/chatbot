import React from 'react';
import { Menu, Trash2, Settings } from 'lucide-react';

// Header component - displays app branding and navigation controls
// Contains menu button, app title, and action buttons
const Header = ({ sidebarOpen, setSidebarOpen, clearChat, currentUser, onLogout, onShowFaceRecognition, onShowTextExtraction }) => {
  return (
    <header className="fixed top-0 left-0 right-0 bg-white shadow-lg z-50 border-b border-gray-200">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left side - Menu button and app title */}
        <div className="flex items-center space-x-4">
          {/* Hamburger menu button for mobile sidebar */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Toggle sidebar"
          >
            <Menu className="w-6 h-6 text-gray-600" />
          </button>
          
          {/* App title and branding */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AI</span>
            </div>
            <h1 className="text-xl font-bold text-gray-800">RAG Chatbot</h1>
          </div>
        </div>

        {/* Right side - Action buttons */}
        <div className="flex items-center space-x-2">
          {/* Face Recognition buttons */}
          {currentUser ? (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Welcome, {currentUser}</span>
              <button
                onClick={onLogout}
                className="px-3 py-1 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
                title="Logout"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={onShowFaceRecognition}
              className="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
              title="Face Recognition Login/Register"
            >
              Face Login
            </button>
          )}
          
          {/* Text Extraction button */}
          <button
            onClick={onShowTextExtraction}
            className="px-3 py-1 text-sm bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors"
            title="Extract text from images"
          >
            📄 Extract Text
          </button>
          
          {/* Settings button */}
          <button
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            aria-label="Settings"
            title="Settings"
          >
            <Settings className="w-5 h-5 text-gray-600" />
          </button>
          
          {/* Clear chat button */}
          <button
            onClick={clearChat}
            className="p-2 rounded-lg hover:bg-red-100 transition-colors"
            aria-label="Clear chat"
            title="Clear chat history"
          >
            <Trash2 className="w-5 h-5 text-red-500" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;






