import React, { useState, useEffect, useRef } from 'react';
import ChatWindow from './components/ChatWindow';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: '🤖 Hello! I\'m your AI-powered camera analysis assistant. I use Ollama Gemma 3:4b to analyze video frames and understand what\'s happening in your camera feeds. Ask me about any activities or events you\'d like to find!',
      type: 'text'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState({
    camera_id: null,
    start_time: '',
    end_time: '',
    searchResults: []
  });
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Initialize time filters with IST timezone
    initializeTimeFilters();
  }, []);

  const initializeTimeFilters = () => {
    const istFormatter = new Intl.DateTimeFormat('en-IN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      timeZone: 'Asia/Kolkata'
    });

    const endTime = new Date();
    const startTime = new Date(endTime.getTime() - 1 * 60 * 60 * 1000);

    const formatDateTimeIST = (date) => {
      const parts = istFormatter.formatToParts(date);
      const year = parts.find(p => p.type === 'year').value;
      const month = parts.find(p => p.type === 'month').value;
      const day = parts.find(p => p.type === 'day').value;
      const hour = parts.find(p => p.type === 'hour').value;
      const minute = parts.find(p => p.type === 'minute').value;
      return `${year}-${month}-${day}T${hour}:${minute}`;
    };

    setFilters(prev => ({
      ...prev,
      start_time: formatDateTimeIST(startTime),
      end_time: formatDateTimeIST(endTime)
    }));
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (query) => {
    // Add user message
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: query,
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          camera_id: filters.camera_id,
          start_time: filters.start_time,
          end_time: filters.end_time
        })
      });

      const data = await response.json();

      if (data.error) {
        setMessages(prev => [...prev, {
          id: Date.now(),
          role: 'assistant',
          content: `❌ Error: ${data.error}`,
          type: 'text'
        }]);
      } else {
        setMessages(prev => [...prev, {
          id: Date.now(),
          role: 'assistant',
          content: data.ollama_summaries || [],
          type: 'summaries'
        }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'assistant',
        content: '❌ Failed to process query. Please try again.',
        type: 'text'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  return (
    <div className="app-container">
      <Sidebar 
        filters={filters} 
        onFilterChange={handleFilterChange}
      />
      <ChatWindow 
        messages={messages}
        isLoading={isLoading}
        onSendMessage={handleSendMessage}
        messagesEndRef={messagesEndRef}
      />
    </div>
  );
}

export default App;
