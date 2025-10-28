import { useState, useEffect } from 'react';
import WebApp from '@twa-dev/sdk';
import Navbar from '../components/Navbar';
import { getGameScripts } from '../utils/api';
import './GameScripts.css';

const GameScripts = () => {
  const [scripts, setScripts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScripts();
  }, []);

  const loadScripts = async () => {
    try {
      const response = await getGameScripts();
      setScripts(response.data.scripts);
    } catch (error) {
      console.error('Error loading scripts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = (script) => {
    WebApp.openLink(script.link);
    WebApp.showAlert(`📜 Opening ${script.name}!\n\n${script.description}`);
  };

  return (
    <div className="page scripts-page">
      <div className="page-header">
        <h1>📜 Game Scripts</h1>
        <p className="page-subtitle">Browse and download game scripts</p>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="scripts-list">
          {scripts.length > 0 ? (
            scripts.map((script) => (
              <div key={script._id} className="script-card">
                <div className="script-icon">📜</div>
                <div className="script-content">
                  <h3 className="script-name">{script.name}</h3>
                  <p className="script-description">{script.description}</p>
                  <div className="script-stats">
                    <span className="script-stat">👁️ {script.views || 0} views</span>
                  </div>
                </div>
                <button
                  className="script-download-btn"
                  onClick={() => handleDownload(script)}
                >
                  ⬇️
                </button>
              </div>
            ))
          ) : (
            <div className="no-items">No game scripts available</div>
          )}
        </div>
      )}

      <Navbar />
    </div>
  );
};

export default GameScripts;
