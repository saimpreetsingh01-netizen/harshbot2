import axios from 'axios';
import WebApp from '@twa-dev/sdk';

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return `${protocol}//${hostname}:8000`;
    }
    return `${protocol}//${hostname}`;
  }
  
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const initData = WebApp.initData;
  if (initData) {
    config.headers.Authorization = initData;
  }
  return config;
});

export const getGames = (params) => api.get('/api/games', { params });
export const getSoftware = (params) => api.get('/api/software', { params });
export const getMovies = (params) => api.get('/api/movies', { params });
export const getNFTs = () => api.get('/api/nfts');
export const getGameScripts = () => api.get('/api/gamescripts');
export const getUserProfile = () => api.get('/api/user/profile');
export const createDownload = (itemId, itemType = 'software') => api.post(`/api/download/${itemId}?item_type=${itemType}`);
export const getCategories = () => api.get('/api/categories');

export default api;
