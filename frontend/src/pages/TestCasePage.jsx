import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Table, Form, Input, Select, Button, Modal, Space, Tag, InputNumber, Switch, message } from 'antd';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const TestCasePage = () => {
  const [cases, setCases] = useState([]);
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchCases();
    fetchApis();
  }, []);

  const fetchCases = async () => {
    try {
      const response = await axios.get('/api-test/ApiTestCaseViewSet/');
      setCases(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching test cases:', error);
      setLoading(false);
    }
  };

  const fetchApis = async () => {
    try {
      const response = await axios.get('/api-test/ApiDefinitionViewSet/');
      setApis(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching APIs:', error);
    }
  };

  const handleAdd = () => {
    setEditingCase(null);
    form.resetFields();
    form.setFieldsValue({
      headers: '{}',
      params: '{}',
      body: '{}',
      assertions: '[]',
      variables: '{}',
      expected_status_code: 200,
      is_active: true
    });
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingCase(record);
    // 格式化JSON字段用于编辑
    const formattedRecord = {
      ...record,
      headers: record.headers ? JSON.stringify(record.headers, null, 2) : '{}',
      params: record.params ? JSON.stringify(record.params, null, 2) : '{}',
      body: record.body ? JSON.stringify(record.body, null, 2) : '{}',
      assertions: record.assertions ? JSON.stringify(record.assertions, null, 2) : '[]',
      variables: record.variables ? JSON.stringify(record.variables, null, 2) : '{}',
    };
    form.setFieldsValue(formattedRecord);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this test case?')) {
      try {
        await axios.delete(`/api-test/ApiTestCaseViewSet/${id}/`);
        fetchCases();
        message.success('Test case deleted successfully');
      } catch (error) {
        console.error('Error deleting test case:', error);
        message.error('Failed to delete test case');
      }
    }
  };

  const handleExecute = async (id) => {
    try {
      const response = await axios.post(`/api-test/ApiTestCaseViewSet/${id}/execute/`);
      message.success(`Test executed successfully: ${response.data.status}`);
      fetchCases(); // 刷新列表以显示最新状态
    } catch (error) {
      console.error('Error executing test case:', error);
      message.error('Failed to execute test case');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      // 解析JSON字段
      const submitValues = {
        ...values,
        headers: values.headers ? JSON.parse(values.headers) : {},
        params: values.params ? JSON.parse(values.params) : {},
        body: values.body ? JSON.parse(values.body) : {},
        assertions: values.assertions ? JSON.parse(values.assertions) : [],
        variables: values.variables ? JSON.parse(values.variables) : {},
      };

      if (editingCase) {
        await axios.put(`/api-test/ApiTestCaseViewSet/${editingCase.id}/`, submitValues);
        message.success('Test case updated successfully');
      } else {
        await axios.post('/api-test/ApiTestCaseViewSet/', submitValues);
        message.success('Test case created successfully');
      }
      setModalVisible(false);
      fetchCases();
    } catch (error) {
      console.error('Error saving test case:', error);
      if (error.response?.data) {
        message.error(`Error: ${JSON.stringify(error.response.data)}`);
      } else {
        message.error('Failed to save test case');
      }
    }
  };

  const handleModalCancel = () => {
    setModalVisible(false);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'API',
      dataIndex: 'api',
      key: 'api',
      render: (apiId) => {
        const api = apis.find(a => a.id === apiId);
        return api ? `${api.method} ${api.name}` : apiId;
      },
    },
    {
      title: 'Status Code',
      dataIndex: 'expected_status_code',
      key: 'expected_status_code',
    },
    {
      title: 'Max Response Time',
      dataIndex: 'max_response_time',
      key: 'max_response_time',
      render: (time) => time ? `${time}ms` : '-',
    },
    {
      title: 'Active',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? 'Active' : 'Inactive'}
        </Tag>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (text, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleEdit(record)}>Edit</Button>
          <Button type="link" onClick={() => handleExecute(record.id)}>Execute</Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>Delete</Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>API Test Cases</Title>
        <Button type="primary" onClick={handleAdd} style={{ marginBottom: '20px' }}>
          Add New Test Case
        </Button>
        <Table 
          columns={columns} 
          dataSource={cases} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }}
        />

        <Modal
          title={editingCase ? 'Edit Test Case' : 'Add New Test Case'}
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
              label="Name"
              rules={[{ required: true, message: 'Please enter test case name' }]}
            >
              <Input />
            </Form.Item>
            
            <Form.Item
              name="api"
              label="API Definition"
              rules={[{ required: true, message: 'Please select API definition' }]}
            >
              <Select>
                {apis.map(api => (
                  <Option key={api.id} value={api.id}>
                    {api.method} {api.name} - {api.url}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name="expected_status_code"
              label="Expected Status Code"
              rules={[{ required: true, message: 'Please enter expected status code' }]}
            >
              <InputNumber min={100} max={599} />
            </Form.Item>

            <Form.Item
              name="max_response_time"
              label="Max Response Time (ms)"
            >
              <InputNumber min={1} />
            </Form.Item>

            <Form.Item
              name="is_active"
              label="Active"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              name="headers"
              label="Headers (JSON)"
              help="Override API definition headers"
            >
              <TextArea rows={3} />
            </Form.Item>

            <Form.Item
              name="params"
              label="Parameters (JSON)"
              help="Override API definition parameters"
            >
              <TextArea rows={3} />
            </Form.Item>

            <Form.Item
              name="body"
              label="Request Body (JSON)"
              help="Override API definition body"
            >
              <TextArea rows={3} />
            </Form.Item>

            <Form.Item
              name="assertions"
              label="Assertions (JSON Array)"
              help="Define test assertions"
            >
              <TextArea rows={4} />
            </Form.Item>

            <Form.Item
              name="variables"
              label="Variables (JSON)"
              help="Define variables for test execution"
            >
              <TextArea rows={3} />
            </Form.Item>

            <Form.Item
              name="description"
              label="Description"
            >
              <TextArea rows={2} />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </div>
  );
};

export default TestCasePage;