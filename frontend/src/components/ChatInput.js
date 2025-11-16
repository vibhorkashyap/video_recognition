import React, { useState } from 'react';
import './ChatInput.css';

function ChatInput({ onSendMessage, disabled }) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-area">
      <div className="input-wrapper">
        <div className="input-group">
          <textarea
            id="chatInput"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything... (e.g., 'activities with bikes?', 'people walking', 'vehicles')"
            disabled={disabled}
          />
          <button
            id="sendBtn"
            className="send-btn"
            onClick={handleSend}
            disabled={disabled || !input.trim()}
          >
            ⬆
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatInput;
