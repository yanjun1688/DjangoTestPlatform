import { useState, useEffect } from 'react';
import {
  Typography, Table, Form, Input, Select, Button, Modal, Space, Tag, 
  message, Card, Tabs, List, Statistic, Row, Col, Progress, Tooltip
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined,
  EyeOutlined, HistoryOutlined, BarChartOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import Logger from '../utils/logger';
import api from '../utils/api';
import BackButton from '../components/BackButton';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

const TestPlanPage = () => {
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);
  const [executeModalVisible, setExecuteModalVisible] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [historicalReports, setHistoricalReports] = useState([]);
  const [reportsLoading, setReportsLoading] = useState(false);
  const [form] = Form.useForm();
  const [executeForm] = Form.useForm();

  useEffect(() => {
    fetchPlans();
    fetchTestCases();
  }, []);

  const fetchPlans = async () => {
    try {
      Logger.info('Fetching test plans...');
      const response = await api.get('/testcases/testplans/');
      Logger.debug('Test plans response:', response.data);
      setPlans(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      Logger.errorWithContext('fetchPlans', error);
      setLoading(false);
    }
  };

  const fetchTestCases = async () => {
    try {
      Logger.info('Fetching test cases...');
      const response = await api.get('/testcases/testcases/');
      setTestCases(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      Logger.errorWithContext('fetchTestCases', error);
    }
  };

  const fetchHistoricalReports = async (planId) => {
    try {
      setReportsLoading(true);
      Logger.info('Fetching historical reports', { planId });
      const response = await api.get(`/api/reports/test-runs/?test_plan=${planId}`);
      setHistoricalReports(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      Logger.errorWithContext('fetchHistoricalReports', error);
      message.error('获取历史报告失败');
    } finally {
      setReportsLoading(false);
    }
  };

  const handleAdd = () => {
    Logger.info('Opening add test plan modal');
    setEditingPlan(null);
    form.resetFields();
    form.setFieldsValue({
      status: 'pending'
    });
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    Logger.info('Opening edit test plan modal', { id: record.id });
    setEditingPlan(record);
    form.setFieldsValue({
      ...record,
      test_cases: record.test_cases || []
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('确定要删除这个测试计划吗？')) {
      try {
        Logger.info('Deleting test plan', { id });
        await api.delete(`/testcases/testplans/${id}/`);
        fetchPlans();
        message.success('测试计划删除成功');
      } catch (error) {
        Logger.errorWithContext('handleDelete', error);
        message.error('删除测试计划失败');
      }
    }
  };

  const handleExecute = (plan) => {
    setSelectedPlan(plan);
    executeForm.setFieldsValue({
      test_plan_id: plan.id,
      run_name: `${plan.name} - ${new Date().toLocaleString()}`
    });
    setExecuteModalVisible(true);
  };

  const handleExecuteSubmit = async (values) => {
    try {
      Logger.info('Executing test plan', values);
      const response = await api.post('/api-test/api-test-cases/execute_test_plan/', values);
      
      message.success('测试计划执行已启动');
      setExecuteModalVisible(false);
      executeForm.resetFields();
      
      // 跳转到报告详情页
      if (response.data.id) {
        navigate(`/reports/${response.data.id}`);
      }
    } catch (error) {
      Logger.errorWithContext('handleExecuteSubmit', error);
      message.error('执行测试计划失败');
    }
  };

  const handleViewReports = (plan) => {
    setSelectedPlan(plan);
    fetchHistoricalReports(plan.id);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      Logger.formData('TestPlanForm', values);

      if (editingPlan) {
        Logger.info('Updating test plan', { id: editingPlan.id });
        await api.put(`/testcases/testplans/${editingPlan.id}/`, values);
        message.success('测试计划更新成功');
      } else {
        Logger.info('Creating new test plan');
        await api.post('/testcases/testplans/', values);
        message.success('测试计划创建成功');
      }
      setModalVisible(false);
      fetchPlans();
    } catch (error) {
      Logger.errorWithContext('handleModalOk', error);
      message.error('保存测试计划失败');
    }
  };

  const handleModalCancel = () => {
    setModalVisible(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'processing';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'completed': return '已完成';
      case 'running': return '进行中';
      case 'pending': return '待执行';
      default: return '未知';
    }
  };

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '测试用例数',
      key: 'test_case_count',
      render: (_, record) => record.test_cases?.length || 0,
    },
    {
      title: '负责人',
      dataIndex: 'assignee',
      key: 'assignee',
      render: (assignee) => assignee?.username || '-',
    },
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      render: (time) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'actions',
      render: (text, record) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            icon={<PlayCircleOutlined />}
            onClick={() => handleExecute(record)}
          >
            执行
          </Button>
          <Button 
            type="link" 
            icon={<HistoryOutlined />}
            onClick={() => handleViewReports(record)}
          >
            历史报告
          </Button>
          <Button 
            type="link" 
            danger 
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  const reportColumns = [
    {
      title: '报告名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Button
          type="link"
          onClick={() => navigate(`/reports/${record.id}`)}
          style={{ padding: 0, height: 'auto' }}
        >
          {text}
        </Button>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {getStatusText(status)}
        </Tag>
      ),
    },
    {
      title: '成功率',
      key: 'success_rate',
      render: (_, record) => (
        <div style={{ width: '120px' }}>
          <Progress
            percent={record.success_rate || 0}
            size="small"
            format={(percent) => `${percent?.toFixed(1) || 0}%`}
            strokeColor={{
              '0%': record.success_rate >= 90 ? '#52c41a' : 
                    record.success_rate >= 70 ? '#faad14' : '#ff4d4f',
              '100%': record.success_rate >= 90 ? '#52c41a' : 
                      record.success_rate >= 70 ? '#faad14' : '#ff4d4f',
            }}
          />
        </div>
      ),
    },
    {
      title: '测试结果',
      key: 'test_results',
      render: (_, record) => (
        <Space>
          <Tooltip title="通过">
            <span style={{ color: '#52c41a' }}>✓ {record.passed_tests}</span>
          </Tooltip>
          <Tooltip title="失败">
            <span style={{ color: '#ff4d4f' }}>✗ {record.failed_tests}</span>
          </Tooltip>
          <Tooltip title="错误">
            <span style={{ color: '#faad14' }}>! {record.error_tests}</span>
          </Tooltip>
        </Space>
      ),
    },
    {
      title: '执行时长',
      dataIndex: 'duration_display',
      key: 'duration_display',
    },
    {
      title: '执行时间',
      dataIndex: 'start_time',
      key: 'start_time',
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/reports/${record.id}`)}
          >
            查看详情
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <BackButton />
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>测试计划</Title>
        <Button 
          type="primary" 
          onClick={handleAdd} 
          style={{ marginBottom: '20px' }}
          icon={<PlusOutlined />}
        >
          添加新测试计划
        </Button>
        
        <Tabs defaultActiveKey="plans">
          <TabPane tab="测试计划" key="plans">
            <Table 
              columns={columns} 
              dataSource={plans} 
              rowKey="id" 
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
          
          {selectedPlan && (
            <TabPane tab={`${selectedPlan.name} - 历史报告`} key="reports">
              <Card title={`${selectedPlan.name} 的历史执行报告`} style={{ marginBottom: '20px' }}>
                {historicalReports.length > 0 && (
                  <Row gutter={[16, 16]} style={{ marginBottom: '20px' }}>
                    <Col span={6}>
                      <Statistic
                        title="总执行次数"
                        value={historicalReports.length}
                        prefix={<BarChartOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="成功执行"
                        value={historicalReports.filter(r => r.status === 'completed').length}
                        valueStyle={{ color: '#52c41a' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="失败执行"
                        value={historicalReports.filter(r => r.status === 'failed').length}
                        valueStyle={{ color: '#ff4d4f' }}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="平均成功率"
                        value={
                          historicalReports.length > 0
                            ? historicalReports
                                .filter(r => r.status === 'completed')
                                .reduce((sum, r) => sum + (r.success_rate || 0), 0) /
                              historicalReports.filter(r => r.status === 'completed').length
                            : 0
                        }
                        precision={1}
                        suffix="%"
                        valueStyle={{ 
                          color: historicalReports.length > 0 && 
                                 historicalReports.reduce((sum, r) => sum + (r.success_rate || 0), 0) / historicalReports.length >= 90 
                                 ? '#52c41a' : '#faad14' 
                        }}
                      />
                    </Col>
                  </Row>
                )}
                
                <Table
                  columns={reportColumns}
                  dataSource={historicalReports}
                  rowKey="id"
                  loading={reportsLoading}
                  pagination={{ pageSize: 10 }}
                  locale={{ emptyText: '暂无执行报告' }}
                />
              </Card>
            </TabPane>
          )}
        </Tabs>

        {/* 添加/编辑测试计划模态框 */}
        <Modal
          title={editingPlan ? '编辑测试计划' : '添加新测试计划'}
          open={modalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          width={600}
          destroyOnClose
        >
          <Form
            form={form}
            layout="vertical"
          >
            <Form.Item
              name="name"
              label="名称"
              rules={[{ required: true, message: '请输入测试计划名称' }]}
            >
              <Input />
            </Form.Item>
            
            <Form.Item
              name="test_cases"
              label="测试用例"
              help="选择要包含在此测试计划中的测试用例"
            >
              <Select
                mode="multiple"
                placeholder="选择测试用例"
                style={{ width: '100%' }}
              >
                {testCases.map(testCase => (
                  <Option key={testCase.id} value={testCase.id}>
                    {testCase.title}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="status"
              label="状态"
              rules={[{ required: true, message: '请选择状态' }]}
            >
              <Select>
                <Option value="pending">待执行</Option>
                <Option value="running">进行中</Option>
                <Option value="completed">已完成</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="start_time"
              label="开始时间"
            >
              <Input type="datetime-local" />
            </Form.Item>

            <Form.Item
              name="end_time"
              label="结束时间"
            >
              <Input type="datetime-local" />
            </Form.Item>
          </Form>
        </Modal>

        {/* 执行测试计划模态框 */}
        <Modal
          title="执行测试计划"
          open={executeModalVisible}
          onCancel={() => setExecuteModalVisible(false)}
          footer={null}
          width={500}
        >
          <Form
            form={executeForm}
            layout="vertical"
            onFinish={handleExecuteSubmit}
          >
            <Form.Item
              name="test_plan_id"
              label="测试计划"
            >
              <Input disabled value={selectedPlan?.name} />
            </Form.Item>

            <Form.Item
              name="run_name"
              label="执行名称"
              rules={[{ required: true, message: '请输入执行名称' }]}
            >
              <Input />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
              <Space>
                <Button onClick={() => setExecuteModalVisible(false)}>
                  取消
                </Button>
                <Button
                  type="primary"
                  htmlType="submit"
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

export default TestPlanPage;