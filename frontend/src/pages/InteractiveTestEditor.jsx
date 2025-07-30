import { useState, useEffect, useRef } from 'react';
import { Button, Input, Select, Switch, InputNumber, message, Tree, Tabs, Space, Card, Tag, Spin, Alert, Collapse, Drawer, Form, Modal, Upload } from 'antd';
import { 
  PlayCircleOutlined, 
  SaveOutlined, 
  FolderOpenOutlined, 
  PlusOutlined, 
  DeleteOutlined,
  SettingOutlined,
  GlobalOutlined,
  FileTextOutlined,
  BugOutlined,
  EyeOutlined,
  UploadOutlined,
  DownloadOutlined,
  CopyOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { Allotment } from 'allotment';
import 'allotment/dist/style.css';
import BackButton from '../components/BackButton';
import api from '../utils/api';
import Logger from '../utils/logger';

const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { Panel } = Collapse;

const InteractiveTestEditor = () => {
  // 左侧导航状态
  const [testCases, setTestCases] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [selectedEnvironment, setSelectedEnvironment] = useState(null);
  
  // 编辑器状态
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [apis, setApis] = useState([]);
  
  // 响应面板状态
  const [response, setResponse] = useState(null);
  const [responseLoading, setResponseLoading] = useState(false);
  const [activeResponseTab, setActiveResponseTab] = useState('response');
  
  // 设置抽屉
  const [settingsVisible, setSettingsVisible] = useState(false);
  const [envModalVisible, setEnvModalVisible] = useState(false);
  const [envForm] = Form.useForm();

  // 初始化数据
  useEffect(() => {
    loadTestCases();
    loadEnvironments();
    loadApis();
  }, []);

  const loadTestCases = async () => {
    try {
      const response = await api.get('/api-test/api-test-cases/');
      setTestCases(response.data || []);
    } catch (error) {
      Logger.errorWithContext('loadTestCases', error);
    }
  };

  const loadEnvironments = async () => {
    try {
      const response = await api.get('/api/environments/environments/');
      setEnvironments(response.data || []);
      // 设置默认环境
      const defaultEnv = response.data.find(env => env.is_default);
      if (defaultEnv) {
        setSelectedEnvironment(defaultEnv.id);
      }
    } catch (error) {
      Logger.errorWithContext('loadEnvironments', error);
    }
  };

  const loadApis = async () => {
    try {
      const response = await api.get('/api-test/api-definitions/');
      setApis(response.data || []);
    } catch (error) {
      Logger.errorWithContext('loadApis', error);
    }
  };

  // 选择测试用例
  const handleCaseSelect = async (caseId) => {
    try {
      setLoading(true);
      const response = await api.get(`/api-test/api-test-cases/${caseId}/`);
      setSelectedCase(response.data);
      
      // 填充表单
      form.setFieldsValue({
        name: response.data.name,
        api: response.data.api,
        expected_status_code: response.data.expected_status_code,
        max_response_time: response.data.max_response_time,
        is_active: response.data.is_active,
        headers: JSON.stringify(response.data.headers || {}, null, 2),
        params: JSON.stringify(response.data.params || {}, null, 2),
        body: JSON.stringify(response.data.body || {}, null, 2),
        assertions: JSON.stringify(response.data.assertions || [], null, 2),
        variables: JSON.stringify(response.data.variables || {}, null, 2),
        description: response.data.description
      });
      
      setResponse(null); // 清空响应
      setLoading(false);
    } catch (error) {
      Logger.errorWithContext('handleCaseSelect', error);
      setLoading(false);
    }
  };

  // 执行测试
  const executeTest = async () => {
    if (!selectedCase) {
      message.error('请先选择测试用例');
      return;
    }

    try {
      setExecuting(true);
      setResponseLoading(true);
      setActiveResponseTab('response');
      
      const requestData = {
        environment_id: selectedEnvironment
      };
      
      const response = await api.post(`/api-test/api-test-cases/${selectedCase.id}/execute/`, requestData);
      
      setResponse({
        ...response.data,
        execution_time: new Date().toISOString()
      });
      
      message.success('测试执行完成');
    } catch (error) {
      Logger.errorWithContext('executeTest', error);
      message.error('测试执行失败');
      setResponse({
        status: 'error',
        error_message: error.message || '未知错误',
        execution_time: new Date().toISOString()
      });
    } finally {
      setExecuting(false);
      setResponseLoading(false);
    }
  };

  // 保存测试用例
  const saveTestCase = async () => {
    if (!selectedCase) {
      message.error('请先选择测试用例');
      return;
    }

    try {
      const values = await form.validateFields();
      
      const submitData = {
        ...values,
        headers: JSON.parse(values.headers || '{}'),
        params: JSON.parse(values.params || '{}'),
        body: JSON.parse(values.body || '{}'),
        assertions: JSON.parse(values.assertions || '[]'),
        variables: JSON.parse(values.variables || '{}')
      };
      
      await api.put(`/api-test/api-test-cases/${selectedCase.id}/`, submitData);
      message.success('测试用例保存成功');
      
      // 更新本地状态
      setSelectedCase({ ...selectedCase, ...submitData });
      loadTestCases();
    } catch (error) {
      Logger.errorWithContext('saveTestCase', error);
      message.error('保存失败');
    }
  };

  // 创建新环境
  const createEnvironment = async () => {
    try {
      const values = await envForm.validateFields();
      await api.post('/api/environments/environments/', values);
      message.success('环境创建成功');
      setEnvModalVisible(false);
      loadEnvironments();
      envForm.resetFields();
    } catch (error) {
      Logger.errorWithContext('createEnvironment', error);
      message.error('创建环境失败');
    }
  };

  // 构建测试用例树
  const buildTestCaseTree = () => {
    return testCases.map(testCase => ({
      key: testCase.id,
      title: (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>{testCase.name}</span>
          <Tag color={testCase.is_active ? 'green' : 'red'} size="small">
            {testCase.is_active ? '启用' : '禁用'}
          </Tag>
        </div>
      ),
      isLeaf: true,
      testCase
    }));
  };

  // 格式化响应时间
  const formatResponseTime = (time) => {
    if (!time) return '-';
    return `${time.toFixed(2)}ms`;
  };

  // 获取状态颜色
  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': return 'green';
      case 'failed': return 'red';
      case 'error': return 'orange';
      default: return 'default';
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <BackButton />
      {/* 顶部工具栏 */}
      <div style={{ 
        height: '60px', 
        borderBottom: '1px solid #f0f0f0', 
        display: 'flex', 
        alignItems: 'center', 
        padding: '0 16px',
        background: '#fff'
      }}>
        <Space size="middle">
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />}
            onClick={executeTest}
            loading={executing}
            disabled={!selectedCase}
          >
            执行测试
          </Button>
          <Button 
            icon={<SaveOutlined />}
            onClick={saveTestCase}
            disabled={!selectedCase}
          >
            保存
          </Button>
          <Select
            placeholder="选择环境"
            style={{ width: 150 }}
            value={selectedEnvironment}
            onChange={setSelectedEnvironment}
            dropdownRender={menu => (
              <div>
                {menu}
                <div style={{ padding: '8px 0', borderTop: '1px solid #f0f0f0' }}>
                  <Button 
                    type="text" 
                    icon={<PlusOutlined />}
                    onClick={() => setEnvModalVisible(true)}
                    style={{ width: '100%' }}
                  >
                    新建环境
                  </Button>
                </div>
              </div>
            )}
          >
            {environments.map(env => (
              <Option key={env.id} value={env.id}>
                <GlobalOutlined style={{ marginRight: 8 }} />
                {env.name}
                {env.is_default && <Tag color="blue" size="small" style={{ marginLeft: 8 }}>默认</Tag>}
              </Option>
            ))}
          </Select>
          <Button 
            icon={<SettingOutlined />}
            onClick={() => setSettingsVisible(true)}
          >
            设置
          </Button>
        </Space>
      </div>

      {/* 主要内容区域 */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <Allotment defaultSizes={[15, 50, 35]}>
          {/* 左侧导航面板 (15%) */}
          <Allotment.Pane minSize={200} maxSize={400}>
            <div style={{ height: '100%', background: '#fafafa', borderRight: '1px solid #f0f0f0' }}>
              <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
                <h3 style={{ margin: 0, fontSize: '16px' }}>测试用例</h3>
              </div>
              <div style={{ padding: '8px' }}>
                <Tree
                  treeData={buildTestCaseTree()}
                  selectedKeys={selectedCase ? [selectedCase.id] : []}
                  onSelect={(keys) => {
                    if (keys.length > 0) {
                      handleCaseSelect(keys[0]);
                    }
                  }}
                  showIcon={false}
                />
              </div>
            </div>
          </Allotment.Pane>

          {/* 中间编辑器面板 (50%) */}
          <Allotment.Pane>
            <div style={{ height: '100%', background: '#fff', display: 'flex', flexDirection: 'column' }}>
              {selectedCase ? (
                <div style={{ flex: 1, overflow: 'auto' }}>
                  <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
                    <h3 style={{ margin: 0 }}>编辑测试用例</h3>
                  </div>
                  <div style={{ padding: '16px' }}>
                    <Form form={form} layout="vertical">
                      <Form.Item
                        name="name"
                        label="测试用例名称"
                        rules={[{ required: true, message: '请输入测试用例名称' }]}
                      >
                        <Input />
                      </Form.Item>
                      
                      <Form.Item
                        name="api"
                        label="API接口"
                        rules={[{ required: true, message: '请选择API接口' }]}
                      >
                        <Select placeholder="选择API接口">
                          {apis.map(api => (
                            <Option key={api.id} value={api.id}>
                              <Tag color="blue">{api.method}</Tag> {api.name} - {api.url}
                            </Option>
                          ))}
                        </Select>
                      </Form.Item>

                      <div style={{ display: 'flex', gap: '16px' }}>
                        <Form.Item
                          name="expected_status_code"
                          label="预期状态码"
                          style={{ flex: 1 }}
                        >
                          <InputNumber min={100} max={599} style={{ width: '100%' }} />
                        </Form.Item>
                        <Form.Item
                          name="max_response_time"
                          label="最大响应时间(ms)"
                          style={{ flex: 1 }}
                        >
                          <InputNumber min={1} style={{ width: '100%' }} />
                        </Form.Item>
                        <Form.Item
                          name="is_active"
                          label="启用状态"
                          valuePropName="checked"
                        >
                          <Switch />
                        </Form.Item>
                      </div>

                      <Tabs defaultActiveKey="request">
                        <TabPane tab="请求配置" key="request">
                          <Form.Item
                            name="headers"
                            label="请求头 (JSON)"
                          >
                            <TextArea 
                              rows={4} 
                              placeholder='{"Content-Type": "application/json"}'
                              style={{ fontFamily: 'monospace' }}
                            />
                          </Form.Item>
                          
                          <Form.Item
                            name="params"
                            label="URL参数 (JSON)"
                          >
                            <TextArea 
                              rows={4} 
                              placeholder='{"page": 1, "size": 10}'
                              style={{ fontFamily: 'monospace' }}
                            />
                          </Form.Item>
                          
                          <Form.Item
                            name="body"
                            label="请求体 (JSON)"
                          >
                            <TextArea 
                              rows={6} 
                              placeholder='{"username": "{{username}}", "password": "{{password}}"}'
                              style={{ fontFamily: 'monospace' }}
                            />
                          </Form.Item>
                        </TabPane>
                        
                        <TabPane tab="断言配置" key="assertions">
                          <Form.Item
                            name="assertions"
                            label="断言规则 (JSON数组)"
                          >
                            <TextArea 
                              rows={8} 
                              placeholder='[{"type": "json_path", "field": "status", "expected": "success"}]'
                              style={{ fontFamily: 'monospace' }}
                            />
                          </Form.Item>
                        </TabPane>
                        
                        <TabPane tab="变量配置" key="variables">
                          <Form.Item
                            name="variables"
                            label="测试变量 (JSON)"
                          >
                            <TextArea 
                              rows={6} 
                              placeholder='{"username": "test_user", "password": "test123"}'
                              style={{ fontFamily: 'monospace' }}
                            />
                          </Form.Item>
                        </TabPane>
                      </Tabs>

                      <Form.Item
                        name="description"
                        label="测试描述"
                      >
                        <TextArea rows={3} />
                      </Form.Item>
                    </Form>
                  </div>
                </div>
              ) : (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: '100%',
                  color: '#999'
                }}>
                  <div style={{ textAlign: 'center' }}>
                    <FileTextOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                    <div>请从左侧选择一个测试用例进行编辑</div>
                  </div>
                </div>
              )}
            </div>
          </Allotment.Pane>

          {/* 右侧响应面板 (35%) */}
          <Allotment.Pane minSize={300}>
            <div style={{ height: '100%', background: '#fff', borderLeft: '1px solid #f0f0f0' }}>
              <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0' }}>
                <h3 style={{ margin: 0 }}>测试结果</h3>
              </div>
              <div style={{ height: 'calc(100% - 65px)', overflow: 'auto' }}>
                {responseLoading ? (
                  <div style={{ padding: '40px', textAlign: 'center' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: '16px' }}>正在执行测试...</div>
                  </div>
                ) : response ? (
                  <Tabs activeKey={activeResponseTab} onChange={setActiveResponseTab}>
                    <TabPane tab="响应结果" key="response">
                      <div style={{ padding: '16px' }}>
                        <Card size="small" style={{ marginBottom: '16px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Tag color={getStatusColor(response.status)} style={{ fontSize: '14px' }}>
                              {response.status?.toUpperCase() || 'UNKNOWN'}
                            </Tag>
                            <div style={{ fontSize: '12px', color: '#666' }}>
                              {formatResponseTime(response.response_time)}
                            </div>
                          </div>
                        </Card>
                        
                        {response.response_code && (
                          <div style={{ marginBottom: '16px' }}>
                            <strong>状态码:</strong> {response.response_code}
                          </div>
                        )}
                        
                        {response.error_message && (
                          <Alert 
                            message="错误信息" 
                            description={response.error_message}
                            type="error" 
                            style={{ marginBottom: '16px' }}
                          />
                        )}
                        
                        {response.response_body && (
                          <div>
                            <strong>响应体:</strong>
                            <pre style={{ 
                              background: '#f5f5f5', 
                              padding: '12px', 
                              borderRadius: '4px',
                              marginTop: '8px',
                              fontSize: '12px',
                              maxHeight: '300px',
                              overflow: 'auto'
                            }}>
                              {JSON.stringify(JSON.parse(response.response_body), null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    </TabPane>
                    
                    <TabPane tab="断言结果" key="assertions">
                      <div style={{ padding: '16px' }}>
                        {response.assertion_results && JSON.parse(response.assertion_results).map((assertion, index) => (
                          <Card key={index} size="small" style={{ marginBottom: '8px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span>{assertion.type}</span>
                              <Tag color={assertion.passed ? 'green' : 'red'}>
                                {assertion.passed ? '通过' : '失败'}
                              </Tag>
                            </div>
                            <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                              {assertion.message}
                            </div>
                          </Card>
                        ))}
                      </div>
                    </TabPane>
                    
                    <TabPane tab="请求头" key="headers">
                      <div style={{ padding: '16px' }}>
                        {response.response_headers && (
                          <pre style={{ 
                            background: '#f5f5f5', 
                            padding: '12px', 
                            borderRadius: '4px',
                            fontSize: '12px',
                            maxHeight: '400px',
                            overflow: 'auto'
                          }}>
                            {JSON.stringify(JSON.parse(response.response_headers), null, 2)}
                          </pre>
                        )}
                      </div>
                    </TabPane>
                  </Tabs>
                ) : (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center', 
                    height: '100%',
                    color: '#999'
                  }}>
                    <div style={{ textAlign: 'center' }}>
                      <BugOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                      <div>点击执行测试查看结果</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </Allotment.Pane>
        </Allotment>
      </div>

      {/* 环境管理模态框 */}
      <Modal
        title="创建新环境"
        visible={envModalVisible}
        onOk={createEnvironment}
        onCancel={() => setEnvModalVisible(false)}
        destroyOnClose
      >
        <Form form={envForm} layout="vertical">
          <Form.Item
            name="name"
            label="环境名称"
            rules={[{ required: true, message: '请输入环境名称' }]}
          >
            <Input placeholder="如：开发环境、测试环境" />
          </Form.Item>
          <Form.Item
            name="description"
            label="环境描述"
          >
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item
            name="is_default"
            label="设为默认环境"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>

      {/* 设置抽屉 */}
      <Drawer
        title="编辑器设置"
        placement="right"
        width={400}
        onClose={() => setSettingsVisible(false)}
        visible={settingsVisible}
      >
        <div>
          <h4>界面设置</h4>
          <p>编辑器主题、字体大小等设置将在未来版本中提供</p>
          
          <h4>快捷键</h4>
          <ul>
            <li>Ctrl+S: 保存测试用例</li>
            <li>Ctrl+Enter: 执行测试</li>
            <li>Ctrl+N: 新建测试用例</li>
          </ul>
        </div>
      </Drawer>
    </div>
  );
};

export default InteractiveTestEditor;