import { useState, useEffect, useMemo, useCallback } from 'react';
import axios from 'axios';
import { Typography, Table, Form, Input, Select, Button, Modal, Space, Tag, InputNumber, Switch, message, Tabs, Upload, Alert, Divider, Collapse, Drawer } from 'antd';
import { UploadOutlined, DeleteOutlined, EyeOutlined, InboxOutlined, CommentOutlined } from '@ant-design/icons';
import Logger from '../utils/logger';
import { safeJsonParse } from '../utils/jsonUtils';
import api from '../utils/api';
import CommentSection from '../components/CommentSection';
import BackButton from '../components/BackButton';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { Panel } = Collapse;
const { Dragger } = Upload;

const TestCasePage = () => {
  const [cases, setCases] = useState([]);
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [form] = Form.useForm();
  
  // 数据驱动相关状态
  const [dataFileInfo, setDataFileInfo] = useState(null);
  const [fileUploadLoading, setFileUploadLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [previewVisible, setPreviewVisible] = useState(false);

  // 评论相关状态
  const [commentDrawerVisible, setCommentDrawerVisible] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);

  // 处理评论
  const handleComment = (record) => {
    setSelectedCase(record);
    setCommentDrawerVisible(true);
  };

  const fetchCases = useCallback(async () => {
    try {
      Logger.info('Fetching test cases...');
      const response = await api.get('/api-test/api-test-cases/');
      Logger.debug('Test cases response:', response.data);
      setCases(Array.isArray(response.data) ? response.data : []);
      setLoading(false);
    } catch (error) {
      Logger.errorWithContext('fetchCases', error);
      setLoading(false);
    }
  }, []);

  const fetchApis = useCallback(async () => {
    try {
      Logger.info('Fetching APIs...');
      const response = await api.get('/api-test/api-definitions/');
      Logger.debug('APIs response:', response.data);
      setApis(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      Logger.errorWithContext('fetchApis', error);
    }
  }, []);

  useEffect(() => {
    fetchCases();
    fetchApis();
  }, [fetchCases, fetchApis]);

  const handleAdd = useCallback(() => {
    Logger.info('Opening add test case modal');
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
  }, [form]);

  const fetchDataFileInfo = useCallback(async (testCaseId) => {
    try {
      const response = await api.get(`/testcases/testcases/${testCaseId}/datafile_info/`);
      setDataFileInfo(response.data);
    } catch (error) {
      if (error.response?.status !== 404) {
        Logger.errorWithContext('fetchDataFileInfo', error);
      }
      setDataFileInfo(null);
    }
  }, []);

  const handleEdit = useCallback((record) => {
    Logger.info('Opening edit test case modal', { id: record.id });
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
    
    // 加载数据文件信息
    fetchDataFileInfo(record.id);
    
    setModalVisible(true);
  }, [form, fetchDataFileInfo]);

  // 上传数据文件
  const handleFileUpload = useCallback(async (file, fileType) => {
    if (!editingCase) {
      message.error('请先选择要编辑的测试用例');
      return false;
    }

    setFileUploadLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    formData.append('name', file.name);
    formData.append('description', `${editingCase.name}的测试数据文件`);

    try {
      const response = await api.post(
        `/testcases/testcases/${editingCase.id}/datafile/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      setDataFileInfo(response.data);
      message.success('数据文件上传成功');
    } catch (error) {
      Logger.errorWithContext('handleFileUpload', error);
      message.error(`上传失败: ${error.response?.data?.file?.[0] || error.message}`);
    } finally {
      setFileUploadLoading(false);
    }
    
    return false; // 阻止默认上传行为
  }, [editingCase]);

  // 删除数据文件
  const handleDeleteDataFile = useCallback(async () => {
    if (!editingCase || !dataFileInfo) return;

    try {
      await api.delete(`/testcases/testcases/${editingCase.id}/datafile_delete/`);
      setDataFileInfo(null);
      setPreviewData(null);
      message.success('数据文件删除成功');
    } catch (error) {
      Logger.errorWithContext('handleDeleteDataFile', error);
      message.error('删除数据文件失败');
    }
  }, [editingCase, dataFileInfo]);

  // 预览数据文件
  const handlePreviewDataFile = useCallback(async () => {
    if (!editingCase || !dataFileInfo) return;

    try {
      const response = await api.get(`/testcases/testcases/${editingCase.id}/datafile_preview/?rows=10`);
      setPreviewData(response.data);
      setPreviewVisible(true);
    } catch (error) {
      Logger.errorWithContext('handlePreviewDataFile', error);
      message.error('预览数据文件失败');
    }
  }, [editingCase, dataFileInfo]);

  const handleDelete = useCallback(async (id) => {
    if (window.confirm('确定要删除这个测试用例吗？')) {
      try {
        Logger.info('Deleting test case', { id });
        await api.delete(`/api-test/api-test-cases/${id}/`);
        fetchCases();
        message.success('测试用例删除成功');
      } catch (error) {
        Logger.errorWithContext('handleDelete', error);
        message.error('删除测试用例失败');
      }
    }
  }, [fetchCases]);

  const handleExecute = useCallback(async (id) => {
    try {
      Logger.info('Executing test case', { id });
      const response = await api.post(`/api-test/api-test-cases/${id}/execute/`);
      message.success(`测试执行成功: ${response.data.status}`);
      fetchCases(); // 刷新列表以显示最新状态
    } catch (error) {
      Logger.errorWithContext('handleExecute', error);
      message.error('执行测试用例失败');
    }
  }, [fetchCases]);

  const handleModalOk = useCallback(async () => {
    try {
      const values = await form.validateFields();
      Logger.formData('TestCaseForm', values);

      // 使用安全的JSON解析函数
      const submitValues = {
        ...values,
        headers: safeJsonParse(values.headers, {}, 'headers'),
        params: safeJsonParse(values.params, {}, 'params'),
        body: safeJsonParse(values.body, {}, 'body'),
        assertions: safeJsonParse(values.assertions, [], 'assertions'),
        variables: safeJsonParse(values.variables, {}, 'variables'),
      };

      Logger.debug('Submit values:', submitValues);

      if (editingCase) {
        Logger.info('Updating test case', { id: editingCase.id });
        await api.put(`/api-test/api-test-cases/${editingCase.id}/`, submitValues);
        message.success('测试用例更新成功');
      } else {
        Logger.info('Creating new test case');
        await api.post('/api-test/api-test-cases/', submitValues);
        message.success('测试用例创建成功');
      }
      setModalVisible(false);
      fetchCases();
    } catch (error) {
      Logger.errorWithContext('handleModalOk', error);
      
      // 更详细的错误处理
      if (error.message && error.message.includes('JSON格式错误')) {
        message.error(error.message);
      } else if (error.response?.data) {
        message.error(`服务器错误: ${JSON.stringify(error.response.data)}`);
      } else {
        message.error('保存测试用例失败');
      }
    }
  }, [form, editingCase, fetchCases]);

  const handleModalCancel = useCallback(() => {
    setModalVisible(false);
    setDataFileInfo(null);
    setPreviewData(null);
    setPreviewVisible(false);
  }, []);

  const columns = useMemo(() => [
    {
      title: '名称',
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
      title: '状态码',
      dataIndex: 'expected_status_code',
      key: 'expected_status_code',
    },
    {
      title: '最大响应时间',
      dataIndex: 'max_response_time',
      key: 'max_response_time',
      render: (time) => time ? `${time}ms` : '-',
    },
    {
      title: '启用状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active) => (
        <Tag color={active ? 'green' : 'red'}>
          {active ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '数据驱动',
      key: 'data_driven',
      render: (text, record) => (
        <Tag color={record.data_file ? 'blue' : 'default'}>
          {record.data_file ? '已配置' : '未配置'}
        </Tag>
      ),
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
      render: (text, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleEdit(record)}>编辑</Button>
          <Button type="link" onClick={() => handleExecute(record.id)}>执行</Button>
          <Button 
            type="link" 
            icon={<CommentOutlined />} 
            onClick={() => handleComment(record)}
          >
            讨论
          </Button>
          <Button type="link" danger onClick={() => handleDelete(record.id)}>删除</Button>
        </Space>
      ),
    },
  ], [apis, handleEdit, handleExecute, handleDelete, handleComment]);

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#fff' }}>
      <BackButton />
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>API 测试用例</Title>
        <Button type="primary" onClick={handleAdd} style={{ marginBottom: '20px' }}>
          添加新测试用例
        </Button>
        <Table 
          columns={columns} 
          dataSource={cases} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }}
        />

        <Modal
          title={editingCase ? '编辑测试用例' : '添加新测试用例'}
          visible={modalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          width={900}
          destroyOnClose
        >
          <Tabs defaultActiveKey="basic">
            <TabPane tab="基本配置" key="basic">
              <Form
                form={form}
                layout="vertical"
              >
                <Form.Item
                  name="name"
                  label="名称"
                  rules={[{ required: true, message: '请输入测试用例名称' }]}
                >
                  <Input />
                </Form.Item>
                
                <Form.Item
                  name="api"
                  label="API定义"
                  rules={[{ required: true, message: '请选择API定义' }]}
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
                  label="预期状态码"
                  rules={[{ required: true, message: '请输入预期状态码' }]}
                >
                  <InputNumber min={100} max={599} />
                </Form.Item>

                <Form.Item
                  name="max_response_time"
                  label="最大响应时间 (毫秒)"
                >
                  <InputNumber min={1} />
                </Form.Item>

                <Form.Item
                  name="is_active"
                  label="启用状态"
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>

                <Form.Item
                  name="headers"
                  label="请求头 (JSON)"
                  help="覆盖API定义的请求头"
                >
                  <TextArea rows={3} />
                </Form.Item>

                <Form.Item
                  name="params"
                  label="参数 (JSON)"
                  help="覆盖API定义的参数"
                >
                  <TextArea rows={3} />
                </Form.Item>

                <Form.Item
                  name="body"
                  label="请求体 (JSON)"
                  help="覆盖API定义的请求体"
                >
                  <TextArea rows={3} />
                </Form.Item>

                <Form.Item
                  name="assertions"
                  label="断言 (JSON数组)"
                  help="定义测试断言"
                >
                  <TextArea rows={4} />
                </Form.Item>

                <Form.Item
                  name="variables"
                  label="变量 (JSON)"
                  help="定义测试变量"
                >
                  <TextArea rows={3} />
                </Form.Item>

                <Form.Item
                  name="description"
                  label="描述"
                >
                  <TextArea rows={2} />
                </Form.Item>
              </Form>
            </TabPane>
            
            {editingCase && (
              <TabPane tab="数据驱动" key="datafile">
                <div style={{ padding: '16px 0' }}>
                  {dataFileInfo ? (
                    <div>
                      <Alert
                        message="数据文件已配置"
                        description={
                          <div>
                            <p><strong>文件名:</strong> {dataFileInfo.name}</p>
                            <p><strong>文件类型:</strong> {dataFileInfo.file_type?.toUpperCase()}</p>
                            <p><strong>文件大小:</strong> {dataFileInfo.file_size}</p>
                            <p><strong>数据行数:</strong> {dataFileInfo.data_count}</p>
                            <p><strong>创建时间:</strong> {new Date(dataFileInfo.created_at).toLocaleString()}</p>
                          </div>
                        }
                        type="success"
                        style={{ marginBottom: 16 }}
                        action={
                          <Space>
                            <Button size="small" icon={<EyeOutlined />} onClick={handlePreviewDataFile}>
                              预览
                            </Button>
                            <Button size="small" danger icon={<DeleteOutlined />} onClick={handleDeleteDataFile}>
                              删除
                            </Button>
                          </Space>
                        }
                      />
                    </div>
                  ) : (
                    <div>
                      <Alert
                        message="数据驱动功能说明"
                        description={
                          <div>
                            <p>上传CSV或JSON格式的测试数据文件，测试执行时将自动遍历数据文件中的每一行进行测试。</p>
                            <p><strong>CSV格式:</strong> 第一行为表头（变量名），后续行为数据值</p>
                            <p><strong>JSON格式:</strong> 对象数组，每个对象的键为变量名，值为数据值</p>
                            <p><strong>变量使用:</strong> 在测试用例中使用 {`{变量名}`} 格式引用数据文件中的变量</p>
                          </div>
                        }
                        type="info"
                        style={{ marginBottom: 16 }}
                      />
                      
                      <Collapse>
                        <Panel header="上传CSV数据文件" key="csv">
                          <Dragger
                            accept=".csv"
                            beforeUpload={(file) => handleFileUpload(file, 'csv')}
                            showUploadList={false}
                            loading={fileUploadLoading}
                          >
                            <p className="ant-upload-drag-icon">
                              <InboxOutlined />
                            </p>
                            <p className="ant-upload-text">点击或拖拽CSV文件到此区域上传</p>
                            <p className="ant-upload-hint">仅支持.csv格式文件，文件大小不超过10MB</p>
                          </Dragger>
                        </Panel>
                        
                        <Panel header="上传JSON数据文件" key="json">
                          <Dragger
                            accept=".json"
                            beforeUpload={(file) => handleFileUpload(file, 'json')}
                            showUploadList={false}
                            loading={fileUploadLoading}
                          >
                            <p className="ant-upload-drag-icon">
                              <InboxOutlined />
                            </p>
                            <p className="ant-upload-text">点击或拖拽JSON文件到此区域上传</p>
                            <p className="ant-upload-hint">仅支持.json格式文件，文件大小不超过10MB</p>
                          </Dragger>
                        </Panel>
                      </Collapse>
                    </div>
                  )}
                </div>
              </TabPane>
            )}
          </Tabs>
        </Modal>

        {/* 数据预览模态框 */}
        <Modal
          title="数据文件预览"
          visible={previewVisible}
          onCancel={() => setPreviewVisible(false)}
          footer={[
            <Button key="close" onClick={() => setPreviewVisible(false)}>
              关闭
            </Button>
          ]}
          width={800}
        >
          {previewData && (
            <div>
              <Alert
                message={`显示前${previewData.preview_rows}行数据，共${previewData.file_info?.total_rows || 0}行`}
                type="info"
                style={{ marginBottom: 16 }}
              />
              <Table
                columns={previewData.preview?.headers?.map(header => ({
                  title: header,
                  dataIndex: header,
                  key: header,
                  ellipsis: true,
                  width: 150
                }))}
                dataSource={previewData.preview?.rows?.map((row, index) => {
                  const record = { key: index };
                  previewData.preview.headers.forEach((header, i) => {
                    record[header] = row[i] || '';
                  });
                  return record;
                })}
                pagination={false}
                scroll={{ x: true }}
                size="small"
              />
            </div>
          )}
        </Modal>

        {/* 评论抽屉 */}
        <Drawer
          title={selectedCase ? `测试用例讨论: ${selectedCase.name}` : '测试用例讨论'}
          placement="right"
          width={600}
          onClose={() => setCommentDrawerVisible(false)}
          visible={commentDrawerVisible}
          destroyOnClose
        >
          {selectedCase && (
            <CommentSection
              targetType="testcase"
              targetId={selectedCase.id}
              currentUser={JSON.parse(localStorage.getItem('user') || 'null')}
            />
          )}
        </Drawer>
      </div>
    </div>
  );
};

export default TestCasePage;