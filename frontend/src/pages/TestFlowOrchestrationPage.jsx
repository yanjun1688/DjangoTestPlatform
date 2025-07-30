import { useState, useEffect, useCallback } from 'react';
import { 
  Card, Button, Modal, Form, Input, Select, Space, message, 
  Tree, Drawer, Steps, Timeline, Tag, Tabs, Collapse,
  Row, Col, Tooltip, Popconfirm, Alert, Divider, Switch
} from 'antd';
import { 
  PlusOutlined, PlayCircleOutlined, EditOutlined, DeleteOutlined,
  SettingOutlined, BranchesOutlined, LinkOutlined, SaveOutlined,
  CopyOutlined, ExportOutlined, ImportOutlined, ApiOutlined,
  ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined,
  ArrowRightOutlined, NodeIndexOutlined, ApartmentOutlined,
  ThunderboltOutlined, BugOutlined, EyeOutlined, WarningOutlined
} from '@ant-design/icons';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import api from '../utils/api';
import Logger from '../utils/logger';
import BackButton from '../components/BackButton';

const { Option } = Select;
const { TextArea } = Input;
const { Step } = Steps;
const { TabPane } = Tabs;
const { Panel } = Collapse;

const TestFlowOrchestrationPage = () => {
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [environments, setEnvironments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState(null);
  const [form] = Form.useForm();
  const [activeTab, setActiveTab] = useState('designer');
  const [executionHistory, setExecutionHistory] = useState([]);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState(null);

  useEffect(() => {
    loadWorkflows();
    loadTestCases();
    loadEnvironments();
  }, []);

  const loadWorkflows = async () => {
    try {
      // 模拟获取工作流数据
      const mockWorkflows = [
        {
          id: 1,
          name: '用户注册登录流程',
          description: '包含用户注册、邮箱验证、登录验证的完整流程',
          steps: [
            { id: 1, type: 'api_test', name: '用户注册', testCaseId: 1, order: 1 },
            { id: 2, type: 'delay', name: '等待1秒', duration: 1000, order: 2 },
            { id: 3, type: 'api_test', name: '邮箱验证', testCaseId: 2, order: 3 },
            { id: 4, type: 'api_test', name: '用户登录', testCaseId: 3, order: 4 },
            { id: 5, type: 'condition', name: '检查登录状态', condition: 'response.status === 200', order: 5 }
          ],
          status: 'active',
          createdAt: '2024-01-15T10:00:00Z',
          lastExecuted: '2024-01-16T14:30:00Z'
        },
        {
          id: 2,
          name: '商品购买流程',
          description: '模拟用户浏览商品、添加购物车、结算支付的完整业务流程',
          steps: [
            { id: 1, type: 'api_test', name: '获取商品列表', testCaseId: 4, order: 1 },
            { id: 2, type: 'api_test', name: '查看商品详情', testCaseId: 5, order: 2 },
            { id: 3, type: 'api_test', name: '添加到购物车', testCaseId: 6, order: 3 },
            { id: 4, type: 'api_test', name: '结算订单', testCaseId: 7, order: 4 },
            { id: 5, type: 'api_test', name: '支付订单', testCaseId: 8, order: 5 }
          ],
          status: 'active',
          createdAt: '2024-01-14T09:00:00Z',
          lastExecuted: '2024-01-16T16:45:00Z'
        }
      ];
      setWorkflows(mockWorkflows);
    } catch (error) {
      Logger.errorWithContext('loadWorkflows', error);
    }
  };

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
    } catch (error) {
      Logger.errorWithContext('loadEnvironments', error);
    }
  };

  const handleCreateWorkflow = () => {
    setEditingWorkflow(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditWorkflow = (workflow) => {
    setEditingWorkflow(workflow);
    form.setFieldsValue({
      name: workflow.name,
      description: workflow.description,
      status: workflow.status
    });
    setModalVisible(true);
  };

  const handleDeleteWorkflow = async (workflowId) => {
    try {
      // 模拟删除工作流
      setWorkflows(workflows.filter(w => w.id !== workflowId));
      message.success('工作流删除成功');
    } catch (error) {
      Logger.errorWithContext('handleDeleteWorkflow', error);
      message.error('删除工作流失败');
    }
  };

  const handleSaveWorkflow = async () => {
    try {
      const values = await form.validateFields();
      
      if (editingWorkflow) {
        // 更新工作流
        const updatedWorkflows = workflows.map(w => 
          w.id === editingWorkflow.id ? { ...w, ...values } : w
        );
        setWorkflows(updatedWorkflows);
        message.success('工作流更新成功');
      } else {
        // 创建新工作流
        const newWorkflow = {
          id: Date.now(),
          ...values,
          steps: [],
          createdAt: new Date().toISOString(),
          lastExecuted: null
        };
        setWorkflows([...workflows, newWorkflow]);
        message.success('工作流创建成功');
      }
      
      setModalVisible(false);
    } catch (error) {
      Logger.errorWithContext('handleSaveWorkflow', error);
      message.error('保存工作流失败');
    }
  };

  const handleExecuteWorkflow = async (workflow) => {
    try {
      setLoading(true);
      
      // 模拟执行工作流
      const execution = {
        id: Date.now(),
        workflowId: workflow.id,
        workflowName: workflow.name,
        startTime: new Date().toISOString(),
        status: 'running',
        steps: workflow.steps.map(step => ({
          ...step,
          status: 'pending',
          startTime: null,
          endTime: null,
          result: null
        }))
      };
      
      setExecutionHistory([execution, ...executionHistory]);
      
      // 模拟步骤执行
      for (let i = 0; i < workflow.steps.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        const updatedExecution = {
          ...execution,
          steps: execution.steps.map((step, index) => {
            if (index === i) {
              return {
                ...step,
                status: Math.random() > 0.1 ? 'passed' : 'failed',
                startTime: new Date().toISOString(),
                endTime: new Date().toISOString(),
                result: Math.random() > 0.1 ? { responseTime: Math.random() * 500 + 100 } : { error: '模拟错误' }
              };
            }
            return step;
          })
        };
        
        setExecutionHistory(prev => 
          prev.map(exec => exec.id === execution.id ? updatedExecution : exec)
        );
      }
      
      const finalExecution = {
        ...execution,
        status: 'completed',
        endTime: new Date().toISOString(),
        steps: execution.steps.map(step => ({
          ...step,
          status: Math.random() > 0.1 ? 'passed' : 'failed',
          startTime: new Date().toISOString(),
          endTime: new Date().toISOString(),
          result: Math.random() > 0.1 ? { responseTime: Math.random() * 500 + 100 } : { error: '模拟错误' }
        }))
      };
      
      setExecutionHistory(prev => 
        prev.map(exec => exec.id === execution.id ? finalExecution : exec)
      );
      
      message.success('工作流执行完成');
    } catch (error) {
      Logger.errorWithContext('handleExecuteWorkflow', error);
      message.error('执行工作流失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination || !selectedWorkflow) return;

    const newSteps = Array.from(selectedWorkflow.steps);
    const [reorderedStep] = newSteps.splice(result.source.index, 1);
    newSteps.splice(result.destination.index, 0, reorderedStep);

    const updatedWorkflow = {
      ...selectedWorkflow,
      steps: newSteps.map((step, index) => ({ ...step, order: index + 1 }))
    };

    setSelectedWorkflow(updatedWorkflow);
    setWorkflows(workflows.map(w => 
      w.id === selectedWorkflow.id ? updatedWorkflow : w
    ));
  };

  const renderWorkflowList = () => {
    return (
      <div style={{ padding: '24px' }}>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
          <h2>测试流程编排</h2>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={handleCreateWorkflow}
          >
            创建工作流
          </Button>
        </div>

        <Row gutter={[16, 16]}>
          {workflows.map(workflow => (
            <Col xs={24} sm={12} lg={8} key={workflow.id}>
              <Card
                hoverable
                style={{ borderRadius: '12px' }}
                actions={[
                  <Tooltip title="编辑">
                    <EditOutlined onClick={() => handleEditWorkflow(workflow)} />
                  </Tooltip>,
                  <Tooltip title="执行">
                    <PlayCircleOutlined onClick={() => handleExecuteWorkflow(workflow)} />
                  </Tooltip>,
                  <Tooltip title="设计">
                    <SettingOutlined onClick={() => setSelectedWorkflow(workflow)} />
                  </Tooltip>,
                  <Popconfirm
                    title="确定删除这个工作流？"
                    onConfirm={() => handleDeleteWorkflow(workflow.id)}
                  >
                    <Tooltip title="删除">
                      <DeleteOutlined style={{ color: '#ff4d4f' }} />
                    </Tooltip>
                  </Popconfirm>
                ]}
              >
                <div style={{ marginBottom: '12px' }}>
                  <h3 style={{ margin: 0, marginBottom: '8px' }}>
                    <ApartmentOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                    {workflow.name}
                  </h3>
                  <Tag color={workflow.status === 'active' ? 'green' : 'red'}>
                    {workflow.status === 'active' ? '活跃' : '暂停'}
                  </Tag>
                </div>
                <p style={{ color: '#666', marginBottom: '12px' }}>{workflow.description}</p>
                <div style={{ fontSize: '12px', color: '#999' }}>
                  <div>步骤数: {workflow.steps.length}</div>
                  <div>创建时间: {new Date(workflow.createdAt).toLocaleDateString()}</div>
                  {workflow.lastExecuted && (
                    <div>最后执行: {new Date(workflow.lastExecuted).toLocaleString()}</div>
                  )}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    );
  };

  const renderWorkflowDesigner = () => {
    if (!selectedWorkflow) {
      return (
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '400px',
          color: '#999'
        }}>
          <div style={{ textAlign: 'center' }}>
            <ApartmentOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>请选择一个工作流进行设计</div>
          </div>
        </div>
      );
    }

    const getStepIcon = (type) => {
      switch (type) {
        case 'api_test':
          return <ApiOutlined style={{ color: '#1890ff' }} />;
        case 'delay':
          return <ClockCircleOutlined style={{ color: '#faad14' }} />;
        case 'condition':
          return <BranchesOutlined style={{ color: '#722ed1' }} />;
        default:
          return <NodeIndexOutlined />;
      }
    };

    const getStepColor = (type) => {
      switch (type) {
        case 'api_test':
          return '#1890ff';
        case 'delay':
          return '#faad14';
        case 'condition':
          return '#722ed1';
        default:
          return '#666';
      }
    };

    return (
      <div style={{ padding: '24px' }}>
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
          <h3>
            <ApartmentOutlined style={{ marginRight: '8px' }} />
            {selectedWorkflow.name} - 流程设计
          </h3>
          <Space>
            <Button 
              icon={<PlusOutlined />}
              onClick={() => {
                // 添加步骤的逻辑
                const newStep = {
                  id: Date.now(),
                  type: 'api_test',
                  name: '新建步骤',
                  testCaseId: null,
                  order: selectedWorkflow.steps.length + 1
                };
                
                const updatedWorkflow = {
                  ...selectedWorkflow,
                  steps: [...selectedWorkflow.steps, newStep]
                };
                
                setSelectedWorkflow(updatedWorkflow);
                setWorkflows(workflows.map(w => 
                  w.id === selectedWorkflow.id ? updatedWorkflow : w
                ));
              }}
            >
              添加步骤
            </Button>
            <Button 
              type="primary" 
              icon={<SaveOutlined />}
              onClick={() => {
                message.success('工作流保存成功');
              }}
            >
              保存设计
            </Button>
          </Space>
        </div>

        <Card style={{ borderRadius: '12px' }}>
          <DragDropContext onDragEnd={handleDragEnd}>
            <Droppable droppableId="workflow-steps">
              {(provided) => (
                <div {...provided.droppableProps} ref={provided.innerRef}>
                  {selectedWorkflow.steps.map((step, index) => (
                    <Draggable key={step.id} draggableId={step.id.toString()} index={index}>
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          style={{
                            marginBottom: '8px',
                            ...provided.draggableProps.style,
                          }}
                        >
                          <Card
                            size="small"
                            style={{ 
                              border: `2px solid ${getStepColor(step.type)}`,
                              borderRadius: '8px',
                              backgroundColor: '#fafafa'
                            }}
                            bodyStyle={{ padding: '12px' }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <div style={{ display: 'flex', alignItems: 'center' }}>
                                <div style={{ 
                                  marginRight: '12px',
                                  width: '32px',
                                  height: '32px',
                                  borderRadius: '50%',
                                  backgroundColor: getStepColor(step.type),
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  color: '#fff',
                                  fontSize: '16px'
                                }}>
                                  {index + 1}
                                </div>
                                <div>
                                  <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                                    {getStepIcon(step.type)}
                                    <span style={{ marginLeft: '8px' }}>{step.name}</span>
                                  </div>
                                  <div style={{ fontSize: '12px', color: '#666' }}>
                                    {step.type === 'api_test' && step.testCaseId && (
                                      <span>测试用例: {testCases.find(tc => tc.id === step.testCaseId)?.name || '未知'}</span>
                                    )}
                                    {step.type === 'delay' && (
                                      <span>等待时间: {step.duration}ms</span>
                                    )}
                                    {step.type === 'condition' && (
                                      <span>条件: {step.condition}</span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              <div>
                                <Space>
                                  <Button 
                                    type="text" 
                                    size="small" 
                                    icon={<EditOutlined />}
                                    onClick={() => {
                                      // 编辑步骤的逻辑
                                      console.log('Edit step:', step);
                                    }}
                                  />
                                  <Button 
                                    type="text" 
                                    size="small" 
                                    icon={<DeleteOutlined />}
                                    style={{ color: '#ff4d4f' }}
                                    onClick={() => {
                                      const updatedWorkflow = {
                                        ...selectedWorkflow,
                                        steps: selectedWorkflow.steps.filter(s => s.id !== step.id)
                                      };
                                      setSelectedWorkflow(updatedWorkflow);
                                      setWorkflows(workflows.map(w => 
                                        w.id === selectedWorkflow.id ? updatedWorkflow : w
                                      ));
                                    }}
                                  />
                                </Space>
                              </div>
                            </div>
                          </Card>
                          {index < selectedWorkflow.steps.length - 1 && (
                            <div style={{ 
                              textAlign: 'center', 
                              margin: '8px 0',
                              color: '#1890ff'
                            }}>
                              <ArrowRightOutlined style={{ fontSize: '16px' }} />
                            </div>
                          )}
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </Card>
      </div>
    );
  };

  const renderExecutionHistory = () => {
    return (
      <div style={{ padding: '24px' }}>
        <h3>
          <ClockCircleOutlined style={{ marginRight: '8px' }} />
          执行历史
        </h3>
        
        <div style={{ marginBottom: '16px' }}>
          {executionHistory.map(execution => (
            <Card 
              key={execution.id}
              style={{ marginBottom: '12px', borderRadius: '8px' }}
              size="small"
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                    {execution.workflowName}
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    开始时间: {new Date(execution.startTime).toLocaleString()}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <Tag color={
                    execution.status === 'running' ? 'blue' :
                    execution.status === 'completed' ? 'green' : 'red'
                  }>
                    {execution.status === 'running' ? '执行中' :
                     execution.status === 'completed' ? '已完成' : '失败'}
                  </Tag>
                  <Button 
                    type="link" 
                    size="small"
                    icon={<EyeOutlined />}
                    onClick={() => {
                      setSelectedExecution(execution);
                      setDetailDrawerVisible(true);
                    }}
                  >
                    查看详情
                  </Button>
                </div>
              </div>
              
              <div style={{ marginTop: '12px' }}>
                <Steps 
                  size="small"
                  current={execution.steps.findIndex(step => step.status === 'pending')}
                  status={execution.status === 'running' ? 'process' : 'finish'}
                >
                  {execution.steps.map((step, index) => (
                    <Step 
                      key={step.id}
                      title={step.name}
                      status={
                        step.status === 'passed' ? 'finish' :
                        step.status === 'failed' ? 'error' :
                        step.status === 'running' ? 'process' : 'wait'
                      }
                      icon={
                        step.status === 'passed' ? <CheckCircleOutlined /> :
                        step.status === 'failed' ? <CloseCircleOutlined /> :
                        step.status === 'running' ? <ThunderboltOutlined /> : undefined
                      }
                    />
                  ))}
                </Steps>
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div style={{ background: '#f5f5f5', minHeight: '100vh' }}>
      <BackButton />
      {selectedWorkflow ? (
        <Tabs activeKey={activeTab} onChange={setActiveTab}>
          <TabPane tab={<><BranchesOutlined />工作流列表</>} key="list">
            {renderWorkflowList()}
          </TabPane>
          <TabPane tab={<><SettingOutlined />流程设计</>} key="designer">
            {renderWorkflowDesigner()}
          </TabPane>
          <TabPane tab={<><ClockCircleOutlined />执行历史</>} key="history">
            {renderExecutionHistory()}
          </TabPane>
        </Tabs>
      ) : (
        renderWorkflowList()
      )}

      {/* 创建/编辑工作流模态框 */}
      <Modal
        title={editingWorkflow ? '编辑工作流' : '创建工作流'}
        visible={modalVisible}
        onOk={handleSaveWorkflow}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="工作流名称"
            rules={[{ required: true, message: '请输入工作流名称' }]}
          >
            <Input placeholder="如：用户注册登录流程" />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
            rules={[{ required: true, message: '请输入工作流描述' }]}
          >
            <TextArea rows={3} placeholder="描述这个工作流的用途和包含的步骤" />
          </Form.Item>
          <Form.Item
            name="status"
            label="状态"
            initialValue="active"
          >
            <Select>
              <Option value="active">活跃</Option>
              <Option value="inactive">暂停</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 执行详情抽屉 */}
      <Drawer
        title="执行详情"
        placement="right"
        width={600}
        onClose={() => setDetailDrawerVisible(false)}
        visible={detailDrawerVisible}
      >
        {selectedExecution && (
          <div>
            <div style={{ marginBottom: '16px' }}>
              <h3>{selectedExecution.workflowName}</h3>
              <Tag color={
                selectedExecution.status === 'running' ? 'blue' :
                selectedExecution.status === 'completed' ? 'green' : 'red'
              }>
                {selectedExecution.status === 'running' ? '执行中' :
                 selectedExecution.status === 'completed' ? '已完成' : '失败'}
              </Tag>
            </div>
            
            <Divider />
            
            <div style={{ marginBottom: '16px' }}>
              <div style={{ marginBottom: '8px' }}>
                <strong>开始时间:</strong> {new Date(selectedExecution.startTime).toLocaleString()}
              </div>
              {selectedExecution.endTime && (
                <div>
                  <strong>结束时间:</strong> {new Date(selectedExecution.endTime).toLocaleString()}
                </div>
              )}
            </div>
            
            <Divider />
            
            <h4>步骤执行详情</h4>
            <Timeline>
              {selectedExecution.steps.map((step, index) => (
                <Timeline.Item
                  key={step.id}
                  dot={
                    step.status === 'passed' ? <CheckCircleOutlined style={{ color: '#52c41a' }} /> :
                    step.status === 'failed' ? <CloseCircleOutlined style={{ color: '#ff4d4f' }} /> :
                    step.status === 'running' ? <ThunderboltOutlined style={{ color: '#1890ff' }} /> :
                    <ClockCircleOutlined style={{ color: '#d9d9d9' }} />
                  }
                  color={
                    step.status === 'passed' ? 'green' :
                    step.status === 'failed' ? 'red' :
                    step.status === 'running' ? 'blue' : 'gray'
                  }
                >
                  <div style={{ marginBottom: '8px' }}>
                    <strong>{step.name}</strong>
                    <Tag 
                      color={
                        step.status === 'passed' ? 'green' :
                        step.status === 'failed' ? 'red' :
                        step.status === 'running' ? 'blue' : 'default'
                      }
                      style={{ marginLeft: '8px' }}
                    >
                      {step.status === 'passed' ? '成功' :
                       step.status === 'failed' ? '失败' :
                       step.status === 'running' ? '执行中' : '等待'}
                    </Tag>
                  </div>
                  {step.result && (
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {step.result.responseTime && (
                        <div>响应时间: {step.result.responseTime.toFixed(2)}ms</div>
                      )}
                      {step.result.error && (
                        <div style={{ color: '#ff4d4f' }}>错误: {step.result.error}</div>
                      )}
                    </div>
                  )}
                </Timeline.Item>
              ))}
            </Timeline>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default TestFlowOrchestrationPage;