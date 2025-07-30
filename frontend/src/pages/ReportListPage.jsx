import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography, Table, Button, Tag, Space, Card, Row, Col,
  Statistic, Input, Select, DatePicker, message, Tooltip,
  Popconfirm, Modal, Form, Progress
} from 'antd';
import {
  EyeOutlined, DownloadOutlined, DeleteOutlined, 
  PlayCircleOutlined, ReloadOutlined, SearchOutlined,
  BarChartOutlined, CheckCircleOutlined, CloseCircleOutlined,
  ExclamationCircleOutlined, ClockCircleOutlined, PlusOutlined
} from '@ant-design/icons';
import api from '../utils/api';
import Logger from '../utils/logger';
import BackButton from '../components/BackButton';

const { Title } = Typography;
const { Search } = Input;
const { Option } = Select;
const { RangePicker } = DatePicker;

const ReportListPage = () => {
  const navigate = useNavigate();
  
  const [reports, setReports] = useState([]);
  const [testPlans, setTestPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [executeLoading, setExecuteLoading] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    test_plan: '',
    search: '',
    date_range: null
  });
  const [executeModalVisible, setExecuteModalVisible] = useState(false);
  const [executeForm] = Form.useForm();
  
  // 统计数据
  const [summary, setSummary] = useState({
    total: 0,
    completed: 0,
    running: 0,
    failed: 0,
    avg_success_rate: 0
  });

  useEffect(() => {
    fetchReports();
    fetchTestPlans();
  }, []);

  useEffect(() => {
    fetchReports();
  }, [filters]);

  const fetchReports = async () => {
    try {
      setLoading(true);
      Logger.info('Fetching test reports');
      
      // 构建查询参数
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.test_plan) params.test_plan = filters.test_plan;
      if (filters.search) params.search = filters.search;
      
      const response = await api.get('/api/reports/test-runs/', { params });
      const reportData = response.data;
      setReports(Array.isArray(reportData) ? reportData : []);
      
      // 计算统计数据
      calculateSummary(reportData);
      
      Logger.debug('Reports data:', reportData);
    } catch (error) {
      Logger.errorWithContext('fetchReports', error);
      message.error('获取测试报告列表失败');
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchTestPlans = async () => {
    try {
      const response = await api.get('/testcases/testplans/');
      setTestPlans(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      Logger.errorWithContext('fetchTestPlans', error);
    }
  };

  const calculateSummary = (reportData) => {
    if (!Array.isArray(reportData) || reportData.length === 0) {
      setSummary({
        total: 0,
        completed: 0,
        running: 0,
        failed: 0,
        avg_success_rate: 0
      });
      return;
    }

    const summary = {
      total: reportData.length,
      completed: reportData.filter(r => r.status === 'completed').length,
      running: reportData.filter(r => r.status === 'running').length,
      failed: reportData.filter(r => r.status === 'failed').length,
      avg_success_rate: 0
    };

    // 计算平均成功率
    const completedReports = reportData.filter(r => r.status === 'completed');
    if (completedReports.length > 0) {
      const totalSuccessRate = completedReports.reduce((sum, r) => sum + (r.success_rate || 0), 0);
      summary.avg_success_rate = totalSuccessRate / completedReports.length;
    }

    setSummary(summary);
  };

  const handleViewReport = (record) => {
    navigate(`/reports/${record.id}`);
  };

  const handleExecuteTestPlan = async (values) => {
    try {
      setExecuteLoading(true);
      Logger.info('Executing test plan', values);
      
      const response = await api.post('/api-test/api-test-cases/execute_test_plan/', {
        test_plan_id: values.test_plan_id,
        run_name: values.run_name
      });
      
      message.success('测试计划执行已启动');
      setExecuteModalVisible(false);
      executeForm.resetFields();
      
      // 跳转到报告详情页
      if (response.data.id) {
        navigate(`/reports/${response.data.id}`);
      } else {
        // 刷新列表
        fetchReports();
      }
    } catch (error) {
      Logger.errorWithContext('handleExecuteTestPlan', error);
      message.error('执行测试计划失败');
    } finally {
      setExecuteLoading(false);
    }
  };

  const handleDeleteReport = async (id) => {
    try {
      Logger.info('Deleting test report', { id });
      await api.delete(`/api/reports/test-runs/${id}/`);
      message.success('删除成功');
      fetchReports();
    } catch (error) {
      Logger.errorWithContext('handleDeleteReport', error);
      message.error('删除失败');
    }
  };

  const handleExportReport = async (id) => {
    try {
      Logger.info('Exporting report', { id });
      
      const response = await api.get(`/api/reports/test-runs/${id}/export_html/`, {
        responseType: 'blob'
      });
      
      // 创建下载链接
      const blob = new Blob([response.data], { type: 'text/html' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `test_report_${id}_${new Date().getTime()}.html`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success('报告导出成功');
    } catch (error) {
      Logger.errorWithContext('handleExportReport', error);
      message.error('导出失败');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'running': return 'processing';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return '已完成';
      case 'failed': return '失败';
      case 'running': return '运行中';
      default: return '未知';
    }
  };

  const columns = [
    {
      title: '报告名称',
      dataIndex: 'name',
      key: 'name',
      width: 250,
      ellipsis: {
        showTitle: false,
      },
      render: (text, record) => (
        <Tooltip placement="topLeft" title={text}>
          <Button
            type="link"
            onClick={() => handleViewReport(record)}
            style={{ padding: 0, height: 'auto', textAlign: 'left' }}
          >
            {text}
          </Button>
        </Tooltip>
      ),
    },
    {
      title: '测试计划',
      dataIndex: 'test_plan_name',
      key: 'test_plan_name',
      width: 150,
      render: (text) => text || '-',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '测试结果',
      key: 'test_results',
      width: 200,
      render: (_, record) => (
        <Space direction="vertical" size="small" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>总计: {record.total_tests}</span>
            <span>{record.success_rate?.toFixed(1) || 0}%</span>
          </div>
          <Progress
            percent={record.success_rate || 0}
            size="small"
            strokeColor={{
              '0%': record.success_rate >= 90 ? '#52c41a' : 
                    record.success_rate >= 70 ? '#faad14' : '#ff4d4f',
              '100%': record.success_rate >= 90 ? '#52c41a' : 
                      record.success_rate >= 70 ? '#faad14' : '#ff4d4f',
            }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#666' }}>
            <span>✓ {record.passed_tests}</span>
            <span>✗ {record.failed_tests}</span>
            <span>! {record.error_tests}</span>
          </div>
        </Space>
      ),
    },
    {
      title: '执行时长',
      dataIndex: 'duration_display',
      key: 'duration_display',
      width: 100,
    },
    {
      title: '执行者',
      dataIndex: 'executed_by_username',
      key: 'executed_by_username',
      width: 100,
      render: (text) => text || '系统',
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 150,
      render: (time) => new Date(time).toLocaleString(),
      sorter: (a, b) => new Date(a.start_time) - new Date(b.start_time),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button
              type="link"
              icon={<EyeOutlined />}
              onClick={() => handleViewReport(record)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="导出HTML">
            <Button
              type="link"
              icon={<DownloadOutlined />}
              onClick={() => handleExportReport(record.id)}
              size="small"
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个报告吗？"
            onConfirm={() => handleDeleteReport(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button
                type="link"
                icon={<DeleteOutlined />}
                danger
                size="small"
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <BackButton />
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2} style={{ margin: 0 }}>
            测试报告
          </Title>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchReports}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setExecuteModalVisible(true)}
            >
              执行测试
            </Button>
          </Space>
        </div>

        {/* Summary Cards */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总报告数"
                value={summary.total}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="已完成"
                value={summary.completed}
                prefix={<CheckCircleOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="运行中"
                value={summary.running}
                prefix={<ClockCircleOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="平均成功率"
                value={summary.avg_success_rate}
                precision={1}
                suffix="%"
                prefix={<ExclamationCircleOutlined />}
                valueStyle={{ 
                  color: summary.avg_success_rate >= 90 ? '#52c41a' : 
                         summary.avg_success_rate >= 70 ? '#faad14' : '#ff4d4f' 
                }}
              />
            </Card>
          </Col>
        </Row>

        {/* Filters */}
        <Card style={{ marginBottom: '24px' }}>
          <Row gutter={[16, 16]} align="middle">
            <Col xs={24} sm={12} md={6}>
              <Search
                placeholder="搜索报告名称"
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                onSearch={() => fetchReports()}
                allowClear
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Select
                placeholder="选择状态"
                value={filters.status}
                onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
                allowClear
                style={{ width: '100%' }}
              >
                <Option value="completed">已完成</Option>
                <Option value="running">运行中</Option>
                <Option value="failed">失败</Option>
              </Select>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Select
                placeholder="选择测试计划"
                value={filters.test_plan}
                onChange={(value) => setFilters(prev => ({ ...prev, test_plan: value }))}
                allowClear
                style={{ width: '100%' }}
              >
                {testPlans.map(plan => (
                  <Option key={plan.id} value={plan.id}>
                    {plan.name}
                  </Option>
                ))}
              </Select>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Button
                icon={<SearchOutlined />}
                onClick={fetchReports}
                loading={loading}
                style={{ width: '100%' }}
              >
                搜索
              </Button>
            </Col>
          </Row>
        </Card>

        {/* Reports Table */}
        <Card>
          <Table
            columns={columns}
            dataSource={reports}
            rowKey="id"
            loading={loading}
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            }}
            scroll={{ x: 1200 }}
          />
        </Card>

        {/* Execute Test Plan Modal */}
        <Modal
          title="执行测试计划"
          open={executeModalVisible}
          onCancel={() => {
            setExecuteModalVisible(false);
            executeForm.resetFields();
          }}
          footer={null}
          width={500}
        >
          <Form
            form={executeForm}
            layout="vertical"
            onFinish={handleExecuteTestPlan}
          >
            <Form.Item
              name="test_plan_id"
              label="选择测试计划"
              rules={[{ required: true, message: '请选择测试计划' }]}
            >
              <Select placeholder="请选择测试计划">
                {testPlans.map(plan => (
                  <Option key={plan.id} value={plan.id}>
                    {plan.name}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="run_name"
              label="执行名称"
              rules={[{ required: true, message: '请输入执行名称' }]}
            >
              <Input 
                placeholder={`测试执行 - ${new Date().toLocaleString()}`}
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
              <Space>
                <Button 
                  onClick={() => {
                    setExecuteModalVisible(false);
                    executeForm.resetFields();
                  }}
                >
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={executeLoading}
                  icon={<PlayCircleOutlined />}
                >
                  开始执行
                </Button>
              </Space>
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  );
};

export default ReportListPage;