import { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ItemCard from '../components/ItemCard';
import { getSoftware, getCategories } from '../utils/api';
import './ContentPage.css';

const Software = () => {
  const [software, setSoftware] = useState([]);
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
    loadSoftware();
  }, [search, category, page]);

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      const softwareCategories = response.data.software.filter(cat => 
        !cat.toLowerCase().includes('game')
      );
      setCategories(softwareCategories);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadSoftware = async () => {
    setLoading(true);
    try {
      const response = await getSoftware({ search, category, page });
      setSoftware(response.data.software);
      setTotalPages(response.data.pages);
    } catch (error) {
      console.error('Error loading software:', error);
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
        <h1>💻 Software</h1>
      </div>

      <div className="filters">
        <input
          type="text"
          className="search-input"
          placeholder="🔍 Search software..."
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
            {software.length > 0 ? (
              software.map((item) => (
                <ItemCard key={item._id} item={item} type="software" />
              ))
            ) : (
              <div className="no-items">No software found</div>
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

export default Software;
