import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { getUserProfile } from '../utils/api';
import './Profile.css';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [downloads, setDownloads] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('downloads');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await getUserProfile();
      setProfile(response.data.user);
      setDownloads(response.data.downloads);
      setFavorites(response.data.favorites);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="page profile-page">
        <div className="loading">Loading profile...</div>
        <Navbar />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="page profile-page">
        <div className="no-items">Unable to load profile</div>
        <Navbar />
      </div>
    );
  }

  return (
    <div className="page profile-page">
      <div className="profile-header">
        <div className="profile-avatar">👤</div>
        <h1 className="profile-name">
          {profile.first_name} {profile.last_name}
        </h1>
        {profile.username && (
          <p className="profile-username">@{profile.username}</p>
        )}
      </div>

      <div className="profile-stats">
        <div className="stat-box">
          <div className="stat-value">{profile.total_downloads || 0}</div>
          <div className="stat-label">Downloads</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{favorites.length}</div>
          <div className="stat-label">Favorites</div>
        </div>
      </div>

      <div className="profile-tabs">
        <button
          className={`tab-btn ${activeTab === 'downloads' ? 'active' : ''}`}
          onClick={() => setActiveTab('downloads')}
        >
          📥 Downloads
        </button>
        <button
          className={`tab-btn ${activeTab === 'favorites' ? 'active' : ''}`}
          onClick={() => setActiveTab('favorites')}
        >
          ❤️ Favorites
        </button>
      </div>

      <div className="profile-content">
        {activeTab === 'downloads' && (
          <div className="downloads-list">
            {downloads.length > 0 ? (
              downloads.map((download, index) => (
                <div key={index} className="download-item">
                  <div className="download-info">
                    <h4 className="download-name">{download.software_name}</h4>
                    <p className="download-date">
                      {new Date(download.timestamp).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="download-badge">
                    {download.links_sent?.length || 0} links
                  </div>
                </div>
              ))
            ) : (
              <div className="no-items">No downloads yet</div>
            )}
          </div>
        )}

        {activeTab === 'favorites' && (
          <div className="favorites-list">
            {favorites.length > 0 ? (
              favorites.map((favorite) => (
                <div key={favorite._id} className="favorite-item">
                  <div className="favorite-info">
                    <h4 className="favorite-name">{favorite.name}</h4>
                    <p className="favorite-category">📂 {favorite.category}</p>
                  </div>
                  <div className="favorite-stats">
                    ⭐ {favorite.average_rating || 0}/5
                  </div>
                </div>
              ))
            ) : (
              <div className="no-items">No favorites yet</div>
            )}
          </div>
        )}
      </div>

      <Navbar />
    </div>
  );
};

export default Profile;
