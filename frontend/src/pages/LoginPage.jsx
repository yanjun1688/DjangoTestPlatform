import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import api from '../utils/api';
import './LoginPage.css';

const LoginPage = ({ setUser }) => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [networkError, setNetworkError] = useState('');
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
    setNetworkError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setNetworkError('');
    try {
      const response = await api.post('/api/user/auth/login/', formData);
      if (response.data.message === '登录成功') {
        setUser(response.data.user);
        navigate('/dashboard');
      }
    } catch (error) {
      if (error.response && error.response.data) {
        if (typeof error.response.data === 'object') {
          const fieldErrors = Object.values(error.response.data).flat();
          setError(fieldErrors.join(', '));
        } else {
          setError(error.response.data);
        }
      } else {
        setNetworkError('网络错误或跨域/CSRF校验失败，请检查后端服务、跨域设置或刷新页面重试。');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>API测试平台</h1>
          <p>请登录您的账户</p>
        </div>
        {networkError && (
          <div className="network-error-message">{networkError}</div>
        )}
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">用户名</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="请输入用户名"
              required
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              placeholder="请输入密码"
              required
              disabled={loading}
            />
          </div>
          {error && (
            <div className="error-message">{error}</div>
          )}
          <button type="submit" className="login-button" disabled={loading}>
            {loading ? '登录中...' : '登录'}
          </button>
        </form>
        <div className="login-footer">
          <p>测试账号：admin / admin123</p>
        </div>
      </div>
    </div>
  );
};

LoginPage.propTypes = {
  setUser: PropTypes.func.isRequired
};

export default LoginPage; 