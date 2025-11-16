import React from 'react';
import './Message.css';

function Message({ message }) {
  if (message.type === 'summaries') {
    return (
      <div className="message assistant">
        <div className="message-bubble">
          <div className="summaries-container">
            <div className="summaries-header">📊 Found {message.content.length} Video Summaries</div>
            {message.content.map((summary, idx) => (
              <div key={idx} className="summary-card">
                <div className="summary-meta">
                  <span className="summary-meta-item">🎥 Camera {summary.camera_id}</span>
                  <span className="summary-meta-item">⏱️ {summary.interval?.replace(/_/g, ' ') || 'Unknown'}</span>
                  <span className="summary-meta-item">🕐 {new Date(summary.timestamp).toLocaleString()}</span>
                </div>
                <div className="summary-text">{summary.summary}</div>
                
                {summary.frame_snapshots && summary.frame_snapshots.length > 0 && (
                  <div className="chat-frame-snapshots">
                    <div className="chat-frames-label">🖼️ Frames ({summary.frames_analyzed} total):</div>
                    <div className="chat-frames-grid">
                      {summary.frame_snapshots.map((frame, frameIdx) => (
                        <div key={frameIdx} className="chat-frame-snapshot">
                          <img
                            src={frame.path}
                            alt={`Frame ${frame.frame_number}`}
                            className="chat-frame-image"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {summary.video_clips && summary.video_clips.length > 0 && (
                  <div className="chat-video-clips">
                    <div className="chat-video-clips-label">📹 Video Clips:</div>
                    <div className="chat-video-clips-grid">
                      {summary.video_clips.map((clip, clipIdx) => (
                        <div key={clipIdx} className="chat-video-clip">
                          <video
                            width="100%"
                            height="120"
                            controls
                            className="chat-video-player"
                          >
                            <source src={clip.path} type="video/mp4" />
                            Your browser does not support the video tag.
                          </video>
                          <div className="chat-video-name">{clip.filename}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="summary-info">📌 Frames analyzed: {summary.frames_analyzed}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`message ${message.role}`}>
      <div className="message-bubble">
        {message.content}
      </div>
    </div>
  );
}

export default Message;
