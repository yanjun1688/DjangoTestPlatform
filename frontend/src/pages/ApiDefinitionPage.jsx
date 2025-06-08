import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Table, Form, Input, Select, Button, Modal, Space, Tag, message } from 'antd';

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
      // 修复：使用正确的API路径
      const response = await axios.get('/api-test/api-definitions/');
      setApis(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching API definitions:', error);
      message.error('获取API定义失败');
      setLoading(false);
    }
  };

  const handleAdd = () => {
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
    setEditingApi(record);
    
    // 修复：正确处理JSON字段
    // 后端返回的是JSON字符串，需要格式化显示
    const formatJsonString = (jsonStr) => {
      try {
        if (!jsonStr || jsonStr === '{}') return '{}';
        // 如果是字符串，先解析再格式化
        const parsed = typeof jsonStr === 'string' ? JSON.parse(jsonStr) : jsonStr;
        return JSON.stringify(parsed, null, 2);
      } catch (e) {
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
        // 修复：使用正确的删除路径
        await axios.delete(`/api-test/api-definitions/${id}/`);
        message.success('删除成功');
        fetchApis();
      } catch (error) {
        console.error('Error deleting API definition:', error);
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
        } catch (e) {
          return Promise.reject(new Error(`${fieldName} 必须是有效的JSON格式`));
        }
      },
    };
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      // 修复：正确处理JSON字段提交
      // 确保提交的是有效的JSON字符串
      const processJsonField = (value) => {
        if (!value || value.trim() === '') return '{}';
        try {
          // 验证JSON格式并返回压缩的字符串
          JSON.parse(value);
          return value.trim();
        } catch (e) {
          throw new Error('JSON格式错误');
        }
      };

      const submitValues = {
        ...values,
        headers: processJsonField(values.headers),
        params: processJsonField(values.params),
        body: processJsonField(values.body),
      };

      if (editingApi) {
        await axios.put(`/api-test/api-definitions/${editingApi.id}/`, submitValues);
        message.success('更新成功');
      } else {
        await axios.post('/api-test/api-definitions/', submitValues);
        message.success('创建成功');
      }
      setModalVisible(false);
      fetchApis();
    } catch (error) {
      console.error('Error saving API definition:', error);
      if (error.message === 'JSON格式错误') {
        message.error('请检查JSON格式是否正确');
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
      return `{${keys.length} fields}`;
    } catch (e) {
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
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      width: 150,
      ellipsis: true,
      render: (text) => text || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 150,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (text, record) => (
        <Space size="small">
          <Button type="link" size="small" onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" size="small" danger onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ 
          background: '#fff', 
          padding: '24px', 
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <Title level={2} style={{ margin: 0 }}>API定义管理</Title>
            <Button type="primary" onClick={handleAdd}>
              新增API定义
            </Button>
          </div>
          
          <Table 
            columns={columns} 
            dataSource={apis} 
            rowKey="id" 
            loading={loading}
            pagination={{ 
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `共 ${total} 条记录`
            }}
            scroll={{ x: 1200 }}
          />
        </div>

        <Modal
          title={editingApi ? '编辑API定义' : '新增API定义'}
          visible={modalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          width={700}
          destroyOnClose
        >
          <Form
            form={form}
            layout="vertical"
            preserve={false}
          >
            <Form.Item
              name="name"
              label="接口名称"
              rules={[
                { required: true, message: '请输入接口名称' },
                { max: 200, message: '接口名称不能超过200个字符' }
              ]}
            >
              <Input placeholder="请输入接口名称" />
            </Form.Item>
            
            <Form.Item
              name="url"
              label="接口URL"
              rules={[
                { required: true, message: '请输入接口URL' },
                { max: 500, message: 'URL不能超过500个字符' },
                { type: 'url', message: '请输入有效的URL格式' }
              ]}
            >
              <Input placeholder="https://api.example.com/v1/users" />
            </Form.Item>
            
            <Form.Item
              name="method"
              label="请求方法"
              rules={[{ required: true, message: '请选择请求方法' }]}
            >
              <Select placeholder="请选择请求方法">
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
              rules={[{ max: 100, message: '模块名不能超过100个字符' }]}
            >
              <Input placeholder="用户管理、订单管理等" />
            </Form.Item>
            
            <Form.Item
              name="headers"
              label="请求头 (JSON格式)"
              rules={[validateJsonField('请求头')]}
            >
              <TextArea 
                rows={4} 
                placeholder='{"Content-Type": "application/json", "Authorization": "Bearer token"}'
              />
            </Form.Item>
            
            <Form.Item
              name="params"
              label="URL参数 (JSON格式)"
              rules={[validateJsonField('URL参数')]}
            >
              <TextArea 
                rows={4} 
                placeholder='{"page": 1, "size": 10, "keyword": "search"}'
              />
            </Form.Item>
            
            <Form.Item
              name="body"
              label="请求体 (JSON格式)"
              rules={[validateJsonField('请求体')]}
            >
              <TextArea 
                rows={4} 
                placeholder='{"name": "John", "email": "john@example.com"}'
              />
            </Form.Item>
            
            <Form.Item
              name="description"
              label="接口描述"
            >
              <TextArea 
                rows={3} 
                placeholder="请描述此接口的功能和用途"
                maxLength={500}
                showCount
              />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  );
};

export default ApiDefinitionPage;