import { useNavigate, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <button
        className={`nav-btn ${isActive('/') ? 'active' : ''}`}
        onClick={() => navigate('/')}
      >
        <span className="nav-icon">🏠</span>
        <span className="nav-label">Home</span>
      </button>
      <button
        className={`nav-btn ${isActive('/games') ? 'active' : ''}`}
        onClick={() => navigate('/games')}
      >
        <span className="nav-icon">🎮</span>
        <span className="nav-label">Games</span>
      </button>
      <button
        className={`nav-btn ${isActive('/movies') ? 'active' : ''}`}
        onClick={() => navigate('/movies')}
      >
        <span className="nav-icon">🎬</span>
        <span className="nav-label">Movies</span>
      </button>
      <button
        className={`nav-btn ${isActive('/nfts') ? 'active' : ''}`}
        onClick={() => navigate('/nfts')}
      >
        <span className="nav-icon">🎨</span>
        <span className="nav-label">NFTs</span>
      </button>
      <button
        className={`nav-btn ${isActive('/profile') ? 'active' : ''}`}
        onClick={() => navigate('/profile')}
      >
        <span className="nav-icon">👤</span>
        <span className="nav-label">Profile</span>
      </button>
    </nav>
  );
};

export default Navbar;
