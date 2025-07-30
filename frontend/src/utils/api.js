import axios from 'axios';
import Logger from './logger';
import API_CONFIG from '../config/api';

// 获取cookie中的csrftoken
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
    if (['post', 'put', 'patch', 'delete'].includes(config.method)) {
      const csrftoken = getCookie('csrftoken');
      if (csrftoken) {
        config.headers['X-CSRFToken'] = csrftoken;
      }
    }
    Logger.apiRequest(config.method?.toUpperCase(), config.url, config.data);
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
    Logger.apiResponse(
      response.config.method?.toUpperCase(),
      response.config.url,
      response.status,
      response.data
    );
    return response;
  },
  (error) => {
    Logger.apiResponse(
      error.config?.method?.toUpperCase(),
      error.config?.url,
      error.response?.status || 'NETWORK_ERROR',
      error.response?.data
    );
    return Promise.reject(error);
  }
);

export default api; 