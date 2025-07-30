import { useState, useEffect } from 'react';
import axios from 'axios';
import { Typography, Table, Button, Space, Tag, Modal, Descriptions, Card, Timeline, message } from 'antd';
import Logger from '../utils/logger';
import api from '../utils/api';
import BackButton from '../components/BackButton';

const { Title } = Typography;

const TestResultPage = () => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [selectedResult, setSelectedResult] = useState(null);

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      Logger.info('Fetching test results...');
      const response = await api.get('/api-test/api-test-results/');
      Logger.debug('Test results response:', response.data);
      setResults(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      Logger.errorWithContext('fetchResults', error);
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('确定要删除这个测试结果吗？')) {
      try {
        Logger.info('Deleting test result', { id });
        await api.delete(`/api-test/api-test-results/${id}/`);
        fetchResults();
        message.success('测试结果删除成功');
      } catch (error) {
        Logger.errorWithContext('handleDelete', error);
        message.error('删除测试结果失败');
      }
    }
  };

  const handleViewDetail = (record) => {
    Logger.info('Opening test result detail modal', { id: record.id });
    setSelectedResult(record);
    setDetailModalVisible(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': return 'green';
      case 'failed': return 'red';
      case 'error': return 'orange';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'passed': return '通过';
      case 'failed': return '失败';
      case 'error': return '错误';
      default: return status;
    }
  };

  const columns = [
    {
      title: '测试用例',
      dataIndex: 'test_case_name',
      key: 'test_case_name',
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
      title: '响应状态码',
      dataIndex: 'response_code',
      key: 'response_code',
      render: (code) => code || '-',
    },
    {
      title: '响应时间',
      dataIndex: 'response_time',
      key: 'response_time',
      render: (time) => time ? `${time.toFixed(2)}ms` : '-',
    },
    {
      title: '执行人',
      dataIndex: 'executed_by_username',
      key: 'executed_by_username',
      render: (username) => username || '系统',
    },
    {
      title: '执行时间',
      dataIndex: 'executed_at',
      key: 'executed_at',
      render: (time) => new Date(time).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'actions',
      render: (text, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleViewDetail(record)}>查看详情</Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <BackButton />
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>测试结果</Title>
        <Table 
          columns={columns} 
          dataSource={results} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }}
        />

        <Modal
          title="测试结果详情"
          visible={detailModalVisible}
          onCancel={() => setDetailModalVisible(false)}
          footer={null}
          width={800}
        >
          {selectedResult && (
            <div>
              <Descriptions title="基本信息" bordered column={2}>
                <Descriptions.Item label="测试用例">{selectedResult.test_case_name}</Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag color={getStatusColor(selectedResult.status)}>
                    {getStatusText(selectedResult.status)}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="响应状态码">{selectedResult.response_code || '-'}</Descriptions.Item>
                <Descriptions.Item label="响应时间">{selectedResult.response_time ? `${selectedResult.response_time.toFixed(2)}ms` : '-'}</Descriptions.Item>
                <Descriptions.Item label="执行人">{selectedResult.executed_by_username || '系统'}</Descriptions.Item>
                <Descriptions.Item label="执行时间">{new Date(selectedResult.executed_at).toLocaleString('zh-CN')}</Descriptions.Item>
              </Descriptions>

              {selectedResult.error_message && (
                <Card title="错误信息" style={{ marginTop: '16px' }}>
                  <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                    {selectedResult.error_message}
                  </pre>
                </Card>
              )}

              {selectedResult.assertion_results && selectedResult.assertion_results.length > 0 && (
                <Card title="断言结果" style={{ marginTop: '16px' }}>
                  <Timeline>
                    {selectedResult.assertion_results.map((assertion, index) => (
                      <Timeline.Item 
                        key={index}
                        color={assertion.passed ? 'green' : 'red'}
                      >
                        <p><strong>{assertion.type}</strong></p>
                        <p>期望: {assertion.expected}</p>
                        <p>实际: {assertion.actual}</p>
                        <p>结果: {assertion.passed ? '通过' : '失败'}</p>
                        {assertion.message && <p>消息: {assertion.message}</p>}
                      </Timeline.Item>
                    ))}
                  </Timeline>
                </Card>
              )}

              <Card title="响应内容" style={{ marginTop: '16px' }}>
                <pre style={{ 
                  whiteSpace: 'pre-wrap', 
                  wordBreak: 'break-word',
                  maxHeight: '300px',
                  overflow: 'auto',
                  backgroundColor: '#f5f5f5',
                  padding: '8px',
                  borderRadius: '4px'
                }}>
                  {selectedResult.response_body || '无响应内容'}
                </pre>
              </Card>
            </div>
          )}
        </Modal>
      </div>
    </div>
  );
};

export default TestResultPage;