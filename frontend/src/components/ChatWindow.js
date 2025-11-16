import React from 'react';
import Message from './Message';
import FetchingLoader from './FetchingLoader';
import ChatInput from './ChatInput';
import './ChatWindow.css';

function ChatWindow({ messages, isLoading, onSendMessage, messagesEndRef }) {
  return (
    <div className="main-content">
      <div className="chat-messages">
        {messages.map(msg => (
          <Message key={msg.id} message={msg} />
        ))}
        
        {isLoading && <FetchingLoader />}
        
        <div ref={messagesEndRef} />
      </div>
      
      <ChatInput onSendMessage={onSendMessage} disabled={isLoading} />
    </div>
  );
}

export default ChatWindow;
