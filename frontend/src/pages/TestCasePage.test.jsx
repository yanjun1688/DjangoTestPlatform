import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { message } from 'antd';
import TestCasePage from './TestCasePage';

// Mock axios
vi.mock('axios');

// Mock Ant Design's message component
vi.mock('antd', async (importOriginal) => {
  const antd = await importOriginal();
  return {
    ...antd,
    message: {
      ...antd.message,
      error: vi.fn(),
      success: vi.fn(),
    },
  };
});

// Mock window.confirm
const mockConfirm = vi.fn();
vi.stubGlobal('confirm', mockConfirm);

describe('TestCasePage', () => {
  const mockTestCases = [
    {
      id: 1,
      title: 'Login Test Case',
      description: 'Test user login functionality',
      precondition: 'User must be registered',
      status: 'blocked',
      priority: 'P1',
      module: 'Authentication',
      tags: 'login,auth',
      version: 'v1.0',
      assignee: 1,
      requirement_link: 'REQ-001',
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      title: 'Logout Test Case',
      description: 'Test user logout functionality',
      precondition: 'User must be logged in',
      status: 'passed',
      priority: 'P2',
      module: 'Authentication',
      tags: 'logout,auth',
      version: 'v1.0',
      assignee: 1,
      requirement_link: 'REQ-002',
      created_at: new Date().toISOString(),
    },
  ];

  beforeEach(() => {
    // Reset mocks before each test
    axios.get.mockClear();
    axios.post.mockClear();
    axios.put.mockClear();
    axios.delete.mockClear();
    message.error.mockClear();
    message.success.mockClear();
    mockConfirm.mockClear();
    axios.get.mockResolvedValue({ data: mockTestCases });
  });

  it('renders the component and fetches test cases successfully', async () => {
    render(<TestCasePage />);

    expect(screen.getByText('测试用例管理')).toBeInTheDocument();
    expect(axios.get).toHaveBeenCalledWith('/testcases/testcases/');

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
      expect(screen.getByText('Logout Test Case')).toBeInTheDocument();
      expect(screen.getByText('Authentication')).toBeInTheDocument();
    });
    expect(message.error).not.toHaveBeenCalled();
  });

  it('shows an error message when fetching test cases fails', async () => {
    axios.get.mockRejectedValue(new Error('Network Error'));

    render(<TestCasePage />);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith('获取测试用例失败');
    });
    expect(screen.queryByText('Login Test Case')).not.toBeInTheDocument();
  });

  it('opens the add test case modal and allows adding a new test case', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增测试用例' }));

    expect(screen.getByText('新增测试用例')).toBeInTheDocument();

    const newTestCase = {
      title: 'New Test Case',
      description: 'A new test case for testing',
      precondition: 'System must be running',
      status: 'blocked',
      priority: 'P1',
      module: 'Test Module',
      tags: 'test,new',
      version: 'v1.0',
      requirement_link: 'REQ-003',
    };

    fireEvent.change(screen.getByLabelText('用例标题'), { target: { value: newTestCase.title } });
    fireEvent.change(screen.getByLabelText('前置条件'), { target: { value: newTestCase.precondition } });
    fireEvent.change(screen.getByLabelText('用例描述'), { target: { value: newTestCase.description } });
    fireEvent.change(screen.getByLabelText('所属模块'), { target: { value: newTestCase.module } });
    fireEvent.change(screen.getByLabelText('标签'), { target: { value: newTestCase.tags } });
    fireEvent.change(screen.getByLabelText('版本'), { target: { value: newTestCase.version } });
    fireEvent.change(screen.getByLabelText('需求链接'), { target: { value: newTestCase.requirement_link } });

    axios.post.mockResolvedValue({ data: { id: 3, ...newTestCase, created_at: new Date().toISOString() } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/testcases/testcases/', newTestCase);
      expect(message.success).toHaveBeenCalledWith('创建成功');
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  it('opens the edit test case modal and allows editing an existing test case', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: '编辑' });
    fireEvent.click(editButtons[0]);

    expect(screen.getByText('编辑测试用例')).toBeInTheDocument();
    expect(screen.getByLabelText('用例标题')).toHaveValue('Login Test Case');

    const updatedTitle = 'Updated Login Test Case';
    fireEvent.change(screen.getByLabelText('用例标题'), { target: { value: updatedTitle } });

    axios.put.mockResolvedValue({ data: { ...mockTestCases[0], title: updatedTitle } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.put).toHaveBeenCalledWith(`/testcases/testcases/${mockTestCases[0].id}/`, {
        ...mockTestCases[0],
        title: updatedTitle,
      });
      expect(message.success).toHaveBeenCalledWith('更新成功');
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  it('allows deleting a test case', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(true);
    axios.delete.mockResolvedValue({});

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个测试用例吗？');
      expect(axios.delete).toHaveBeenCalledWith(`/testcases/testcases/${mockTestCases[0].id}/`);
      expect(message.success).toHaveBeenCalledWith('删除成功');
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  it('does not delete a test case if confirmation is cancelled', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(false);

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个测试用例吗？');
      expect(axios.delete).not.toHaveBeenCalled();
      expect(message.success).not.toHaveBeenCalled();
      expect(axios.get).toHaveBeenCalledTimes(1);
    });
  });

  it('filters test cases by priority', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    // Mock filtered response
    const p1TestCases = mockTestCases.filter(tc => tc.priority === 'P1');
    axios.get.mockResolvedValue({ data: p1TestCases });

    // Find and click priority filter
    const prioritySelect = screen.getByLabelText('优先级');
    fireEvent.mouseDown(prioritySelect);
    fireEvent.click(screen.getByText('P1'));

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/testcases/testcases/?priority=P1');
    });
  });

  it('filters test cases by status', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    // Mock filtered response
    const passedTestCases = mockTestCases.filter(tc => tc.status === 'passed');
    axios.get.mockResolvedValue({ data: passedTestCases });

    // Find and click status filter
    const statusSelect = screen.getByLabelText('状态');
    fireEvent.mouseDown(statusSelect);
    fireEvent.click(screen.getByText('通过'));

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/testcases/testcases/?status=passed');
    });
  });

  it('searches test cases by keyword', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    // Mock search response
    const searchResults = mockTestCases.filter(tc => tc.title.includes('Login'));
    axios.get.mockResolvedValue({ data: searchResults });

    // Find and use search input
    const searchInput = screen.getByPlaceholderText('搜索测试用例...');
    fireEvent.change(searchInput, { target: { value: 'Login' } });

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/testcases/testcases/?search=Login');
    });
  });

  it('shows error message when form validation fails', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增测试用例' }));

    // Try to submit without required fields
    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(screen.getByText('请输入用例标题')).toBeInTheDocument();
      expect(axios.post).not.toHaveBeenCalled();
    });
  });

  it('shows error message when create operation fails', async () => {
    render(<TestCasePage />);

    await waitFor(() => {
      expect(screen.getByText('Login Test Case')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增测试用例' }));

    fireEvent.change(screen.getByLabelText('用例标题'), { target: { value: 'Failing Test Case' } });

    axios.post.mockRejectedValue(new Error('Creation failed'));

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalledWith('保存失败');
    });
  });
});