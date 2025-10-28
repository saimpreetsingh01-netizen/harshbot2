import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ItemCard from '../components/ItemCard';
import { getMovies } from '../utils/api';
import './ContentPage.css';

const Movies = () => {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const movieCategories = [
    'NETFLIX', 'PRIME', 'HOTSTAR', 'HINDI', 'ENGLISH',
    'TAMIL', 'TELUGU', 'MALAYALAM', 'KANNADA',
    'BOLLYWOOD', 'HOLLYWOOD', 'SOUTH', 'WEB-SERIES'
  ];

  useEffect(() => {
    loadMovies();
  }, [search, category, page]);

  const loadMovies = async () => {
    setLoading(true);
    try {
      const response = await getMovies({ search, category, page });
      setMovies(response.data.movies);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error('Error loading movies:', error);
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
        <h1>🎬 Movies</h1>
      </div>

      <div className="filters">
        <input
          type="text"
          className="search-input"
          placeholder="🔍 Search movies..."
          value={search}
          onChange={handleSearch}
        />

        <select
          className="category-select"
          value={category}
          onChange={handleCategoryChange}
        >
          <option value="all">All Categories</option>
          {movieCategories.map((cat) => (
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
            {movies.length > 0 ? (
              movies.map((movie) => (
                <ItemCard key={movie._id} item={movie} type="movie" />
              ))
            ) : (
              <div className="no-items">No movies found</div>
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

export default Movies;
