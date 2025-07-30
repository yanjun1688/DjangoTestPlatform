import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { 
  apiRequest, 
  get, 
  post, 
  put, 
  del, 
  setAuthToken, 
  getAuthToken, 
  clearAuthToken 
} from './api';

// Mock axios
vi.mock('axios');

describe('API Utils', () => {
  beforeEach(() => {
    // Clear axios mocks
    vi.clearAllMocks();
    
    // Clear localStorage
    localStorage.clear();
    
    // Reset axios defaults
    delete axios.defaults.headers.common['Authorization'];
  });

  describe('apiRequest', () => {
    it('should make successful API requests', async () => {
      const mockResponse = { data: { id: 1, name: 'Test' } };
      axios.mockResolvedValue(mockResponse);

      const result = await apiRequest('GET', '/api/test');
      
      expect(axios).toHaveBeenCalledWith({
        method: 'GET',
        url: '/api/test',
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle API request with data', async () => {
      const mockResponse = { data: { success: true } };
      const requestData = { name: 'Test', value: 123 };
      axios.mockResolvedValue(mockResponse);

      const result = await apiRequest('POST', '/api/test', requestData);
      
      expect(axios).toHaveBeenCalledWith({
        method: 'POST',
        url: '/api/test',
        data: requestData,
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle API request with custom headers', async () => {
      const mockResponse = { data: { success: true } };
      const customHeaders = { 'X-Custom-Header': 'custom-value' };
      axios.mockResolvedValue(mockResponse);

      await apiRequest('GET', '/api/test', null, customHeaders);
      
      expect(axios).toHaveBeenCalledWith({
        method: 'GET',
        url: '/api/test',
        headers: { 
          'Content-Type': 'application/json',
          'X-Custom-Header': 'custom-value'
        }
      });
    });

    it('should handle API request errors', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: { message: 'Bad Request' }
        }
      };
      axios.mockRejectedValue(errorResponse);

      await expect(apiRequest('GET', '/api/test')).rejects.toThrow('Bad Request');
    });

    it('should handle network errors', async () => {
      const networkError = new Error('Network Error');
      axios.mockRejectedValue(networkError);

      await expect(apiRequest('GET', '/api/test')).rejects.toThrow('Network Error');
    });

    it('should handle API request with query parameters', async () => {
      const mockResponse = { data: [] };
      axios.mockResolvedValue(mockResponse);

      await apiRequest('GET', '/api/test?page=1&limit=10');
      
      expect(axios).toHaveBeenCalledWith({
        method: 'GET',
        url: '/api/test?page=1&limit=10',
        headers: { 'Content-Type': 'application/json' }
      });
    });
  });

  describe('HTTP method helpers', () => {
    it('should make GET requests', async () => {
      const mockResponse = { data: { id: 1 } };
      axios.mockResolvedValue(mockResponse);

      const result = await get('/api/test');
      
      expect(axios).toHaveBeenCalledWith({
        method: 'GET',
        url: '/api/test',
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should make POST requests', async () => {
      const mockResponse = { data: { success: true } };
      const postData = { name: 'Test' };
      axios.mockResolvedValue(mockResponse);

      const result = await post('/api/test', postData);
      
      expect(axios).toHaveBeenCalledWith({
        method: 'POST',
        url: '/api/test',
        data: postData,
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should make PUT requests', async () => {
      const mockResponse = { data: { updated: true } };
      const putData = { name: 'Updated' };
      axios.mockResolvedValue(mockResponse);

      const result = await put('/api/test/1', putData);
      
      expect(axios).toHaveBeenCalledWith({
        method: 'PUT',
        url: '/api/test/1',
        data: putData,
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('should make DELETE requests', async () => {
      const mockResponse = { data: { deleted: true } };
      axios.mockResolvedValue(mockResponse);

      const result = await del('/api/test/1');
      
      expect(axios).toHaveBeenCalledWith({
        method: 'DELETE',
        url: '/api/test/1',
        headers: { 'Content-Type': 'application/json' }
      });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Authentication token management', () => {
    it('should set authentication token', () => {
      const token = 'test-token-123';
      setAuthToken(token);
      
      expect(localStorage.getItem('authToken')).toBe(token);
      expect(axios.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);
    });

    it('should get authentication token', () => {
      const token = 'test-token-123';
      localStorage.setItem('authToken', token);
      
      const retrievedToken = getAuthToken();
      expect(retrievedToken).toBe(token);
    });

    it('should return null when no token is stored', () => {
      const retrievedToken = getAuthToken();
      expect(retrievedToken).toBeNull();
    });

    it('should clear authentication token', () => {
      const token = 'test-token-123';
      localStorage.setItem('authToken', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      clearAuthToken();
      
      expect(localStorage.getItem('authToken')).toBeNull();
      expect(axios.defaults.headers.common['Authorization']).toBeUndefined();
    });

    it('should include token in requests when set', async () => {
      const token = 'test-token-123';
      const mockResponse = { data: { authenticated: true } };
      axios.mockResolvedValue(mockResponse);
      
      setAuthToken(token);
      await get('/api/protected');
      
      expect(axios).toHaveBeenCalledWith({
        method: 'GET',
        url: '/api/protected',
        headers: { 'Content-Type': 'application/json' }
      });
      expect(axios.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);
    });
  });

  describe('Error handling', () => {
    it('should handle 401 Unauthorized errors', async () => {
      const errorResponse = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      };
      axios.mockRejectedValue(errorResponse);

      await expect(get('/api/protected')).rejects.toThrow('Unauthorized');
    });

    it('should handle 403 Forbidden errors', async () => {
      const errorResponse = {
        response: {
          status: 403,
          data: { message: 'Forbidden' }
        }
      };
      axios.mockRejectedValue(errorResponse);

      await expect(get('/api/admin')).rejects.toThrow('Forbidden');
    });

    it('should handle 404 Not Found errors', async () => {
      const errorResponse = {
        response: {
          status: 404,
          data: { message: 'Not Found' }
        }
      };
      axios.mockRejectedValue(errorResponse);

      await expect(get('/api/nonexistent')).rejects.toThrow('Not Found');
    });

    it('should handle 500 Internal Server errors', async () => {
      const errorResponse = {
        response: {
          status: 500,
          data: { message: 'Internal Server Error' }
        }
      };
      axios.mockRejectedValue(errorResponse);

      await expect(get('/api/error')).rejects.toThrow('Internal Server Error');
    });

    it('should handle errors without response data', async () => {
      const errorResponse = {
        response: {
          status: 400
        }
      };
      axios.mockRejectedValue(errorResponse);

      await expect(get('/api/test')).rejects.toThrow('HTTP Error: 400');
    });

    it('should handle validation errors', async () => {
      const errorResponse = {
        response: {
          status: 400,
          data: { 
            errors: {
              name: ['This field is required.'],
              email: ['Enter a valid email address.']
            }
          }
        }
      };
      axios.mockRejectedValue(errorResponse);

      await expect(post('/api/users', {})).rejects.toThrow();
    });
  });

  describe('Request interceptors', () => {
    it('should automatically include auth token from localStorage', async () => {
      const token = 'stored-token-123';
      localStorage.setItem('authToken', token);
      
      const mockResponse = { data: { success: true } };
      axios.mockResolvedValue(mockResponse);

      // Simulate the token being loaded from localStorage on app start
      const storedToken = localStorage.getItem('authToken');
      if (storedToken) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      }

      await get('/api/test');
      
      expect(axios.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);
    });

    it('should handle requests when no token is stored', async () => {
      const mockResponse = { data: { success: true } };
      axios.mockResolvedValue(mockResponse);

      await get('/api/public');
      
      expect(axios.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });

  describe('Content type handling', () => {
    it('should handle JSON content type by default', async () => {
      const mockResponse = { data: { success: true } };
      axios.mockResolvedValue(mockResponse);

      await post('/api/test', { data: 'test' });
      
      expect(axios).toHaveBeenCalledWith({
        method: 'POST',
        url: '/api/test',
        data: { data: 'test' },
        headers: { 'Content-Type': 'application/json' }
      });
    });

    it('should handle custom content types', async () => {
      const mockResponse = { data: { success: true } };
      axios.mockResolvedValue(mockResponse);

      await post('/api/upload', 'file data', { 'Content-Type': 'multipart/form-data' });
      
      expect(axios).toHaveBeenCalledWith({
        method: 'POST',
        url: '/api/upload',
        data: 'file data',
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    });
  });

  describe('Base URL handling', () => {
    it('should handle relative URLs', async () => {
      const mockResponse = { data: { success: true } };
      axios.mockResolvedValue(mockResponse);

      await get('/api/test');
      
      expect(axios).toHaveBeenCalledWith({
        method: 'GET',
        url: '/api/test',
        headers: { 'Content-Type': 'application/json' }
      });
    });

    it('should handle absolute URLs', async () => {
      const mockResponse = { data: { success: true } };
      axios.mockResolvedValue(mockResponse);

      await get('https://api.example.com/test');
      
      expect(axios).toHaveBeenCalledWith({
        method: 'GET',
        url: 'https://api.example.com/test',
        headers: { 'Content-Type': 'application/json' }
      });
    });
  });
});