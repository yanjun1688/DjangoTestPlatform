import { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Input, Switch, Tag, Space, message, Drawer, Collapse, Alert } from 'antd';
import { 
  GlobalOutlined, 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SettingOutlined,
  EyeOutlined,
  CopyOutlined,
  StarOutlined,
  StarFilled
} from '@ant-design/icons';
import api from '../utils/api';
import Logger from '../utils/logger';
import BackButton from '../components/BackButton';

const { TextArea } = Input;
const { Panel } = Collapse;

const EnvironmentManagePage = () => {
  const [environments, setEnvironments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingEnv, setEditingEnv] = useState(null);
  const [variableDrawerVisible, setVariableDrawerVisible] = useState(false);
  const [selectedEnv, setSelectedEnv] = useState(null);
  const [variables, setVariables] = useState([]);
  const [variableForm] = Form.useForm();
  const [form] = Form.useForm();
  const [usageStats, setUsageStats] = useState([]);
  const [cloneModalVisible, setCloneModalVisible] = useState(false);
  const [cloneForm] = Form.useForm();

  useEffect(() => {
    loadEnvironments();
    loadUsageStats();
  }, []);

  const loadEnvironments = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/environments/environments/');
      setEnvironments(response.data || []);
    } catch (error) {
      Logger.errorWithContext('loadEnvironments', error);
      message.error('加载环境列表失败');
    } finally {
      setLoading(false);
    }
  };

  const loadUsageStats = async () => {
    try {
      const response = await api.get('/api/environments/environments/usage_stats/');
      setUsageStats(response.data || []);
    } catch (error) {
      Logger.errorWithContext('loadUsageStats', error);
    }
  };

  const loadVariables = async (envId) => {
    try {
      const response = await api.get(`/api/environments/environments/${envId}/variables/`);
      setVariables(response.data || []);
    } catch (error) {
      Logger.errorWithContext('loadVariables', error);
      message.error('加载环境变量失败');
    }
  };

  const handleCreateEnvironment = () => {
    setEditingEnv(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditEnvironment = (env) => {
    setEditingEnv(env);
    form.setFieldsValue(env);
    setModalVisible(true);
  };

  const handleDeleteEnvironment = async (envId) => {
    if (window.confirm('确定要删除这个环境吗？这将同时删除所有关联的环境变量。')) {
      try {
        await api.delete(`/api/environments/environments/${envId}/`);
        message.success('环境删除成功');
        loadEnvironments();
      } catch (error) {
        Logger.errorWithContext('handleDeleteEnvironment', error);
        message.error('删除环境失败');
      }
    }
  };

  const handleSetDefault = async (envId) => {
    try {
      await api.post(`/api/environments/environments/${envId}/set_default/`);
      message.success('默认环境设置成功');
      loadEnvironments();
    } catch (error) {
      Logger.errorWithContext('handleSetDefault', error);
      message.error('设置默认环境失败');
    }
  };

  const handleCloneEnvironment = (env) => {
    setEditingEnv(env);
    cloneForm.setFieldsValue({
      name: `${env.name} (副本)`,
      description: env.description
    });
    setCloneModalVisible(true);
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingEnv) {
        await api.put(`/api/environments/environments/${editingEnv.id}/`, values);
        message.success('环境更新成功');
      } else {
        await api.post('/api/environments/environments/', values);
        message.success('环境创建成功');
      }
      
      setModalVisible(false);
      loadEnvironments();
    } catch (error) {
      Logger.errorWithContext('handleModalOk', error);
      message.error('保存环境失败');
    }
  };

  const handleCloneOk = async () => {
    try {
      const values = await cloneForm.validateFields();
      await api.post(`/api/environments/environments/${editingEnv.id}/clone/`, values);
      message.success('环境克隆成功');
      setCloneModalVisible(false);
      loadEnvironments();
    } catch (error) {
      Logger.errorWithContext('handleCloneOk', error);
      message.error('克隆环境失败');
    }
  };

  const handleManageVariables = (env) => {
    setSelectedEnv(env);
    loadVariables(env.id);
    setVariableDrawerVisible(true);
  };

  const handleAddVariable = async () => {
    try {
      const values = await variableForm.validateFields();
      await api.post(`/api/environments/environments/${selectedEnv.id}/variables/`, values);
      message.success('环境变量添加成功');
      variableForm.resetFields();
      loadVariables(selectedEnv.id);
    } catch (error) {
      Logger.errorWithContext('handleAddVariable', error);
      message.error('添加环境变量失败');
    }
  };

  const handleDeleteVariable = async (variableId) => {
    if (window.confirm('确定要删除这个环境变量吗？')) {
      try {
        await api.delete(`/api/environments/environments/${selectedEnv.id}/variables/${variableId}/`);
        message.success('环境变量删除成功');
        loadVariables(selectedEnv.id);
      } catch (error) {
        Logger.errorWithContext('handleDeleteVariable', error);
        message.error('删除环境变量失败');
      }
    }
  };

  const handleTestVariableReplacement = async () => {
    try {
      const testText = '测试变量替换: {{base_url}}/api/{{version}}/users';
      const response = await api.post(`/api/environments/environments/${selectedEnv.id}/replace_variables/`, {
        text: testText
      });
      
      Modal.info({
        title: '变量替换测试',
        content: (
          <div>
            <p><strong>原始文本:</strong> {testText}</p>
            <p><strong>替换后:</strong> {response.data.replaced_text}</p>
            <p><strong>使用的变量:</strong> {response.data.variables_used.join(', ')}</p>
          </div>
        )
      });
    } catch (error) {
      Logger.errorWithContext('handleTestVariableReplacement', error);
      message.error('测试变量替换失败');
    }
  };

  const columns = [
    {
      title: '环境名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <GlobalOutlined />
          {text}
          {record.is_default && (
            <Tag color="blue" icon={<StarFilled />}>默认</Tag>
          )}
        </Space>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true
    },
    {
      title: '变量数量',
      dataIndex: 'variables_count',
      key: 'variables_count',
      render: (count) => (
        <Tag color="purple">{count || 0} 个变量</Tag>
      )
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? '启用' : '禁用'}
        </Tag>
      )
    },
    {
      title: '使用次数',
      key: 'usage_count',
      render: (_, record) => {
        const stats = usageStats.find(s => s.environment_id === record.id);
        return <Tag color="cyan">{stats?.usage_count || 0} 次</Tag>;
      }
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleDateString()
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button 
            type="link" 
            icon={<EditOutlined />}
            onClick={() => handleEditEnvironment(record)}
          >
            编辑
          </Button>
          <Button 
            type="link" 
            icon={<SettingOutlined />}
            onClick={() => handleManageVariables(record)}
          >
            变量
          </Button>
          <Button 
            type="link" 
            icon={<CopyOutlined />}
            onClick={() => handleCloneEnvironment(record)}
          >
            克隆
          </Button>
          {!record.is_default && (
            <Button 
              type="link" 
              icon={<StarOutlined />}
              onClick={() => handleSetDefault(record.id)}
            >
              设为默认
            </Button>
          )}
          <Button 
            type="link" 
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteEnvironment(record.id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ];

  const variableColumns = [
    {
      title: '变量名',
      dataIndex: 'key',
      key: 'key',
      render: (key) => <code>{key}</code>
    },
    {
      title: '变量值',
      dataIndex: 'value',
      key: 'value',
      render: (value, record) => (
        record.is_secret ? 
          <span style={{ color: '#999' }}>{'*'.repeat(8)}</span> : 
          <code>{value}</code>
      )
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: '敏感信息',
      dataIndex: 'is_secret',
      key: 'is_secret',
      render: (secret) => (
        <Tag color={secret ? 'red' : 'green'}>
          {secret ? '是' : '否'}
        </Tag>
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Button 
          type="link" 
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDeleteVariable(record.id)}
        >
          删除
        </Button>
      )
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <BackButton />
      <div style={{ marginBottom: '24px' }}>
        <h1>环境管理</h1>
        <p>管理测试环境和环境变量，支持变量替换功能</p>
      </div>

      {/* 使用统计卡片 */}
      <div style={{ marginBottom: '24px' }}>
        <Card title="使用统计" size="small">
          <div style={{ display: 'flex', gap: '24px' }}>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                {environments.length}
              </div>
              <div style={{ color: '#666' }}>环境总数</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
                {environments.filter(env => env.is_active).length}
              </div>
              <div style={{ color: '#666' }}>启用环境</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#722ed1' }}>
                {environments.reduce((sum, env) => sum + (env.variables_count || 0), 0)}
              </div>
              <div style={{ color: '#666' }}>变量总数</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#fa8c16' }}>
                {usageStats.reduce((sum, stat) => sum + stat.usage_count, 0)}
              </div>
              <div style={{ color: '#666' }}>使用次数</div>
            </div>
          </div>
        </Card>
      </div>

      {/* 环境列表 */}
      <Card 
        title="环境列表" 
        extra={(
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={handleCreateEnvironment}
          >
            新建环境
          </Button>
        )}
      >
        <Table
          columns={columns}
          dataSource={environments}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 环境编辑模态框 */}
      <Modal
        title={editingEnv ? '编辑环境' : '新建环境'}
        visible={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="环境名称"
            rules={[{ required: true, message: '请输入环境名称' }]}
          >
            <Input placeholder="如：开发环境、测试环境、生产环境" />
          </Form.Item>
          <Form.Item
            name="description"
            label="环境描述"
          >
            <TextArea rows={3} placeholder="描述此环境的用途和特点" />
          </Form.Item>
          <Form.Item
            name="is_active"
            label="启用状态"
            valuePropName="checked"
          >
            <Switch />
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

      {/* 环境克隆模态框 */}
      <Modal
        title="克隆环境"
        visible={cloneModalVisible}
        onOk={handleCloneOk}
        onCancel={() => setCloneModalVisible(false)}
        destroyOnClose
      >
        <Form form={cloneForm} layout="vertical">
          <Form.Item
            name="name"
            label="新环境名称"
            rules={[{ required: true, message: '请输入新环境名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="description"
            label="环境描述"
          >
            <TextArea rows={3} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 环境变量管理抽屉 */}
      <Drawer
        title={selectedEnv ? `管理环境变量 - ${selectedEnv.name}` : '管理环境变量'}
        width={800}
        onClose={() => setVariableDrawerVisible(false)}
        visible={variableDrawerVisible}
        extra={(
          <Space>
            <Button 
              type="primary" 
              ghost
              onClick={handleTestVariableReplacement}
            >
              测试变量替换
            </Button>
          </Space>
        )}
      >
        <div style={{ marginBottom: '24px' }}>
          <Alert
            message="变量使用说明"
            description={(
              <div>
                <p>在API测试中，可以使用 <code>{'{{变量名}}'}</code> 的格式来引用环境变量。</p>
                <p>例如：<code>{'{{base_url}}'}/api/{'{{version}}'}/users</code></p>
                <p>敏感信息变量（如API密钥、密码等）会在界面上显示为星号。</p>
              </div>
            )}
            type="info"
            showIcon
          />
        </div>

        <Collapse defaultActiveKey={['1']}>
          <Panel header="添加新变量" key="1">
            <Form form={variableForm} layout="vertical">
              <Form.Item
                name="key"
                label="变量名"
                rules={[
                  { required: true, message: '请输入变量名' },
                  { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '变量名只能包含字母、数字和下划线，且不能以数字开头' }
                ]}
              >
                <Input placeholder="如：base_url, api_key, version" />
              </Form.Item>
              <Form.Item
                name="value"
                label="变量值"
                rules={[{ required: true, message: '请输入变量值' }]}
              >
                <Input placeholder="如：https://api.example.com, v1.0" />
              </Form.Item>
              <Form.Item
                name="description"
                label="变量描述"
              >
                <Input placeholder="描述此变量的用途" />
              </Form.Item>
              <Form.Item
                name="is_secret"
                label="敏感信息"
                valuePropName="checked"
              >
                <Switch />
              </Form.Item>
              <Form.Item>
                <Button type="primary" onClick={handleAddVariable}>
                  添加变量
                </Button>
              </Form.Item>
            </Form>
          </Panel>
        </Collapse>

        <div style={{ marginTop: '24px' }}>
          <Table
            columns={variableColumns}
            dataSource={variables}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            size="small"
          />
        </div>
      </Drawer>
    </div>
  );
};

export default EnvironmentManagePage;