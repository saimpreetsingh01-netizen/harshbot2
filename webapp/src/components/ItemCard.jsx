import { useState } from 'react';
import WebApp from '@twa-dev/sdk';
import { createDownload } from '../utils/api';
import './ItemCard.css';

const ItemCard = ({ item, type = 'software' }) => {
  const [loading, setLoading] = useState(false);

  const handleDownload = async () => {
    setLoading(true);
    try {
      const response = await createDownload(item._id);
      const links = response.data.links;

      let message = `📦 ${item.name || item.title}\n\n⬇️ Download Links:\n\n`;
      links.forEach((link, i) => {
        const emoji = link.service === 'adrinolinks' ? '💵' : '💰';
        message += `${emoji} Link ${i + 1}: ${link.url}\n`;
      });

      WebApp.showAlert(message);
    } catch (error) {
      WebApp.showAlert('Error getting download links. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderContent = () => {
    if (type === 'movie') {
      return (
        <>
          <h3 className="item-title">{item.title}</h3>
          <div className="item-meta">
            <span className="item-category">📂 {item.category}</span>
          </div>
        </>
      );
    }

    return (
      <>
        <h3 className="item-title">{item.name}</h3>
        <div className="item-meta">
          <span className="item-category">📂 {item.category}</span>
          {item.os && (
            <span className="item-os">💻 {Array.isArray(item.os) ? item.os.join(', ') : item.os}</span>
          )}
        </div>
        <div className="item-stats">
          <span className="stat">⭐ {item.average_rating || 0}/5</span>
          <span className="stat">📥 {item.downloads_count || 0}</span>
          {item.file_size && <span className="stat">📏 {item.file_size}</span>}
        </div>
        {item.description && (
          <p className="item-description">{item.description}</p>
        )}
      </>
    );
  };

  return (
    <div className="item-card">
      {renderContent()}
      <button
        className="download-btn"
        onClick={handleDownload}
        disabled={loading}
      >
        {loading ? 'Loading...' : '⬇️ Download'}
      </button>
    </div>
  );
};

export default ItemCard;
