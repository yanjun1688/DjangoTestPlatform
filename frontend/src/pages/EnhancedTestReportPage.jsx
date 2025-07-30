import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography, Card, Row, Col, Table, Button, Tag, Statistic,
  Spin, Alert, Divider, Space, Progress, Tooltip,
  message, Drawer, Tabs, Select, Timeline, Badge
} from 'antd';
import {
  DownloadOutlined, ReloadOutlined, ArrowLeftOutlined,
  EyeOutlined, CheckCircleOutlined, CloseCircleOutlined,
  ExclamationCircleOutlined, ClockCircleOutlined,
  BarChartOutlined, PieChartOutlined, LineChartOutlined,
  ThunderboltOutlined, BugOutlined, TrophyOutlined,
  DashboardOutlined, ShareAltOutlined, CalendarOutlined
} from '@ant-design/icons';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  Filler,
  RadialLinearScale,
} from 'chart.js';
import { Bar, Pie, Line, Doughnut, Radar } from 'react-chartjs-2';
import api from '../utils/api';
import Logger from '../utils/logger';

// 注册 Chart.js 组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  LineElement,
  PointElement,
  Title,
  ChartTooltip,
  Legend,
  Filler,
  RadialLinearScale
);

const { Title: AntTitle } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

const EnhancedTestReportPage = () => {
  const { runId } = useParams();
  const navigate = useNavigate();
  
  const [testRun, setTestRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedResult, setSelectedResult] = useState(null);
  const [detailVisible, setDetailVisible] = useState(false);
  
  useEffect(() => {
    if (runId) {
      fetchTestRun();
    }
  }, [runId]);

  const fetchTestRun = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/reports/test-runs/${runId}/`);
      setTestRun(response.data);
    } catch (error) {
      Logger.errorWithContext('fetchTestRun', error);
      message.error('获取测试报告失败');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'passed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': return 'success';
      case 'failed': return 'error';
      case 'error': return 'warning';
      default: return 'default';
    }
  };

  const renderKPICards = () => {
    if (!testRun) return null;

    const kpis = [
      {
        title: '总用例数',
        value: testRun.total_tests,
        icon: <BarChartOutlined />,
        color: '#1890ff',
      },
      {
        title: '通过率',
        value: testRun.success_rate,
        suffix: '%',
        icon: <TrophyOutlined />,
        color: testRun.success_rate >= 90 ? '#52c41a' : testRun.success_rate >= 70 ? '#faad14' : '#ff4d4f',
      },
      {
        title: '平均响应时间',
        value: testRun.avg_response_time || 0,
        suffix: 'ms',
        icon: <ThunderboltOutlined />,
        color: '#722ed1',
      },
      {
        title: '错误率',
        value: ((testRun.error_tests / testRun.total_tests) * 100).toFixed(1),
        suffix: '%',
        icon: <BugOutlined />,
        color: testRun.error_tests > 0 ? '#ff4d4f' : '#52c41a',
      }
    ];

    return (
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        {kpis.map((kpi, index) => (
          <Col xs={12} sm={6} key={index}>
            <Card 
              style={{ 
                textAlign: 'center', 
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }} 
              hoverable
            >
              <div style={{ fontSize: '32px', color: kpi.color, marginBottom: '8px' }}>
                {kpi.icon}
              </div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: kpi.color }}>
                {kpi.value}{kpi.suffix}
              </div>
              <div style={{ fontSize: '14px', color: '#666' }}>{kpi.title}</div>
            </Card>
          </Col>
        ))}
      </Row>
    );
  };

  const renderOverviewCharts = () => {
    if (!testRun) return null;

    const pieData = {
      labels: ['通过', '失败', '错误'],
      datasets: [{
        data: [testRun.passed_tests, testRun.failed_tests, testRun.error_tests],
        backgroundColor: [
          'rgba(82, 196, 26, 0.8)',
          'rgba(255, 77, 79, 0.8)',
          'rgba(250, 173, 20, 0.8)'
        ],
        borderColor: [
          'rgba(82, 196, 26, 1)',
          'rgba(255, 77, 79, 1)',
          'rgba(250, 173, 20, 1)'
        ],
        borderWidth: 2,
      }]
    };

    const pieOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            usePointStyle: true,
            font: {
              size: 14
            }
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || '';
              const value = context.parsed || 0;
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((value / total) * 100).toFixed(1);
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    };

    // 响应时间分布图
    const responseTimeData = testRun.results
      ? testRun.results
          .filter(result => result.response_time)
          .slice(0, 15)
          .map(result => ({
            name: result.test_case_name.length > 12 
              ? result.test_case_name.substring(0, 12) + '...' 
              : result.test_case_name,
            time: result.response_time
          }))
      : [];

    const barData = {
      labels: responseTimeData.map(item => item.name),
      datasets: [{
        label: '响应时间 (ms)',
        data: responseTimeData.map(item => item.time),
        backgroundColor: 'rgba(24, 144, 255, 0.6)',
        borderColor: 'rgba(24, 144, 255, 1)',
        borderWidth: 1,
      }]
    };

    const barOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            title: (context) => `测试用例: ${context[0].label}`,
            label: (context) => `响应时间: ${context.parsed.y}ms`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '响应时间 (ms)'
          }
        }
      }
    };

    return (
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card 
            title={<><PieChartOutlined /> 测试结果分布</>} 
            style={{ borderRadius: '12px' }}
          >
            <div style={{ height: '300px' }}>
              <Pie data={pieData} options={pieOptions} />
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card 
            title={<><BarChartOutlined /> 响应时间分布</>} 
            style={{ borderRadius: '12px' }}
          >
            <div style={{ height: '300px' }}>
              <Bar data={barData} options={barOptions} />
            </div>
          </Card>
        </Col>
      </Row>
    );
  };

  const renderTestTimeline = () => {
    if (!testRun?.results) return null;

    const timelineItems = testRun.results.slice(0, 10).map((result, index) => ({
      dot: getStatusIcon(result.status),
      color: result.status === 'passed' ? 'green' : result.status === 'failed' ? 'red' : 'orange',
      children: (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
            {result.test_case_name}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {result.response_time ? `${result.response_time.toFixed(2)}ms` : ''} • 
            {new Date(result.executed_at).toLocaleTimeString()}
          </div>
          {result.error_message && (
            <div style={{ fontSize: '12px', color: '#ff4d4f', marginTop: '4px' }}>
              {result.error_message}
            </div>
          )}
        </div>
      )
    }));

    return (
      <Card 
        title={<><ClockCircleOutlined /> 测试执行时间线</>}
        style={{ borderRadius: '12px' }}
      >
        <Timeline items={timelineItems} />
      </Card>
    );
  };

  const filteredResults = testRun?.results?.filter(result => 
    filterStatus === 'all' || result.status === filterStatus
  ) || [];

  const columns = [
    {
      title: '测试用例',
      dataIndex: 'test_case_name',
      key: 'test_case_name',
      ellipsis: true,
      render: (text) => (
        <Tooltip title={text}>
          <span>{text}</span>
        </Tooltip>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={getStatusColor(status)} icon={getStatusIcon(status)}>
          {status === 'passed' ? '通过' : status === 'failed' ? '失败' : '错误'}
        </Tag>
      ),
    },
    {
      title: '响应时间',
      dataIndex: 'response_time',
      key: 'response_time',
      width: 120,
      render: (time) => (
        <span style={{ 
          color: time > 1000 ? '#ff4d4f' : time > 500 ? '#faad14' : '#52c41a' 
        }}>
          {time ? `${time.toFixed(2)}ms` : '-'}
        </span>
      ),
      sorter: (a, b) => (a.response_time || 0) - (b.response_time || 0),
    },
    {
      title: '状态码',
      dataIndex: 'response_code',
      key: 'response_code',
      width: 100,
      render: (code) => (
        <Badge 
          count={code} 
          style={{ 
            backgroundColor: code >= 200 && code < 300 ? '#52c41a' : '#ff4d4f' 
          }} 
        />
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedResult(record);
            setDetailVisible(true);
          }}
        >
          详情
        </Button>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '60vh' 
      }}>
        <Spin size="large" tip="加载测试报告中..." />
      </div>
    );
  }

  if (!testRun) {
    return (
      <Alert
        message="未找到测试报告"
        description="请检查报告ID是否正确"
        type="error"
        showIcon
      />
    );
  }

  return (
    <div style={{ 
      padding: '24px', 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      minHeight: '100vh' 
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ 
          marginBottom: '24px', 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          background: '#fff',
          padding: '16px 24px',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/reports')}
            >
              返回列表
            </Button>
            <AntTitle level={2} style={{ margin: 0 }}>
              {testRun.name}
            </AntTitle>
            <Tag 
              color={testRun.status === 'completed' ? 'green' : testRun.status === 'failed' ? 'red' : 'blue'}
              style={{ fontSize: '14px', padding: '4px 12px' }}
            >
              {testRun.status === 'completed' ? '已完成' : 
               testRun.status === 'failed' ? '失败' : '运行中'}
            </Tag>
          </div>
          <Space>
            <Button icon={<CalendarOutlined />}>
              {new Date(testRun.start_time).toLocaleDateString()}
            </Button>
            <Button icon={<ShareAltOutlined />}>
              分享报告
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchTestRun}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
            >
              导出报告
            </Button>
          </Space>
        </div>

        {/* KPI Cards */}
        {renderKPICards()}

        {/* Main Content */}
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          style={{
            background: '#fff',
            borderRadius: '12px',
            padding: '0 24px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
          }}
        >
          <TabPane tab={<><PieChartOutlined />概览</>} key="overview">
            <div style={{ padding: '24px 0' }}>
              {renderOverviewCharts()}
            </div>
          </TabPane>
          
          <TabPane tab={<><BarChartOutlined />详细结果</>} key="details">
            <div style={{ padding: '24px 0' }}>
              <Card 
                title="测试结果" 
                style={{ borderRadius: '12px' }}
                extra={(
                  <Select
                    value={filterStatus}
                    onChange={setFilterStatus}
                    style={{ width: 120 }}
                  >
                    <Option value="all">全部</Option>
                    <Option value="passed">通过</Option>
                    <Option value="failed">失败</Option>
                    <Option value="error">错误</Option>
                  </Select>
                )}
              >
                <Table
                  columns={columns}
                  dataSource={filteredResults}
                  rowKey="id"
                  pagination={{
                    pageSize: 20,
                    showSizeChanger: true,
                    showQuickJumper: true,
                    showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
                  }}
                  size="middle"
                />
              </Card>
            </div>
          </TabPane>
          
          <TabPane tab={<><ClockCircleOutlined />执行时间线</>} key="timeline">
            <div style={{ padding: '24px 0' }}>
              <Row gutter={[24, 24]}>
                <Col xs={24} lg={16}>
                  {renderTestTimeline()}
                </Col>
                <Col xs={24} lg={8}>
                  <Card 
                    title="执行统计" 
                    style={{ borderRadius: '12px' }}
                  >
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{ fontSize: '14px', color: '#666' }}>执行时长</div>
                      <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
                        {testRun.duration_display}
                      </div>
                    </div>
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{ fontSize: '14px', color: '#666' }}>开始时间</div>
                      <div style={{ fontSize: '14px' }}>
                        {new Date(testRun.start_time).toLocaleString()}
                      </div>
                    </div>
                    <div style={{ marginBottom: '16px' }}>
                      <div style={{ fontSize: '14px', color: '#666' }}>结束时间</div>
                      <div style={{ fontSize: '14px' }}>
                        {testRun.end_time ? new Date(testRun.end_time).toLocaleString() : '运行中'}
                      </div>
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', color: '#666' }}>执行者</div>
                      <div style={{ fontSize: '14px' }}>
                        {testRun.executed_by_username || '系统'}
                      </div>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
          </TabPane>
        </Tabs>
      </div>

      {/* Detail Drawer */}
      <Drawer
        title="测试结果详情"
        placement="right"
        onClose={() => setDetailVisible(false)}
        open={detailVisible}
        width={600}
      >
        {selectedResult && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <h3>{selectedResult.test_case_name}</h3>
              <Tag color={getStatusColor(selectedResult.status)} icon={getStatusIcon(selectedResult.status)}>
                {selectedResult.status === 'passed' ? '通过' : 
                 selectedResult.status === 'failed' ? '失败' : '错误'}
              </Tag>
            </div>
            
            <Divider />
            
            <div style={{ marginBottom: '16px' }}>
              <h4>基本信息</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '8px' }}>
                <span style={{ fontWeight: 'bold' }}>API:</span>
                <span>
                  <Tag color="blue">{selectedResult.api_method}</Tag>
                  {selectedResult.api_name}
                </span>
                
                <span style={{ fontWeight: 'bold' }}>URL:</span>
                <code style={{ background: '#f5f5f5', padding: '2px 6px', borderRadius: '3px' }}>
                  {selectedResult.api_url}
                </code>
                
                <span style={{ fontWeight: 'bold' }}>状态码:</span>
                <Badge 
                  count={selectedResult.response_code} 
                  style={{ 
                    backgroundColor: selectedResult.response_code >= 200 && selectedResult.response_code < 300 ? '#52c41a' : '#ff4d4f' 
                  }} 
                />
                
                <span style={{ fontWeight: 'bold' }}>响应时间:</span>
                <span style={{ 
                  color: selectedResult.response_time > 1000 ? '#ff4d4f' : selectedResult.response_time > 500 ? '#faad14' : '#52c41a' 
                }}>
                  {selectedResult.response_time ? `${selectedResult.response_time.toFixed(2)}ms` : '-'}
                </span>
              </div>
            </div>

            {selectedResult.error_message && (
              <div style={{ marginBottom: '16px' }}>
                <h4>错误信息</h4>
                <Alert
                  message={selectedResult.error_message}
                  type="error"
                  showIcon
                />
              </div>
            )}

            {selectedResult.response_body && (
              <div>
                <h4>响应内容</h4>
                <div style={{ 
                  background: '#f5f5f5', 
                  padding: '12px', 
                  borderRadius: '6px',
                  maxHeight: '300px',
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '12px'
                }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(JSON.parse(selectedResult.response_body || '{}'), null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default EnhancedTestReportPage;