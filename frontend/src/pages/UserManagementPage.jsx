import { useState, useEffect } from 'react';
import axios from 'axios';
import API_CONFIG from '../config/api';
import ErrorHandler from '../utils/errorHandler';
import './UserManagementPage.css';
import BackButton from '../components/BackButton';

const UserManagementPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: 'user',
    phone: '',
    department: '',
    password: '',
    confirm_password: ''
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.BASE_URL}/api/user/users/`, {
        withCredentials: true
      });
      setUsers(response.data);
    } catch (error) {
      ErrorHandler.handleApiError(error, '获取用户列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_CONFIG.BASE_URL}/api/user/users/`, formData, {
        withCredentials: true
      });
      setShowCreateForm(false);
      setFormData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        role: 'user',
        phone: '',
        department: '',
        password: '',
        confirm_password: ''
      });
      ErrorHandler.showSuccess('用户创建成功');
      fetchUsers();
    } catch (error) {
      ErrorHandler.handleFormError(error);
    }
  };

  const handleUpdateUser = async (e) => {
    e.preventDefault();
    try {
      const updateData = { ...formData };
      if (!updateData.password) {
        delete updateData.password;
        delete updateData.confirm_password;
      }
      
      await axios.put(`${API_CONFIG.BASE_URL}/api/user/users/${editingUser.id}/`, updateData, {
        withCredentials: true
      });
      setEditingUser(null);
      setFormData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        role: 'user',
        phone: '',
        department: '',
        password: '',
        confirm_password: ''
      });
      ErrorHandler.showSuccess('用户更新成功');
      fetchUsers();
    } catch (error) {
      ErrorHandler.handleFormError(error);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (window.confirm('确定要删除这个用户吗？')) {
      try {
        await axios.delete(`${API_CONFIG.BASE_URL}/api/user/users/${userId}/`, {
          withCredentials: true
        });
        ErrorHandler.showSuccess('用户删除成功');
        fetchUsers();
      } catch (error) {
        ErrorHandler.handleApiError(error, '删除用户失败');
      }
    }
  };

  const handleToggleActive = async (userId) => {
    try {
      await axios.post(`${API_CONFIG.BASE_URL}/api/user/users/${userId}/toggle_active/`, {}, {
        withCredentials: true
      });
      ErrorHandler.showSuccess('用户状态更新成功');
      fetchUsers();
    } catch (error) {
      ErrorHandler.handleApiError(error, '更新用户状态失败');
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email || '',
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      role: user.role,
      phone: user.phone || '',
      department: user.department || '',
      password: '',
      confirm_password: ''
    });
  };

  const cancelEdit = () => {
    setEditingUser(null);
    setShowCreateForm(false);
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      role: 'user',
      phone: '',
      department: '',
      password: '',
      confirm_password: ''
    });
  };

  if (loading) {
    return <div className="loading">加载中...</div>;
  }

  return (
    <div className="user-management">
      <BackButton />
      <div className="user-management-header">
        <h1>用户管理</h1>
        <button 
          className="create-user-btn"
          onClick={() => setShowCreateForm(true)}
        >
          创建用户
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 创建/编辑用户表单 */}
      {(showCreateForm || editingUser) && (
        <div className="user-form-overlay">
          <div className="user-form-card">
            <h2>{editingUser ? '编辑用户' : '创建用户'}</h2>
            <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser}>
              <div className="form-row">
                <div className="form-group">
                  <label>用户名 *</label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                <div className="form-group">
                  <label>邮箱</label>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>姓</label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                  />
                </div>
                <div className="form-group">
                  <label>名</label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>角色</label>
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                  >
                    <option value="user">普通用户</option>
                    <option value="admin">管理员</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>手机号</label>
                  <input
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>部门</label>
                <input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>{editingUser ? '新密码' : '密码 *'}</label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required={!editingUser}
                  />
                </div>
                <div className="form-group">
                  <label>确认密码 *</label>
                  <input
                    type="password"
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleInputChange}
                    required={!editingUser}
                  />
                </div>
              </div>

              <div className="form-actions">
                <button type="submit" className="submit-btn">
                  {editingUser ? '更新' : '创建'}
                </button>
                <button type="button" className="cancel-btn" onClick={cancelEdit}>
                  取消
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 用户列表 */}
      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>用户名</th>
              <th>姓名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>部门</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.username}</td>
                <td>{user.first_name} {user.last_name}</td>
                <td>{user.email}</td>
                <td>
                  <span className={`role-badge ${user.role}`}>
                    {user.role === 'admin' ? '管理员' : '普通用户'}
                  </span>
                </td>
                <td>{user.department}</td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? '启用' : '禁用'}
                  </span>
                </td>
                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="edit-btn"
                      onClick={() => handleEdit(user)}
                    >
                      编辑
                    </button>
                    <button
                      className={`toggle-btn ${user.is_active ? 'deactivate' : 'activate'}`}
                      onClick={() => handleToggleActive(user.id)}
                    >
                      {user.is_active ? '禁用' : '启用'}
                    </button>
                    <button
                      className="delete-btn"
                      onClick={() => handleDeleteUser(user.id)}
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default UserManagementPage; 