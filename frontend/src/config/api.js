// API配置 - 统一的API配置管理
const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000,
  WITH_CREDENTIALS: true,
  HEADERS: {
    'Content-Type': 'application/json',
  },
  // CSRF配置
  CSRF_HEADER_NAME: 'X-CSRFToken',
  CSRF_COOKIE_NAME: 'csrftoken',
  // 环境配置
  IS_DEVELOPMENT: import.meta.env.DEV,
  IS_PRODUCTION: import.meta.env.PROD,
};

export default API_CONFIG;