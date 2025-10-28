import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import './Home.css';

const Home = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: '🎮',
      title: 'Games',
      description: 'Browse and download games',
      path: '/games',
      color: '#e74c3c'
    },
    {
      icon: '💻',
      title: 'Software',
      description: 'Professional tools & apps',
      path: '/software',
      color: '#f39c12'
    },
    {
      icon: '🎬',
      title: 'Movies',
      description: 'Discover movies across categories',
      path: '/movies',
      color: '#9b59b6'
    },
    {
      icon: '🎨',
      title: 'NFTs',
      description: 'Claim free NFTs',
      path: '/nfts',
      color: '#3498db'
    },
    {
      icon: '📜',
      title: 'Game Scripts',
      description: 'Browse game scripts',
      path: '/scripts',
      color: '#2ecc71'
    }
  ];

  return (
    <div className="page home-page">
      <div className="home-header">
        <h1 className="home-title">🌟 Digital Hub</h1>
        <p className="home-subtitle">Your ultimate entertainment & software platform</p>
      </div>

      <div className="features-grid">
        {features.map((feature, index) => (
          <div
            key={index}
            className="feature-card"
            onClick={() => navigate(feature.path)}
            style={{ borderLeft: `4px solid ${feature.color}` }}
          >
            <div className="feature-icon">{feature.icon}</div>
            <div className="feature-content">
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="info-section">
        <h2>📱 Access Anywhere</h2>
        <p>Use this mini app directly in Telegram or continue using bot commands - both work perfectly!</p>
      </div>

      <Navbar />
    </div>
  );
};

export default Home;
