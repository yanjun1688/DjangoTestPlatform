import axios from 'axios';
import Logger from './logger';
import API_CONFIG from '../config/api';

// 获取CSRF token
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// 获取CSRF token
function getCSRFToken() {
  return getCookie(API_CONFIG.CSRF_COOKIE_NAME);
}

// 创建axios实例
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
  withCredentials: API_CONFIG.WITH_CREDENTIALS,
});

// 请求拦截器，自动加CSRF token
api.interceptors.request.use(
  (config) => {
    // 为非安全方法添加CSRF token
    if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
      const csrftoken = getCSRFToken();
      if (csrftoken) {
        config.headers[API_CONFIG.CSRF_HEADER_NAME] = csrftoken;
      }
    }
    
    // 记录请求日志（仅在开发环境）
    if (API_CONFIG.IS_DEVELOPMENT) {
      Logger.apiRequest(config.method?.toUpperCase(), config.url, config.data);
    }
    
    return config;
  },
  (error) => {
    Logger.error('Request error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 记录响应日志（仅在开发环境）
    if (API_CONFIG.IS_DEVELOPMENT) {
      Logger.apiResponse(
        response.config.method?.toUpperCase(),
        response.config.url,
        response.status,
        response.data
      );
    }
    return response;
  },
  (error) => {
    // 记录错误日志
    if (API_CONFIG.IS_DEVELOPMENT) {
      Logger.apiResponse(
        error.config?.method?.toUpperCase(),
        error.config?.url,
        error.response?.status || 'NETWORK_ERROR',
        error.response?.data
      );
    }
    
    // 统一错误处理
    if (error.response?.status === 403) {
      console.warn('CSRF token may be invalid, please refresh the page');
    }
    
    return Promise.reject(error);
  }
);

export default api; 