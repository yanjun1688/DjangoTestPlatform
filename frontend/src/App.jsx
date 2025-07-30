import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import axios from 'axios';
import API_CONFIG from './config/api';
import ErrorHandler from './utils/errorHandler';
import NotificationCenter from './components/NotificationCenter';
import ThemeProvider from './components/ThemeProvider';
import ThemeToggle from './components/ThemeToggle';
import TestCasePage from './pages/TestCasePage';
import TestResultPage from './pages/TestResultPage';
import ApiDefinitionPage from './pages/ApiDefinitionPage';
import DebugPage from './pages/DebugPage';
import LoginPage from './pages/LoginPage';
import UserManagementPage from './pages/UserManagementPage';
import DashboardPage from './pages/DashboardPage';
import ReportListPage from './pages/ReportListPage';
import TestPlanPage from './pages/TestPlanPage';
import TestReportPage from './pages/TestReportPage';
import MockServerPage from './pages/MockServerPage';
import InteractiveTestEditor from './pages/InteractiveTestEditor';
import EnvironmentManagePage from './pages/EnvironmentManagePage';
import TestFlowOrchestrationPage from './pages/TestFlowOrchestrationPage';
import EnhancedTestReportPage from './pages/EnhancedTestReportPage';
import './App.css';
import './styles/theme.css';

// 路由保护组件
const ProtectedRoute = ({ children, user }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  user: PropTypes.object
};

// 管理员路由保护组件
const AdminRoute = ({ children, user }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (!user.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
};

AdminRoute.propTypes = {
  children: PropTypes.node.isRequired,
  user: PropTypes.object
};

// 主应用组件
const AppContent = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get(`${API_CONFIG.BASE_URL}/api/user/auth/check_auth/`, {
        withCredentials: true
      });
      if (response.data.authenticated) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.log('Auth check failed:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.get('/api/user/auth/logout/');
      setUser(null);
      navigate('/login');
      ErrorHandler.showSuccess('已成功退出登录');
    } catch (error) {
      ErrorHandler.handleApiError(error, '退出登录失败');
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>加载中...</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="app">
        <Routes>
          <Route path="/login" element={<LoginPage setUser={setUser} />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>API测试平台</h1>
          <div className="user-info">
            <NotificationCenter currentUser={user} />
            <ThemeToggle />
            <span className="username">
              {user.first_name || user.username}
              {user.is_admin && <span className="admin-badge">管理员</span>}
            </span>
            <button onClick={handleLogout} className="logout-btn">
              退出登录
            </button>
          </div>
        </div>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/dashboard" element={
            <ProtectedRoute user={user}>
              <DashboardPage user={user} />
            </ProtectedRoute>
          } />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/test-results" element={
            <ProtectedRoute user={user}>
              <TestResultPage />
            </ProtectedRoute>
          } />
          <Route path="/api-definitions" element={
            <ProtectedRoute user={user}>
              <ApiDefinitionPage />
            </ProtectedRoute>
          } />
          <Route path="/debug" element={
            <ProtectedRoute user={user}>
              <DebugPage />
            </ProtectedRoute>
          } />
          <Route path="/user-management" element={
            <AdminRoute user={user}>
              <UserManagementPage />
            </AdminRoute>
          } />
          <Route path="/reports" element={
            <ProtectedRoute user={user}>
              <ReportListPage />
            </ProtectedRoute>
          } />
          <Route path="/reports/:runId" element={
            <ProtectedRoute user={user}>
              <TestReportPage />
            </ProtectedRoute>
          } />
          <Route path="/test-plans" element={
            <ProtectedRoute user={user}>
              <TestPlanPage />
            </ProtectedRoute>
          } />
          <Route path="/test-cases" element={
            <ProtectedRoute user={user}>
              <TestCasePage />
            </ProtectedRoute>
          } />
          <Route path="/interactive-editor" element={
            <ProtectedRoute user={user}>
              <InteractiveTestEditor />
            </ProtectedRoute>
          } />
          <Route path="/environments" element={
            <ProtectedRoute user={user}>
              <EnvironmentManagePage />
            </ProtectedRoute>
          } />
          <Route path="/workflow-orchestration" element={
            <ProtectedRoute user={user}>
              <TestFlowOrchestrationPage />
            </ProtectedRoute>
          } />
          <Route path="/enhanced-reports/:runId" element={
            <ProtectedRoute user={user}>
              <EnhancedTestReportPage />
            </ProtectedRoute>
          } />
          <Route path="/mock-server" element={
            <ProtectedRoute user={user}>
              <MockServerPage />
            </ProtectedRoute>
          } />
          <Route path="/login" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
};

// 根App组件
const App = () => {
  return (
    <ThemeProvider>
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  );
};

export default App;