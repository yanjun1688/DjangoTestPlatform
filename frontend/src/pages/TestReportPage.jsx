import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography, Card, Row, Col, Table, Button, Tag, Statistic,
  Spin, Alert, Divider, Collapse, Space, Progress, Tooltip,
  message, Drawer, Modal
} from 'antd';
import {
  DownloadOutlined, ReloadOutlined, ArrowLeftOutlined,
  EyeOutlined, CheckCircleOutlined, CloseCircleOutlined,
  ExclamationCircleOutlined, ClockCircleOutlined,
  BarChartOutlined, PieChartOutlined
} from '@ant-design/icons';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import api from '../utils/api';
import Logger from '../utils/logger';
import CommentSection from '../components/CommentSection';

// 注册 Chart.js 组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  ChartTooltip,
  Legend
);

const { Title: AntTitle } = Typography;
const { Panel } = Collapse;

const TestReportPage = () => {
  const { runId } = useParams();
  const navigate = useNavigate();
  
  const [testRun, setTestRun] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exportLoading, setExportLoading] = useState(false);
  const [statisticsLoading, setStatisticsLoading] = useState(false);
  const [statistics, setStatistics] = useState(null);
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
      Logger.info('Fetching test run details', { runId });
      const response = await api.get(`/api/reports/test-runs/${runId}/`);
      setTestRun(response.data);
      Logger.debug('Test run data:', response.data);
      
      // 同时获取统计信息
      fetchStatistics();
    } catch (error) {
      Logger.errorWithContext('fetchTestRun', error);
      message.error('获取测试报告失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      setStatisticsLoading(true);
      const response = await api.get(`/api/reports/test-runs/${runId}/statistics/`);
      setStatistics(response.data);
      Logger.debug('Statistics data:', response.data);
    } catch (error) {
      Logger.errorWithContext('fetchStatistics', error);
    } finally {
      setStatisticsLoading(false);
    }
  };

  const handleExportHTML = async () => {
    try {
      setExportLoading(true);
      Logger.info('Exporting HTML report', { runId });
      
      const response = await api.get(`/api/reports/test-runs/${runId}/export_html/`, {
        responseType: 'blob'
      });
      
      // 创建下载链接
      const blob = new Blob([response.data], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `test_report_${runId}_${new Date().getTime()}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('报告导出成功');
    } catch (error) {
      Logger.errorWithContext('handleExportHTML', error);
      message.error('导出报告失败');
    } finally {
      setExportLoading(false);
    }
  };

  const handleViewDetails = (result) => {
    setSelectedResult(result);
    setDetailVisible(true);
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

  const renderPieChart = () => {
    if (!testRun) return null;

    const data = {
      labels: ['通过', '失败', '错误'],
      datasets: [
        {
          data: [testRun.passed_tests, testRun.failed_tests, testRun.error_tests],
          backgroundColor: ['#52c41a', '#ff4d4f', '#faad14'],
          borderColor: ['#389e0d', '#cf1322', '#d48806'],
          borderWidth: 2,
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom',
        },
        title: {
          display: true,
          text: '测试结果分布',
        },
      },
    };

    return <Pie data={data} options={options} />;
  };

  const renderResponseTimeChart = () => {
    if (!testRun?.results) return null;

    const responseTimeData = testRun.results
      .filter(result => result.response_time)
      .slice(0, 20) // 只显示前20个结果
      .map(result => ({
        name: result.test_case_name.length > 15 
          ? result.test_case_name.substring(0, 15) + '...' 
          : result.test_case_name,
        time: result.response_time
      }));

    const data = {
      labels: responseTimeData.map(item => item.name),
      datasets: [
        {
          label: '响应时间 (ms)',
          data: responseTimeData.map(item => item.time),
          backgroundColor: 'rgba(24, 144, 255, 0.6)',
          borderColor: 'rgba(24, 144, 255, 1)',
          borderWidth: 1,
        },
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          display: false,
        },
        title: {
          display: true,
          text: '响应时间分布 (前20个)',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: '时间 (ms)'
          }
        },
        x: {
          title: {
            display: true,
            text: '测试用例'
          }
        }
      },
    };

    return <Bar data={data} options={options} />;
  };

  const columns = [
    {
      title: '测试用例',
      dataIndex: 'test_case_name',
      key: 'test_case_name',
      width: 200,
      ellipsis: {
        showTitle: false,
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: 'API',
      key: 'api',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tag color="blue">{record.api_method}</Tag>
          <span>{record.api_name}</span>
        </Space>
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
      title: '状态码',
      dataIndex: 'response_code',
      key: 'response_code',
      width: 100,
      render: (code) => code || '-',
    },
    {
      title: '响应时间',
      dataIndex: 'response_time',
      key: 'response_time',
      width: 120,
      render: (time) => time ? `${time.toFixed(2)}ms` : '-',
      sorter: (a, b) => (a.response_time || 0) - (b.response_time || 0),
    },
    {
      title: '执行时间',
      dataIndex: 'executed_at',
      key: 'executed_at',
      width: 150,
      render: (time) => new Date(time).toLocaleTimeString(),
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
          onClick={() => handleViewDetails(record)}
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
        minHeight: '400px' 
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
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
              onClick={handleExportHTML}
              loading={exportLoading}
            >
              导出HTML
            </Button>
          </Space>
        </div>

        {/* Summary Cards */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总用例数"
                value={testRun.total_tests}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="通过"
                value={testRun.passed_tests}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="失败"
                value={testRun.failed_tests}
                prefix={<CloseCircleOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="成功率"
                value={testRun.success_rate}
                precision={1}
                suffix="%"
                prefix={<PieChartOutlined />}
                valueStyle={{ 
                  color: testRun.success_rate >= 90 ? '#52c41a' : 
                         testRun.success_rate >= 70 ? '#faad14' : '#ff4d4f' 
                }}
              />
              <Progress
                percent={testRun.success_rate}
                showInfo={false}
                strokeColor={{
                  '0%': testRun.success_rate >= 90 ? '#52c41a' : 
                        testRun.success_rate >= 70 ? '#faad14' : '#ff4d4f',
                  '100%': testRun.success_rate >= 90 ? '#52c41a' : 
                          testRun.success_rate >= 70 ? '#faad14' : '#ff4d4f',
                }}
                size="small"
                style={{ marginTop: '8px' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Charts */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} md={12}>
            <Card title="测试结果分布" loading={loading}>
              <div style={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                {renderPieChart()}
              </div>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="响应时间分析" loading={loading}>
              <div style={{ height: '300px' }}>
                {renderResponseTimeChart()}
              </div>
            </Card>
          </Col>
        </Row>

        {/* Test Details */}
        <Card title="详细结果" style={{ marginBottom: '24px' }}>
          <Table
            columns={columns}
            dataSource={testRun.results}
            rowKey="id"
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            }}
            scroll={{ x: 1000 }}
            size="middle"
          />
        </Card>

        {/* Additional Info */}
        <Collapse style={{ marginBottom: '24px' }}>
          <Panel header="测试信息" key="1">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <p><strong>测试计划:</strong> {testRun.test_plan_detail?.name || '无'}</p>
                <p><strong>执行者:</strong> {testRun.executed_by_username || '系统'}</p>
                <p><strong>开始时间:</strong> {new Date(testRun.start_time).toLocaleString()}</p>
              </Col>
              <Col span={12}>
                <p><strong>结束时间:</strong> {testRun.end_time ? new Date(testRun.end_time).toLocaleString() : '未完成'}</p>
                <p><strong>执行时长:</strong> {testRun.duration_display}</p>
                <p><strong>平均响应时间:</strong> {testRun.avg_response_time ? `${testRun.avg_response_time}ms` : '无'}</p>
              </Col>
            </Row>
            {testRun.description && (
              <>
                <Divider />
                <p><strong>描述:</strong></p>
                <div style={{ padding: '12px', background: '#f5f5f5', borderRadius: '6px' }}>
                  {testRun.description}
                </div>
              </>
            )}
          </Panel>
        </Collapse>
      </div>

      {/* 评论讨论区 */}
      <div style={{ marginTop: '24px' }}>
        <CommentSection
          targetType="testreport"
          targetId={parseInt(runId)}
          currentUser={JSON.parse(localStorage.getItem('user') || 'null')}
        />
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
            <h3>{selectedResult.test_case_name}</h3>
            <Divider />
            
            <Row gutter={[16, 16]}>
              <Col span={8}><strong>状态:</strong></Col>
              <Col span={16}>
                <Tag color={getStatusColor(selectedResult.status)} icon={getStatusIcon(selectedResult.status)}>
                  {selectedResult.status === 'passed' ? '通过' : 
                   selectedResult.status === 'failed' ? '失败' : '错误'}
                </Tag>
              </Col>

              <Col span={8}><strong>API:</strong></Col>
              <Col span={16}>
                <Tag color="blue">{selectedResult.api_method}</Tag>
                {selectedResult.api_name}
              </Col>

              <Col span={8}><strong>URL:</strong></Col>
              <Col span={16}>
                <code style={{ background: '#f5f5f5', padding: '2px 6px', borderRadius: '3px' }}>
                  {selectedResult.api_url}
                </code>
              </Col>

              <Col span={8}><strong>状态码:</strong></Col>
              <Col span={16}>{selectedResult.response_code || '-'}</Col>

              <Col span={8}><strong>响应时间:</strong></Col>
              <Col span={16}>
                {selectedResult.response_time ? `${selectedResult.response_time.toFixed(2)}ms` : '-'}
              </Col>

              <Col span={8}><strong>执行时间:</strong></Col>
              <Col span={16}>{new Date(selectedResult.executed_at).toLocaleString()}</Col>
            </Row>

            {selectedResult.error_message && (
              <>
                <Divider />
                <h4>错误信息</h4>
                <Alert
                  message={selectedResult.error_message}
                  type="error"
                  style={{ marginBottom: '16px' }}
                />
              </>
            )}

            {selectedResult.response_body && (
              <>
                <Divider />
                <h4>响应内容</h4>
                <div style={{ 
                  background: '#f5f5f5', 
                  padding: '12px', 
                  borderRadius: '6px',
                  maxHeight: '300px',
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '12px',
                  lineHeight: '1.4'
                }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(JSON.parse(selectedResult.response_body || '{}'), null, 2)}
                  </pre>
                </div>
              </>
            )}
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default TestReportPage;