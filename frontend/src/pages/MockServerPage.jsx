import { useState, useEffect } from 'react';
import {
  Typography, Table, Form, Input, Select, Button, Modal, Space, Tag, 
  message, Card, Tabs, Row, Col, Statistic, Progress, Tooltip, Badge,
  Popconfirm, Switch, InputNumber, Alert, Divider, Descriptions
} from 'antd';
import {
  PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined,
  EyeOutlined, CopyOutlined, ReloadOutlined, ApiOutlined,
  CodeOutlined, BarChartOutlined, HistoryOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import Logger from '../utils/logger';
import api from '../utils/api';
import './MockServerPage.css';
import BackButton from '../components/BackButton';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;

const MockServerPage = () => {
  const navigate = useNavigate();
  const [mocks, setMocks] = useState([]);
  const [logs, setLogs] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [testModalVisible, setTestModalVisible] = useState(false);
  const [editingMock, setEditingMock] = useState(null);
  const [selectedMock, setSelectedMock] = useState(null);
  const [activeTab, setActiveTab] = useState('mocks');
  const [form] = Form.useForm();

  const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'];
  const statusCodes = [
    { value: 200, label: '200 OK' },
    { value: 201, label: '201 Created' },
    { value: 400, label: '400 Bad Request' },
    { value: 401, label: '401 Unauthorized' },
    { value: 403, label: '403 Forbidden' },
    { value: 404, label: '404 Not Found' },
    { value: 500, label: '500 Internal Server Error' },
    { value: 502, label: '502 Bad Gateway' },
    { value: 503, label: '503 Service Unavailable' },
  ];

  useEffect(() => {
    fetchMocks();
    fetchStatistics();
    if (activeTab === 'logs') {
      fetchLogs();
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'logs') {
      fetchLogs();
    }
  }, [activeTab]);

  const fetchMocks = async () => {
    try {
      Logger.info('Fetching mock APIs...');
      const response = await api.get('/api/mock-server/mocks/');
      Logger.debug('Mock APIs response:', response.data);
      setMocks(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      Logger.errorWithContext('fetchMocks', error);
      message.error('获取Mock API列表失败');
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    try {
      Logger.info('Fetching mock API logs...');
      const response = await api.get('/api/mock-server/logs/recent/?limit=50');
      setLogs(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      Logger.errorWithContext('fetchLogs', error);
      message.error('获取使用日志失败');
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await api.get('/api/mock-server/mocks/statistics/');
      setStatistics(response.data);
    } catch (error) {
      Logger.errorWithContext('fetchStatistics', error);
    }
  };

  const handleAdd = () => {
    Logger.info('Opening add mock API modal');
    setEditingMock(null);
    form.resetFields();
    form.setFieldsValue({
      method: 'GET',
      response_status_code: 200,
      is_active: true,
      delay_ms: 0,
      response_headers: {}
    });
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    Logger.info('Opening edit mock API modal', { id: record.id });
    setEditingMock(record);
    form.setFieldsValue({
      ...record,
      response_headers: JSON.stringify(record.response_headers || {}, null, 2)
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    try {
      Logger.info('Deleting mock API', { id });
      await api.delete(`/api/mock-server/mocks/${id}/`);
      fetchMocks();
      fetchStatistics();
      message.success('Mock API删除成功');
    } catch (error) {
      Logger.errorWithContext('handleDelete', error);
      message.error('删除Mock API失败');
    }
  };

  const handleTest = async (mock) => {
    try {
      const response = await api.post(`/api/mock-server/mocks/${mock.id}/test/`);
      setSelectedMock({
        ...mock,
        testInfo: response.data
      });
      setTestModalVisible(true);
    } catch (error) {
      Logger.errorWithContext('handleTest', error);
      message.error('生成测试信息失败');
    }
  };

  const handleCopyUrl = (mock) => {
    const url = `${window.location.origin}/mock${mock.path}`;
    navigator.clipboard.writeText(url).then(() => {
      message.success('Mock URL已复制到剪贴板');
    }).catch(() => {
      message.error('复制失败');
    });
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      Logger.formData('MockAPIForm', values);

      // 处理响应头
      if (values.response_headers) {
        try {
          values.response_headers = JSON.parse(values.response_headers);
        } catch (e) {
          message.error('响应头格式不正确，请输入有效的JSON');
          return;
        }
      }

      if (editingMock) {
        Logger.info('Updating mock API', { id: editingMock.id });
        await api.put(`/api/mock-server/mocks/${editingMock.id}/`, values);
        message.success('Mock API更新成功');
      } else {
        Logger.info('Creating new mock API');
        await api.post('/api/mock-server/mocks/', values);
        message.success('Mock API创建成功');
      }
      setModalVisible(false);
      fetchMocks();
      fetchStatistics();
    } catch (error) {
      Logger.errorWithContext('handleModalOk', error);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        message.error(errorMessages.join(', '));
      } else {
        message.error('保存Mock API失败');
      }
    }
  };

  const getStatusColor = (statusCode) => {
    if (statusCode >= 200 && statusCode < 300) return 'success';
    if (statusCode >= 300 && statusCode < 400) return 'warning';
    if (statusCode >= 400 && statusCode < 500) return 'error';
    if (statusCode >= 500) return 'error';
    return 'default';
  };

  const getMethodColor = (method) => {
    const colors = {
      GET: 'blue', POST: 'green', PUT: 'orange', 
      DELETE: 'red', PATCH: 'purple', HEAD: 'cyan', OPTIONS: 'magenta'
    };
    return colors[method] || 'default';
  };

  const columns = [
    {
      title: 'Mock名称',
      dataIndex: 'name',
      key: 'name',
      width: 200,
      ellipsis: { showTitle: false },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          {text}
        </Tooltip>
      ),
    },
    {
      title: 'URL路径',
      key: 'url',
      width: 250,
      render: (_, record) => (
        <Space>
          <Tag color={getMethodColor(record.method)}>{record.method}</Tag>
          <code style={{ fontSize: '12px' }}>{record.path}</code>
        </Space>
      ),
    },
    {
      title: '状态码',
      dataIndex: 'response_status_code',
      key: 'response_status_code',
      width: 100,
      render: (code) => (
        <Tag color={getStatusColor(code)}>{code}</Tag>
      ),
    },
    {
      title: '状态',
      key: 'status',
      width: 80,
      render: (_, record) => (
        <Badge
          status={record.is_active ? 'success' : 'default'}
          text={record.is_active ? '启用' : '禁用'}
        />
      ),
    },
    {
      title: '延迟',
      dataIndex: 'delay_ms',
      key: 'delay_ms',
      width: 80,
      render: (delay) => delay > 0 ? `${delay}ms` : '-',
    },
    {
      title: '创建者',
      dataIndex: 'created_by_username',
      key: 'created_by_username',
      width: 100,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="测试">
            <Button
              type="link"
              icon={<PlayCircleOutlined />}
              onClick={() => handleTest(record)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="复制URL">
            <Button
              type="link"
              icon={<CopyOutlined />}
              onClick={() => handleCopyUrl(record)}
              size="small"
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
              size="small"
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这个Mock API吗？"
            onConfirm={() => handleDelete(record.id)}
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

  const logColumns = [
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 150,
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: '请求',
      key: 'request',
      width: 200,
      render: (_, record) => (
        <Space>
          <Tag color={getMethodColor(record.request_method)}>
            {record.request_method}
          </Tag>
          <code style={{ fontSize: '12px' }}>{record.request_path}</code>
        </Space>
      ),
    },
    {
      title: '状态码',
      dataIndex: 'response_status_code',
      key: 'response_status_code',
      width: 100,
      render: (code) => (
        <Tag color={getStatusColor(code)}>{code}</Tag>
      ),
    },
    {
      title: '客户端IP',
      dataIndex: 'client_ip',
      key: 'client_ip',
      width: 120,
    },
    {
      title: 'Mock API',
      dataIndex: 'mock_api_name',
      key: 'mock_api_name',
      width: 150,
      ellipsis: { showTitle: false },
      render: (text) => text || '-',
    },
  ];

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <BackButton />
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={2}>Mock Server</Title>
          <Space>
            <Button
              icon={<ReloadOutlined />}
              onClick={() => {
                fetchMocks();
                fetchStatistics();
                if (activeTab === 'logs') fetchLogs();
              }}
              loading={loading}
            >
              刷新
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAdd}
            >
              创建Mock API
            </Button>
          </Space>
        </div>

        {/* 统计卡片 */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总Mock数"
                value={statistics.total_mocks || 0}
                prefix={<ApiOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="活跃Mock"
                value={statistics.active_mocks || 0}
                prefix={<Badge status="success" />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总请求数"
                value={statistics.total_requests || 0}
                prefix={<BarChartOutlined />}
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="今日请求"
                value={statistics.requests_today || 0}
                prefix={<HistoryOutlined />}
                valueStyle={{ color: '#fa8c16' }}
              />
            </Card>
          </Col>
        </Row>

        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab="Mock APIs" key="mocks">
            <Table
              columns={columns}
              dataSource={mocks}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 20, showSizeChanger: true }}
              scroll={{ x: 1200 }}
            />
          </TabPane>

          <TabPane tab="使用日志" key="logs">
            <Table
              columns={logColumns}
              dataSource={logs}
              rowKey="id"
              pagination={{ pageSize: 20 }}
              scroll={{ x: 800 }}
            />
          </TabPane>
        </Tabs>

        {/* 创建/编辑Modal */}
        <Modal
          title={editingMock ? '编辑Mock API' : '创建Mock API'}
          open={modalVisible}
          onOk={handleModalOk}
          onCancel={() => setModalVisible(false)}
          width={800}
          destroyOnClose
        >
          <Form
            form={form}
            layout="vertical"
          >
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="Mock名称"
                  rules={[{ required: true, message: '请输入Mock名称' }]}
                >
                  <Input placeholder="例如: 用户信息接口" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="method"
                  label="HTTP方法"
                  rules={[{ required: true, message: '请选择HTTP方法' }]}
                >
                  <Select>
                    {httpMethods.map(method => (
                      <Option key={method} value={method}>{method}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              name="path"
              label="URL路径"
              rules={[{ required: true, message: '请输入URL路径' }]}
            >
              <Input 
                placeholder="例如: /api/user/profile"
                addonBefore="/mock"
              />
            </Form.Item>

            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="response_status_code"
                  label="响应状态码"
                  rules={[{ required: true, message: '请选择状态码' }]}
                >
                  <Select>
                    {statusCodes.map(({ value, label }) => (
                      <Option key={value} value={value}>{label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  name="delay_ms"
                  label="响应延迟(ms)"
                >
                  <InputNumber min={0} max={30000} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={6}>
                <Form.Item
                  name="is_active"
                  label="是否启用"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Col>
            </Row>

            <Form.Item
              name="response_headers"
              label="响应头 (JSON格式)"
            >
              <TextArea
                rows={3}
                placeholder='{"Content-Type": "application/json"}'
              />
            </Form.Item>

            <Form.Item
              name="response_body"
              label="响应体"
            >
              <TextArea
                rows={6}
                placeholder='{"username": "MockUser", "email": "mock@test.com"}'
              />
            </Form.Item>

            <Form.Item
              name="description"
              label="描述"
            >
              <TextArea rows={2} placeholder="Mock API的用途说明" />
            </Form.Item>
          </Form>
        </Modal>

        {/* 测试Modal */}
        <Modal
          title="测试Mock API"
          open={testModalVisible}
          onCancel={() => setTestModalVisible(false)}
          footer={null}
          width={800}
        >
          {selectedMock && (
            <div>
              <Alert
                message="测试信息"
                description={`测试URL: ${selectedMock.testInfo?.test_url || selectedMock.full_url}`}
                type="info"
                style={{ marginBottom: '16px' }}
              />
              
              <Descriptions title="Mock API详情" bordered size="small">
                <Descriptions.Item label="名称">{selectedMock.name}</Descriptions.Item>
                <Descriptions.Item label="方法">
                  <Tag color={getMethodColor(selectedMock.method)}>{selectedMock.method}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="路径">
                  <code>{selectedMock.path}</code>
                </Descriptions.Item>
                <Descriptions.Item label="状态码">
                  <Tag color={getStatusColor(selectedMock.response_status_code)}>
                    {selectedMock.response_status_code}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="延迟">
                  {selectedMock.delay_ms > 0 ? `${selectedMock.delay_ms}ms` : '无'}
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Badge
                    status={selectedMock.is_active ? 'success' : 'default'}
                    text={selectedMock.is_active ? '启用' : '禁用'}
                  />
                </Descriptions.Item>
              </Descriptions>

              {selectedMock.testInfo?.curl_command && (
                <div style={{ marginTop: '16px' }}>
                  <Title level={5}>cURL命令:</Title>
                  <Input.TextArea
                    value={selectedMock.testInfo.curl_command}
                    rows={3}
                    readOnly
                    style={{ fontFamily: 'monospace', fontSize: '12px' }}
                  />
                </div>
              )}

              {selectedMock.response_body && (
                <div style={{ marginTop: '16px' }}>
                  <Title level={5}>响应体预览:</Title>
                  <Input.TextArea
                    value={selectedMock.response_body}
                    rows={6}
                    readOnly
                    style={{ fontFamily: 'monospace', fontSize: '12px' }}
                  />
                </div>
              )}
            </div>
          )}
        </Modal>
      </div>
    </div>
  );
};

export default MockServerPage;