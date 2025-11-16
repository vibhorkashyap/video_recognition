import React from 'react';
import './ResultModal.css';

function ResultModal({ result, onClose }) {
  if (!result) return null;

  const time = new Date(result.timestamp).toLocaleString();
  const interval = result.interval?.replace(/_/g, ' ').toUpperCase() || 'Unknown';
  const camera = `Camera ${result.camera_id}`;
  const videoClips = result.video_clips || [];
  const frameSnapshots = result.frame_snapshots || [];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📊 Event Details</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="result-meta">
            <div className="result-meta-item">
              <span className="meta-icon">🎥</span>
              <span className="meta-label">Camera</span>
              <span className="meta-value">{camera}</span>
            </div>
            <div className="result-meta-item">
              <span className="meta-icon">⏱️</span>
              <span className="meta-label">Interval</span>
              <span className="meta-value">{interval}</span>
            </div>
            <div className="result-meta-item">
              <span className="meta-icon">🕐</span>
              <span className="meta-label">Time</span>
              <span className="meta-value">{time}</span>
            </div>
          </div>

          <div className="result-summary">
            <h3>Summary</h3>
            <p>{result.summary}</p>
          </div>

          {frameSnapshots.length > 0 && (
            <div className="frame-snapshots-section">
              <h3>🖼️ Frame Snapshots ({result.frames_analyzed} total frames, {result.frames_sampled} sampled)</h3>
              <div className="frame-snapshots-container">
                {frameSnapshots.map((frame, idx) => (
                  <div key={idx} className="frame-snapshot-item">
                    <img
                      src={frame.path}
                      alt={`Frame ${idx}`}
                      className="frame-snapshot-image"
                    />
                    <div className="frame-snapshot-info">
                      <div className="frame-number">Frame {frame.frame_number}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {videoClips.length > 0 && (
            <div className="video-clips-section">
              <h3>📹 Related Video Clips</h3>
              <div className="video-clips-container">
                {videoClips.map((clip, idx) => (
                  <div key={idx} className="video-clip-item">
                    <video
                      width="100%"
                      height="200"
                      controls
                      className="video-player"
                    >
                      <source src={clip.path} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                    <div className="video-clip-info">
                      <div className="video-clip-name">{clip.filename}</div>
                      <div className="video-clip-time">
                        {new Date(clip.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="result-info">
            <span>📌 Frames analyzed: {result.frames_analyzed}</span>
            {result.frames_sampled && <span> • Sampled: {result.frames_sampled}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResultModal;
