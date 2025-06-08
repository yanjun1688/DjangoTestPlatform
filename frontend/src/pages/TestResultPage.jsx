import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Table, Button, Space, Tag, Modal, Descriptions, Card, Timeline } from 'antd';

const { Title } = Typography;

const TestResultPage = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      const response = await axios.get('/api-test/ApiTestResultViewSet/');
      setResults(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching test results:', error);
      setLoading(false);
    }
  };

  const handleViewDetail = (record) => {
    setSelectedResult(record);
    setDetailVisible(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this test result?')) {
      try {
        await axios.delete(`/api-test/ApiTestResultViewSet/${id}/`);
        fetchResults();
      } catch (error) {
        console.error('Error deleting test result:', error);
      }
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': return 'green';
      case 'failed': return 'red';
      case 'error': return 'orange';
      default: return 'default';
    }
  };

  const columns = [
    {
      title: 'Test Case',
      dataIndex: 'test_case',
      key: 'test_case',
      render: (testCaseId) => `Test Case #${testCaseId}`,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Response Code',
      dataIndex: 'response_code',
      key: 'response_code',
      render: (code) => code || '-',
    },
    {
      title: 'Response Time',
      dataIndex: 'response_time',
      key: 'response_time',
      render: (time) => time ? `${time.toFixed(2)}ms` : '-',
    },
    {
      title: 'Executed At',
      dataIndex: 'executed_at',
      key: 'executed_at',
      render: (time) => formatDateTime(time),
    },
    {
      title: 'Executed By',
      dataIndex: 'executed_by',
      key: 'executed_by',
      render: (userId) => `User #${userId}`,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (text, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleViewDetail(record)}>View Detail</Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>Delete</Button>
        </Space>
      ),
    },
  ];

  const renderAssertionResults = (assertionResults) => {
    if (!assertionResults || assertionResults.length === 0) {
      return <div>No assertions</div>;
    }

    return (
      <Timeline>
        {assertionResults.map((assertion, index) => (
          <Timeline.Item
            key={index}
            color={assertion.passed ? 'green' : 'red'}
          >
            <div>
              <strong>{assertion.type}</strong>
              {assertion.field && <span> - {assertion.field}</span>}
              <div>Expected: {JSON.stringify(assertion.expected)}</div>
              <div>Actual: {JSON.stringify(assertion.actual)}</div>
              <div style={{ color: assertion.passed ? 'green' : 'red' }}>
                {assertion.message}
              </div>
            </div>
          </Timeline.Item>
        ))}
      </Timeline>
    );
  };

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>Test Results</Title>
        <Table 
          columns={columns} 
          dataSource={results} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 20 }}
        />

        <Modal
          title="Test Result Detail"
          visible={detailVisible}
          onCancel={() => setDetailVisible(false)}
          footer={[
            <Button key="close" onClick={() => setDetailVisible(false)}>
              Close
            </Button>
          ]}
          width={800}
        >
          {selectedResult && (
            <div>
              <Descriptions title="Basic Information" bordered>
                <Descriptions.Item label="Test Case ID">
                  {selectedResult.test_case}
                </Descriptions.Item>
                <Descriptions.Item label="Status">
                  <Tag color={getStatusColor(selectedResult.status)}>
                    {selectedResult.status.toUpperCase()}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Response Code">
                  {selectedResult.response_code || '-'}
                </Descriptions.Item>
                <Descriptions.Item label="Response Time">
                  {selectedResult.response_time ? `${selectedResult.response_time.toFixed(2)}ms` : '-'}
                </Descriptions.Item>
                <Descriptions.Item label="Executed At">
                  {formatDateTime(selectedResult.executed_at)}
                </Descriptions.Item>
                <Descriptions.Item label="Executed By">
                  User #{selectedResult.executed_by}
                </Descriptions.Item>
              </Descriptions>

              {selectedResult.error_message && (
                <Card title="Error Message" style={{ marginTop: 16 }}>
                  <div style={{ color: 'red' }}>{selectedResult.error_message}</div>
                </Card>
              )}

              {selectedResult.response_body && (
                <Card title="Response Body" style={{ marginTop: 16 }}>
                  <pre style={{ maxHeight: '200px', overflow: 'auto' }}>
                    {selectedResult.response_body}
                  </pre>
                </Card>
              )}

              {selectedResult.response_headers && (
                <Card title="Response Headers" style={{ marginTop: 16 }}>
                  <pre style={{ maxHeight: '150px', overflow: 'auto' }}>
                    {JSON.stringify(
                      typeof selectedResult.response_headers === 'string' 
                        ? JSON.parse(selectedResult.response_headers)
                        : selectedResult.response_headers, 
                      null, 2
                    )}
                  </pre>
                </Card>
              )}

              <Card title="Assertion Results" style={{ marginTop: 16 }}>
                {renderAssertionResults(
                  typeof selectedResult.assertion_results === 'string'
                    ? JSON.parse(selectedResult.assertion_results)
                    : selectedResult.assertion_results
                )}
              </Card>
            </div>
          )}
        </Modal>
      </div>
    </div>
  );
};

export default TestResultPage;