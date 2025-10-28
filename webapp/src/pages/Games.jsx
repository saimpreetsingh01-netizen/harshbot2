import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ItemCard from '../components/ItemCard';
import { getGames, getCategories } from '../utils/api';
import './ContentPage.css';

const Games = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [categories, setCategories] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadGames();
  }, [search, category, page]);

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      const gameCategories = response.data.software.filter(cat => 
        cat.toLowerCase().includes('game')
      );
      setCategories(gameCategories);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadGames = async () => {
    setLoading(true);
    try {
      const response = await getGames({ search, category, page });
      setGames(response.data.games);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error('Error loading games:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    setSearch(e.target.value);
    setPage(1);
  };

  const handleCategoryChange = (e) => {
    setCategory(e.target.value);
    setPage(1);
  };

  return (
    <div className="page content-page">
      <div className="page-header">
        <h1>🎮 Games</h1>
      </div>

      <div className="filters">
        <input
          type="text"
          className="search-input"
          placeholder="🔍 Search games..."
          value={search}
          onChange={handleSearch}
        />

        <select
          className="category-select"
          value={category}
          onChange={handleCategoryChange}
        >
          <option value="all">All Categories</option>
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <>
          <div className="items-list">
            {games.length > 0 ? (
              games.map((game) => (
                <ItemCard key={game._id} item={game} type="software" />
              ))
            ) : (
              <div className="no-items">No games found</div>
            )}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="page-btn"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                ← Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages}
              </span>
              <button
                className="page-btn"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      <Navbar />
    </div>
  );
};

export default Games;
