import { useState, useEffect } from 'react';
import { Typography, Table, Form, Input, Select, Button, Modal, Space, Tag, message } from 'antd';
import Logger from '../utils/logger';
import { compressJson } from '../utils/jsonUtils';
import api from '../utils/api';
import BackButton from '../components/BackButton';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const ApiDefinitionPage = () => {
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingApi, setEditingApi] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchApis();
  }, []);

  const fetchApis = async () => {
    try {
      Logger.info('Fetching API definitions...');
      const response = await api.get('/api-test/api-definitions/');
      Logger.debug('API definitions response:', response.data);
      setApis(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      Logger.errorWithContext('fetchApis', error);
      message.error('获取API定义失败');
      setLoading(false);
    }
  };

  const handleAdd = () => {
    Logger.info('Opening add API definition modal');
    setEditingApi(null);
    form.resetFields();
    // 设置默认的JSON字符串值
    form.setFieldsValue({
      headers: '{}',
      params: '{}',
      body: '{}'
    });
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    Logger.info('Opening edit API definition modal', { id: record.id });
    setEditingApi(record);
    
    // 修复：正确处理JSON字段
    // 后端返回的是JSON字符串，需要格式化显示
    const formatJsonString = (jsonStr) => {
      try {
        if (!jsonStr || jsonStr === '{}') return '{}';
        // 如果是字符串，先解析再格式化
        const parsed = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
        return JSON.stringify(parsed, null, 2);
      } catch (error) {
        Logger.warn('Failed to format JSON for display:', error.message);
        return jsonStr || '{}';
      }
    };

    const formData = {
      ...record,
      headers: formatJsonString(record.headers),
      params: formatJsonString(record.params),
      body: formatJsonString(record.body),
    };
    
    form.setFieldsValue(formData);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('确定要删除这个API定义吗？')) {
      try {
        Logger.info('Deleting API definition', { id });
        await api.delete(`/api-test/api-definitions/${id}/`);
        message.success('删除成功');
        fetchApis();
      } catch (error) {
        Logger.errorWithContext('handleDelete', error);
        message.error('删除失败');
      }
    }
  };

  const validateJsonField = (fieldName) => {
    return {
      validator: (_, value) => {
        if (!value || value.trim() === '') {
          return Promise.resolve();
        }
        try {
          JSON.parse(value);
          return Promise.resolve();
        } catch (error) {
          Logger.warn(`JSON validation failed for ${fieldName}:`, error.message);
          return Promise.reject(new Error(`${fieldName} 必须是有效的JSON格式`));
        }
      },
    };
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      Logger.formData('ApiDefinitionForm', values);

      // 使用安全的JSON处理函数
      const submitValues = {
        ...values,
        headers: compressJson(values.headers),
        params: compressJson(values.params),
        body: compressJson(values.body),
      };

      Logger.debug('Submit values:', submitValues);

      if (editingApi) {
        Logger.info('Updating API definition', { id: editingApi.id });
        await api.put(`/api-test/api-definitions/${editingApi.id}/`, submitValues);
        message.success('更新成功');
      } else {
        Logger.info('Creating new API definition');
        await api.post('/api-test/api-definitions/', submitValues);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchApis();
    } catch (error) {
      Logger.errorWithContext('handleModalOk', error);
      if (error.message && error.message.includes('JSON格式错误')) {
        message.error('请检查JSON格式是否正确');
      } else if (error.response?.data) {
        message.error(`服务器错误: ${JSON.stringify(error.response.data)}`);
      } else {
        message.error('保存失败');
      }
    }
  };

  const handleModalCancel = () => {
    setModalVisible(false);
  };

  // 渲染JSON字段的显示
  const renderJsonField = (text) => {
    if (!text || text === '{}') return '-';
    try {
      const parsed = typeof text === 'string' ? JSON.parse(text) : text;
      const keys = Object.keys(parsed);
      if (keys.length === 0) return '-';
      return `{${keys.length} 个字段}`;
    } catch {
      return text;
    }
  };

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '方法',
      dataIndex: 'method',
      key: 'method',
      width: 80,
      render: (method) => (
        <Tag color={
          method === 'GET' ? 'green' : 
          method === 'POST' ? 'blue' : 
          method === 'PUT' ? 'gold' : 
          method === 'DELETE' ? 'red' : 
          method === 'PATCH' ? 'purple' : 'default'
        }>
          {method}
        </Tag>
      ),
    },
    {
      title: 'URL',
      dataIndex: 'url',
      key: 'url',
      ellipsis: true,
    },
    {
      title: '模块',
      dataIndex: 'module',
      key: 'module',
      width: 100,
      render: (text) => text || '-',
    },
    {
      title: '请求头',
      dataIndex: 'headers',
      key: 'headers',
      width: 100,
      render: renderJsonField,
    },
    {
      title: '参数',
      dataIndex: 'params',
      key: 'params',
      width: 100,
      render: renderJsonField,
    },
    {
      title: '请求体',
      dataIndex: 'body',
      key: 'body',
      width: 100,
      render: renderJsonField,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (text, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleEdit(record)}>编辑</Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <BackButton />
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>API 定义</Title>
        <Button type="primary" onClick={handleAdd} style={{ marginBottom: '20px' }}>
          添加新API定义
        </Button>
        <Table 
          columns={columns} 
          dataSource={apis} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }}
        />

        <Modal
          title={editingApi ? '编辑API定义' : '添加新API定义'}
          visible={modalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          width={800}
          destroyOnClose
        >
          <Form
            form={form}
            layout="vertical"
          >
            <Form.Item
              name="name"
              label="名称"
              rules={[{ required: true, message: '请输入API名称' }]}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="url"
              label="URL"
              rules={[{ required: true, message: '请输入API URL' }]}
            >
              <Input placeholder="https://api.example.com/endpoint" />
            </Form.Item>

            <Form.Item
              name="method"
              label="请求方法"
              rules={[{ required: true, message: '请选择请求方法' }]}
            >
              <Select>
                <Option value="GET">GET</Option>
                <Option value="POST">POST</Option>
                <Option value="PUT">PUT</Option>
                <Option value="DELETE">DELETE</Option>
                <Option value="PATCH">PATCH</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="module"
              label="所属模块"
            >
              <Input placeholder="例如：用户管理、订单系统等" />
            </Form.Item>

            <Form.Item
              name="headers"
              label="请求头 (JSON)"
              rules={[validateJsonField('请求头')]}
            >
              <TextArea 
                rows={4} 
                placeholder='{"Content-Type": "application/json", "Authorization": "Bearer token"}'
              />
            </Form.Item>

            <Form.Item
              name="params"
              label="URL参数 (JSON)"
              rules={[validateJsonField('URL参数')]}
            >
              <TextArea 
                rows={4} 
                placeholder='{"page": 1, "size": 10}'
              />
            </Form.Item>

            <Form.Item
              name="body"
              label="请求体 (JSON)"
              rules={[validateJsonField('请求体')]}
            >
              <TextArea 
                rows={4} 
                placeholder='{"name": "test", "email": "test@example.com"}'
              />
            </Form.Item>

            <Form.Item
              name="description"
              label="描述"
            >
              <TextArea rows={3} placeholder="API的详细描述..." />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  );
};

export default ApiDefinitionPage;
