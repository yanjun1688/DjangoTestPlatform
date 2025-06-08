import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Table, Form, Input, Select, Button, Modal, Space, Tag, Transfer, message, Progress } from 'antd';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const TestSuitePage = () => {
  const [suites, setSuites] = useState([]);
  const [testCases, setTestCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSuite, setEditingSuite] = useState(null);
  const [executionModalVisible, setExecutionModalVisible] = useState(false);
  const [executionResults, setExecutionResults] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchSuites();
    fetchTestCases();
  }, []);

  const fetchSuites = async () => {
    try {
      const response = await axios.get('/api-test/ApiTestSuiteViewSet/');
      setSuites(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching test suites:', error);
      setLoading(false);
    }
  };

  const fetchTestCases = async () => {
    try {
      const response = await axios.get('/api-test/ApiTestCaseViewSet/');
      setTestCases(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error fetching test cases:', error);
    }
  };

  const handleAdd = () => {
    setEditingSuite(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingSuite(record);
    form.setFieldsValue({
      ...record,
      test_cases: record.test_cases || []
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this test suite?')) {
      try {
        await axios.delete(`/api-test/ApiTestSuiteViewSet/${id}/`);
        fetchSuites();
        message.success('Test suite deleted successfully');
      } catch (error) {
        console.error('Error deleting test suite:', error);
        message.error('Failed to delete test suite');
      }
    }
  };

  const handleExecute = async (id) => {
    try {
      const response = await axios.post(`/api-test/ApiTestSuiteViewSet/${id}/execute/`);
      setExecutionResults(response.data);
      setExecutionModalVisible(true);
      message.success('Test suite executed successfully');
    } catch (error) {
      console.error('Error executing test suite:', error);
      message.error('Failed to execute test suite');
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();

      if (editingSuite) {
        await axios.put(`/api-test/ApiTestSuiteViewSet/${editingSuite.id}/`, values);
        message.success('Test suite updated successfully');
      } else {
        await axios.post('/api-test/ApiTestSuiteViewSet/', values);
        message.success('Test suite created successfully');
      }
      setModalVisible(false);
      fetchSuites();
    } catch (error) {
      console.error('Error saving test suite:', error);
      message.error('Failed to save test suite');
    }
  };

  const handleModalCancel = () => {
    setModalVisible(false);
  };

  const getTransferData = () => {
    return testCases.map(tc => ({
      key: tc.id.toString(),
      title: tc.name,
      description: tc.description || 'No description'
    }));
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Test Cases Count',
      dataIndex: 'test_cases',
      key: 'test_cases_count',
      render: (testCases) => testCases ? testCases.length : 0,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (time) => new Date(time).toLocaleString(),
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

  const renderExecutionResults = () => {
    if (!executionResults) return null;

    const { total_cases, passed, failed, errors, results } = executionResults;
    const successRate = total_cases > 0 ? (passed / total_cases) * 100 : 0;

    return (
      <div>
        <div style={{ marginBottom: 20 }}>
          <h3>Execution Summary</h3>
          <Progress
            percent={successRate}
            status={successRate === 100 ? 'success' : successRate > 50 ? 'active' : 'exception'}
            format={() => `${passed}/${total_cases} passed`}
          />
          <div style={{ marginTop: 10 }}>
            <Tag color="green">Passed: {passed}</Tag>
            <Tag color="red">Failed: {failed}</Tag>
            <Tag color="orange">Errors: {errors}</Tag>
          </div>
        </div>

        <Table
          dataSource={results}
          rowKey="id"
          pagination={false}
          columns={[
            {
              title: 'Test Case',
              dataIndex: 'test_case',
              key: 'test_case',
            },
            {
              title: 'Status',
              dataIndex: 'status',
              key: 'status',
              render: (status) => (
                <Tag color={status === 'passed' ? 'green' : status === 'failed' ? 'red' : 'orange'}>
                  {status.toUpperCase()}
                </Tag>
              ),
            },
            {
              title: 'Response Time',
              dataIndex: 'response_time',
              key: 'response_time',
              render: (time) => time ? `${time.toFixed(2)}ms` : '-',
            },
            {
              title: 'Error Message',
              dataIndex: 'error_message',
              key: 'error_message',
              ellipsis: true,
            },
          ]}
        />
      </div>
    );
  };

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>Test Suites</Title>
        <Button type="primary" onClick={handleAdd} style={{ marginBottom: '20px' }}>
          Add New Test Suite
        </Button>
        <Table 
          columns={columns} 
          dataSource={suites} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }}
        />

        <Modal
          title={editingSuite ? 'Edit Test Suite' : 'Add New Test Suite'}
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
              rules={[{ required: true, message: 'Please enter suite name' }]}
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="description"
              label="Description"
            >
              <TextArea rows={3} />
            </Form.Item>

            <Form.Item
              name="test_cases"
              label="Test Cases"
            >
              <Transfer
                dataSource={getTransferData()}
                targetKeys={form.getFieldValue('test_cases')?.map(id => id.toString()) || []}
                onChange={(targetKeys) => {
                  form.setFieldsValue({
                    test_cases: targetKeys.map(key => parseInt(key))
                  });
                }}
                render={item => item.title}
                showSearch
                listStyle={{
                  width: 300,
                  height: 300,
                }}
              />
            </Form.Item>
          </Form>
        </Modal>

        <Modal
          title="Execution Results"
          visible={executionModalVisible}
          onCancel={() => setExecutionModalVisible(false)}
          footer={[
            <Button key="close" onClick={() => setExecutionModalVisible(false)}>
              Close
            </Button>
          ]}
          width={1000}
        >
          {renderExecutionResults()}
        </Modal>
      </div>
    </div>
  );
};

export default TestSuitePage;