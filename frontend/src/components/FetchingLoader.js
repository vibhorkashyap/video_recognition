import React from 'react';
import './FetchingLoader.css';

function FetchingLoader() {
  return (
    <div className="fetching-loader-container">
      <div className="fetching-spinner"></div>
      <span className="fetching-text">Fetching response from backend...</span>
    </div>
  );
}

export default FetchingLoader;
