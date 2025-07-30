// API配置
const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  TIMEOUT: 10000,
  WITH_CREDENTIALS: true,
  HEADERS: {
    'Content-Type': 'application/json',
  }
};

export default API_CONFIG;