import React, { useState } from 'react';
import { X, MessageSquare, Settings, Database, Zap } from 'lucide-react';

// Sidebar component - displays chat history and settings
// Contains navigation, chat history, and configuration options
const Sidebar = ({ isOpen, chatHistory, settings, updateSettings, clearChat, setSidebarOpen }) => {
  const [activeTab, setActiveTab] = useState('history');

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar container */}
      <div className={`
        fixed top-16 left-0 h-full w-80 bg-white shadow-xl z-50
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:shadow-none
      `}>
        <div className="flex flex-col h-full">
          {/* Header with close button for mobile */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 lg:hidden">
            <h2 className="text-lg font-semibold text-gray-800">Menu</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Tab navigation */}
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('history')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === 'history'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <MessageSquare className="w-4 h-4 inline mr-2" />
              History
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === 'settings'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <Settings className="w-4 h-4 inline mr-2" />
              Settings
            </button>
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'history' && (
              <ChatHistory chatHistory={chatHistory} />
            )}
            {activeTab === 'settings' && (
              <SettingsPanel settings={settings} updateSettings={updateSettings} />
            )}
          </div>

          {/* Footer actions */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={clearChat}
              className="w-full py-2 px-4 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Clear Chat History
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

// ChatHistory component - displays previous conversations
const ChatHistory = ({ chatHistory }) => {
  // Group messages by conversation (simple implementation)
  const conversations = chatHistory.reduce((acc, message, index) => {
    if (index % 2 === 0) {
      acc.push({
        id: index,
        userMessage: message,
        botMessage: chatHistory[index + 1] || null
      });
    }
    return acc;
  }, []);

  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Chat History</h3>
      {conversations.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No chat history yet</p>
      ) : (
        <div className="space-y-3">
          {conversations.map((conversation) => (
            <div key={conversation.id} className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 truncate">
                {conversation.userMessage?.content || 'User message'}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// SettingsPanel component - displays and manages application settings
const SettingsPanel = ({ settings, updateSettings }) => {
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Settings</h3>
      
      <div className="space-y-4">
        {/* Model selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            AI Model
          </label>
          <select
            value={settings.model}
            onChange={(e) => updateSettings({ model: e.target.value })}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
                    <option value="mistral:7b">Mistral-7B (Ollama) - Default</option>
        <option value="llama2:7b">Llama2-7B (Ollama)</option>
        <option value="phi:2.7b">Phi-2.7B (Ollama)</option>
          </select>
        </div>

        {/* Temperature setting */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Temperature: {settings.temperature}
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={settings.temperature}
            onChange={(e) => updateSettings({ temperature: parseFloat(e.target.value) })}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Conservative</span>
            <span>Creative</span>
          </div>
        </div>

        {/* Max tokens setting */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Max Tokens: {settings.maxTokens}
          </label>
          <input
            type="range"
            min="100"
            max="2000"
            step="100"
            value={settings.maxTokens}
            onChange={(e) => updateSettings({ maxTokens: parseInt(e.target.value) })}
            className="w-full"
          />
        </div>

        {/* RAG toggle */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-medium text-gray-700">Enable RAG</span>
          </div>
          <button
            onClick={() => updateSettings({ enableRAG: !settings.enableRAG })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              settings.enableRAG ? 'bg-blue-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                settings.enableRAG ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
