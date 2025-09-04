import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { User, Bot, AlertCircle, ExternalLink } from 'lucide-react';

// Message component - renders individual chat messages with proper styling
// Supports markdown, code highlighting, and different message types
const Message = ({ message }) => {
  const { type, content, timestamp, sources } = message;

  // Get appropriate icon and styling based on message type
  const getMessageConfig = () => {
    switch (type) {
      case 'user':
        return {
          icon: <User className="w-5 h-5 text-white" />,
          bgColor: 'bg-blue-500',
          textColor: 'text-white',
          alignment: 'justify-end',
          bubbleColor: 'bg-blue-500 text-white'
        };
      case 'bot':
        return {
          icon: <Bot className="w-5 h-5 text-gray-600" />,
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
          alignment: 'justify-start',
          bubbleColor: 'bg-gray-100 text-gray-800'
        };
      case 'error':
        return {
          icon: <AlertCircle className="w-5 h-5 text-red-500" />,
          bgColor: 'bg-red-100',
          textColor: 'text-red-800',
          alignment: 'justify-start',
          bubbleColor: 'bg-red-100 text-red-800'
        };
      default:
        return {
          icon: <Bot className="w-5 h-5 text-gray-600" />,
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
          alignment: 'justify-start',
          bubbleColor: 'bg-gray-100 text-gray-800'
        };
    }
  };

  const config = getMessageConfig();

  // Format timestamp for display
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className={`flex ${config.alignment}`}>
      <div className={`flex items-start space-x-2 max-w-3xl ${type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar/Icon */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full ${config.bgColor} flex items-center justify-center`}>
          {config.icon}
        </div>

        {/* Message content */}
        <div className={`flex flex-col space-y-1 ${type === 'user' ? 'items-end' : 'items-start'}`}>
          {/* Message bubble */}
          <div className={`rounded-lg px-4 py-2 max-w-2xl ${config.bubbleColor} shadow-sm`}>
            <ReactMarkdown
              className="prose prose-sm max-w-none"
              components={{
                // Custom code block rendering with syntax highlighting
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={tomorrow}
                      language={match[1]}
                      PreTag="div"
                      className="rounded-md"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className="bg-gray-200 px-1 py-0.5 rounded text-sm" {...props}>
                      {children}
                    </code>
                  );
                },
                // Custom link rendering
                a({ href, children }) {
                  return (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline inline-flex items-center"
                    >
                      {children}
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  );
                }
              }}
            >
              {content}
            </ReactMarkdown>
          </div>

          {/* Sources section for bot messages */}
          {type === 'bot' && sources && sources.length > 0 && (
            <div className="bg-blue-50 rounded-lg p-3 max-w-2xl">
              <h4 className="text-sm font-medium text-blue-800 mb-2">Sources:</h4>
              <div className="space-y-1">
                {sources.map((source, index) => (
                  <div key={index} className="text-xs text-blue-600">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="hover:text-blue-800 underline inline-flex items-center"
                    >
                      {source.title || source.url}
                      <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timestamp */}
          <span className="text-xs text-gray-500">
            {formatTime(timestamp)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default Message;








