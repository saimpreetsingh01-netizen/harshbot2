import { useState, useEffect } from 'react';
import WebApp from '@twa-dev/sdk';
import Navbar from '../components/Navbar';
import { getNFTs } from '../utils/api';
import './NFTs.css';

const NFTs = () => {
  const [nfts, setNfts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNFTs();
  }, []);

  const loadNFTs = async () => {
    try {
      const response = await getNFTs();
      setNfts(response.data.nfts);
    } catch (error) {
      console.error('Error loading NFTs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = (nft) => {
    WebApp.openLink(nft.link);
    WebApp.showAlert(`🎨 Opening ${nft.name}!\n\nFollow the instructions to claim your free NFT.`);
  };

  return (
    <div className="page nfts-page">
      <div className="page-header">
        <h1>🎨 Free NFTs</h1>
        <p className="page-subtitle">Claim your free NFT collectibles</p>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <div className="nfts-grid">
          {nfts.length > 0 ? (
            nfts.map((nft) => (
              <div key={nft._id} className="nft-card">
                <div className="nft-icon">🎨</div>
                <h3 className="nft-name">{nft.name}</h3>
                <p className="nft-description">{nft.description}</p>
                <div className="nft-stats">
                  <span className="nft-stat">
                    👥 {nft.claims?.length || 0} claimed
                  </span>
                </div>
                <button
                  className="claim-btn"
                  onClick={() => handleClaim(nft)}
                >
                  🎁 Claim Now
                </button>
              </div>
            ))
          ) : (
            <div className="no-items">No NFTs available at the moment</div>
          )}
        </div>
      )}

      <Navbar />
    </div>
  );
};

export default NFTs;
