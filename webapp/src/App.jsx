import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import WebApp from '@twa-dev/sdk';
import Home from './pages/Home';
import Games from './pages/Games';
import Software from './pages/Software';
import Movies from './pages/Movies';
import NFTs from './pages/NFTs';
import GameScripts from './pages/GameScripts';
import Profile from './pages/Profile';
import './App.css';

function App() {
  useEffect(() => {
    WebApp.ready();
    WebApp.expand();
    WebApp.setHeaderColor('#1a1a2e');
    WebApp.setBackgroundColor('#16213e');
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/games" element={<Games />} />
        <Route path="/software" element={<Software />} />
        <Route path="/movies" element={<Movies />} />
        <Route path="/nfts" element={<NFTs />} />
        <Route path="/scripts" element={<GameScripts />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
}

export default App;
