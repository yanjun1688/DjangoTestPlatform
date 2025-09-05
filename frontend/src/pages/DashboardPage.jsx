import { useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import { useState, useEffect } from 'react';
import './DashboardPage.css';
import BackButton from '../components/BackButton';

const features = [
  { key: 'users', title: '用户管理', desc: '管理平台用户（仅管理员）', path: '/user-management', icon: '👥', admin: true },
  { key: 'environments', title: '环境管理', desc: '管理测试环境和变量', path: '/environments', icon: '🌍' },
  { key: 'api', title: 'API定义', desc: '管理API接口定义', path: '/api-definitions', icon: '🔗' },
  { key: 'testcases', title: '测试用例', desc: '管理和执行API测试用例', path: '/test-cases', icon: '📝' },
  { key: 'interactive-editor', title: '交互式编辑器', desc: '三窗格交互式测试用例编辑器', path: '/interactive-editor', icon: '🎯' },
  { key: 'testplans', title: '测试计划', desc: '管理测试计划和历史报告', path: '/test-plans', icon: '📋' },
  { key: 'workflow', title: '流程编排', desc: '设计和管理测试工作流程', path: '/workflow-orchestration', icon: '🔄' },
  { key: 'mock', title: 'Mock Server', desc: '创建和管理Mock API接口', path: '/mock-server', icon: '🔄' },
  { key: 'results', title: '测试结果', desc: '查看测试执行结果', path: '/test-results', icon: '📊' },
  { key: 'reports', title: '测试报告', desc: '查看可视化测试报告', path: '/reports', icon: '📈' },
  { key: 'debug', title: '调试日志', desc: '查看接口调试日志', path: '/debug', icon: '🐛' },
];

const DashboardPage = ({ user }) => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalTests: 0,
    passedTests: 0,
    failedTests: 0,
    avgResponseTime: 0
  });
  const [loading, setLoading] = useState(true);

  // 获取仪表盘统计数据
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        // 模拟API调用 - 实际应用中应该调用真实的API
        const mockStats = {
          totalTests: 156,
          passedTests: 134,
          failedTests: 22,
          avgResponseTime: 245
        };
        
        setTimeout(() => {
          setStats(mockStats);
          setLoading(false);
        }, 500);
      } catch (error) {
        console.error('获取统计数据失败:', error);
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const successRate = stats.totalTests > 0 ? ((stats.passedTests / stats.totalTests) * 100).toFixed(1) : 0;

  return (
    <div className="dashboard-container">
      <BackButton />
      <div className="dashboard-header">
        <h1 className="dashboard-title">测试平台仪表盘</h1>
        <p className="dashboard-subtitle">欢迎回来，{user.username}！</p>
      </div>

      {/* KPI 统计卡片 */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon">📊</div>
          <div className="kpi-content">
            <div className="kpi-value">{loading ? '...' : stats.totalTests}</div>
            <div className="kpi-label">总测试数</div>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">✅</div>
          <div className="kpi-content">
            <div className="kpi-value">{loading ? '...' : `${successRate}%`}</div>
            <div className="kpi-label">成功率</div>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">⚡</div>
          <div className="kpi-content">
            <div className="kpi-value">{loading ? '...' : `${stats.avgResponseTime}ms`}</div>
            <div className="kpi-label">平均响应时间</div>
          </div>
        </div>
        
        <div className="kpi-card">
          <div className="kpi-icon">❌</div>
          <div className="kpi-content">
            <div className="kpi-value">{loading ? '...' : stats.failedTests}</div>
            <div className="kpi-label">失败测试</div>
          </div>
        </div>
      </div>

      {/* 快速操作区 */}
      <div className="quick-actions">
        <h2 className="section-title">快速操作</h2>
        <div className="quick-actions-grid">
          <button className="quick-action-btn primary" onClick={() => navigate('/test-cases?action=create')}>
            <span className="action-icon">➕</span>
            <span>创建测试用例</span>
          </button>
          <button className="quick-action-btn secondary" onClick={() => navigate('/test-plans?action=execute')}>
            <span className="action-icon">▶️</span>
            <span>执行测试计划</span>
          </button>
          <button className="quick-action-btn tertiary" onClick={() => navigate('/api-definitions?action=create')}>
            <span className="action-icon">🔗</span>
            <span>新建API定义</span>
          </button>
          <button className="quick-action-btn quaternary" onClick={() => navigate('/reports')}>
            <span className="action-icon">📊</span>
            <span>查看报告</span>
          </button>
        </div>
      </div>

      {/* 功能模块 */}
      <div className="features-section">
        <h2 className="section-title">功能模块</h2>
        <div className="dashboard-grid">
          {features.map(f => {
            if (f.admin && !user.is_admin) return null;
            return (
              <div className="dashboard-card" key={f.key} onClick={() => navigate(f.path)}>
                <div className="card-icon">{f.icon}</div>
                <div className="card-title">{f.title}</div>
                <div className="card-desc">{f.desc}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

DashboardPage.propTypes = {
  user: PropTypes.object.isRequired
};

export default DashboardPage; 