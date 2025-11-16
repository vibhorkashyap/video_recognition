import React, { useState, useEffect } from 'react';
import './Sidebar.css';
import ResultModal from './ResultModal';

function Sidebar({ filters, onFilterChange }) {
  const [localFilters, setLocalFilters] = useState(filters);
  const [recentSummaries, setRecentSummaries] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (key, value) => {
    const updated = { ...localFilters, [key]: value };
    setLocalFilters(updated);
    onFilterChange(updated);
  };

  const handleSearch = async () => {
    setIsSearching(true);
    setHasSearched(true);
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: '',
          camera_id: localFilters.camera_id ? parseInt(localFilters.camera_id) : null,
          start_time: localFilters.start_time,
          end_time: localFilters.end_time,
          search_type: 'summaries'
        })
      });

      const data = await response.json();
      setRecentSummaries(data.ollama_summaries || []);
    } catch (error) {
      console.error('Error loading summaries:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleResultClick = (summary) => {
    setSelectedResult(summary);
  };

  const handleCloseModal = () => {
    setSelectedResult(null);
  };

  return (
    <div className="sidebar">
      <button className="new-chat-btn">+ New Chat</button>

      <div className="sidebar-section">
        <div className="sidebar-title">🔍 FILTERS</div>

        <div className="filter-group">
          <label className="filter-label">CAMERA</label>
          <select
            className="filter-select"
            value={localFilters.camera_id || ''}
            onChange={(e) => handleFilterChange('camera_id', e.target.value || null)}
          >
            <option value="">All Cameras</option>
            <option value="1">Camera 1</option>
            <option value="2">Camera 2</option>
            <option value="3">Camera 3</option>
            <option value="4">Camera 4</option>
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">FROM</label>
          <input
            type="datetime-local"
            className="filter-input"
            value={localFilters.start_time}
            onChange={(e) => handleFilterChange('start_time', e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label className="filter-label">TO</label>
          <input
            type="datetime-local"
            className="filter-input"
            value={localFilters.end_time}
            onChange={(e) => handleFilterChange('end_time', e.target.value)}
          />
        </div>

        <button className="search-btn" onClick={handleSearch} disabled={isSearching}>
          {isSearching ? (
            <span className="search-btn-loader">
              <span className="search-spinner"></span>
              Searching...
            </span>
          ) : (
            <>● Search</>
          )}
        </button>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-title">SEARCH RESULTS</div>
        <div id="eventsList" className="events-list">
          {recentSummaries.slice(0, 8).map((summary, idx) => (
            <div key={idx} className="event-item" onClick={() => handleResultClick(summary)}>
              <div className="event-time">
                {new Date(summary.timestamp).toLocaleTimeString()} • {summary.interval?.replace(/_/g, ' ')}
              </div>
              <div className="event-desc">
                {summary.summary.substring(0, 40)}...
              </div>
            </div>
          ))}
          {recentSummaries.length === 0 && hasSearched && (
            <div style={{ color: '#666', fontSize: '11px', padding: '8px' }}>
              No results found
            </div>
          )}
          {recentSummaries.length === 0 && !hasSearched && (
            <div style={{ color: '#666', fontSize: '11px', padding: '8px' }}>
              No events found
            </div>
          )}
        </div>
      </div>

      {selectedResult && (
        <ResultModal result={selectedResult} onClose={handleCloseModal} />
      )}
    </div>
  );
}

export default Sidebar;
