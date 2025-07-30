import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { message } from 'antd';
import TestPlanPage from './TestPlanPage';

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

describe('TestPlanPage', () => {
  const mockTestPlans = [
    {
      id: 1,
      name: 'Sprint 1 Test Plan',
      status: 'pending',
      assignee: 1,
      assignee_name: 'John Doe',
      test_cases: [1, 2, 3],
      test_cases_count: 3,
      start_time: '2024-01-01T00:00:00Z',
      end_time: '2024-01-31T23:59:59Z',
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      name: 'Sprint 2 Test Plan',
      status: 'running',
      assignee: 2,
      assignee_name: 'Jane Smith',
      test_cases: [4, 5],
      test_cases_count: 2,
      start_time: '2024-02-01T00:00:00Z',
      end_time: '2024-02-28T23:59:59Z',
      created_at: new Date().toISOString(),
    },
  ];

  const mockTestCases = [
    { id: 1, title: 'Test Case 1', status: 'blocked' },
    { id: 2, title: 'Test Case 2', status: 'passed' },
    { id: 3, title: 'Test Case 3', status: 'failed' },
    { id: 4, title: 'Test Case 4', status: 'blocked' },
    { id: 5, title: 'Test Case 5', status: 'passed' },
  ];

  const mockUsers = [
    { id: 1, username: 'johndoe', first_name: 'John', last_name: 'Doe' },
    { id: 2, username: 'janesmith', first_name: 'Jane', last_name: 'Smith' },
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
    
    // Setup default mock responses
    axios.get.mockImplementation((url) => {
      if (url === '/testcases/testplans/') {
        return Promise.resolve({ data: mockTestPlans });
      } else if (url === '/testcases/testcases/') {
        return Promise.resolve({ data: mockTestCases });
      } else if (url === '/api/user/users/') {
        return Promise.resolve({ data: mockUsers });
      }
      return Promise.resolve({ data: [] });
    });
  });

  it('renders the component and fetches test plans successfully', async () => {
    render(<TestPlanPage />);

    expect(screen.getByText('测试计划管理')).toBeInTheDocument();
    expect(axios.get).toHaveBeenCalledWith('/testcases/testplans/');

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
      expect(screen.getByText('Sprint 2 Test Plan')).toBeInTheDocument();
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
    expect(message.error).not.toHaveBeenCalled();
  });

  it('shows an error message when fetching test plans fails', async () => {
    axios.get.mockRejectedValue(new Error('Network Error'));

    render(<TestPlanPage />);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith('获取测试计划失败');
    });
    expect(screen.queryByText('Sprint 1 Test Plan')).not.toBeInTheDocument();
  });

  it('opens the add test plan modal and allows adding a new test plan', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增测试计划' }));

    expect(screen.getByText('新增测试计划')).toBeInTheDocument();

    const newTestPlan = {
      name: 'Sprint 3 Test Plan',
      status: 'pending',
      assignee: 1,
      test_cases: [1, 2],
      start_time: '2024-03-01T00:00:00Z',
      end_time: '2024-03-31T23:59:59Z',
    };

    fireEvent.change(screen.getByLabelText('计划名称'), { target: { value: newTestPlan.name } });
    
    // Select assignee
    fireEvent.mouseDown(screen.getByLabelText('执行人'));
    fireEvent.click(screen.getByText('John Doe'));
    
    // Select test cases
    fireEvent.mouseDown(screen.getByLabelText('测试用例'));
    fireEvent.click(screen.getByText('Test Case 1'));
    fireEvent.click(screen.getByText('Test Case 2'));
    
    // Set dates
    const startDateInput = screen.getByLabelText('开始时间');
    const endDateInput = screen.getByLabelText('结束时间');
    fireEvent.change(startDateInput, { target: { value: '2024-03-01' } });
    fireEvent.change(endDateInput, { target: { value: '2024-03-31' } });

    axios.post.mockResolvedValue({ data: { id: 3, ...newTestPlan, created_at: new Date().toISOString() } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/testcases/testplans/', expect.objectContaining({
        name: newTestPlan.name,
        assignee: newTestPlan.assignee,
        test_cases: newTestPlan.test_cases,
      }));
      expect(message.success).toHaveBeenCalledWith('创建成功');
    });
  });

  it('opens the edit test plan modal and allows editing an existing test plan', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: '编辑' });
    fireEvent.click(editButtons[0]);

    expect(screen.getByText('编辑测试计划')).toBeInTheDocument();
    expect(screen.getByLabelText('计划名称')).toHaveValue('Sprint 1 Test Plan');

    const updatedName = 'Updated Sprint 1 Test Plan';
    fireEvent.change(screen.getByLabelText('计划名称'), { target: { value: updatedName } });

    axios.put.mockResolvedValue({ data: { ...mockTestPlans[0], name: updatedName } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.put).toHaveBeenCalledWith(`/testcases/testplans/${mockTestPlans[0].id}/`, expect.objectContaining({
        name: updatedName,
      }));
      expect(message.success).toHaveBeenCalledWith('更新成功');
    });
  });

  it('allows deleting a test plan', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(true);
    axios.delete.mockResolvedValue({});

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个测试计划吗？');
      expect(axios.delete).toHaveBeenCalledWith(`/testcases/testplans/${mockTestPlans[0].id}/`);
      expect(message.success).toHaveBeenCalledWith('删除成功');
    });
  });

  it('does not delete a test plan if confirmation is cancelled', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(false);

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个测试计划吗？');
      expect(axios.delete).not.toHaveBeenCalled();
      expect(message.success).not.toHaveBeenCalled();
    });
  });

  it('filters test plans by status', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    // Mock filtered response
    const runningPlans = mockTestPlans.filter(tp => tp.status === 'running');
    axios.get.mockResolvedValue({ data: runningPlans });

    // Find and click status filter
    const statusSelect = screen.getByLabelText('状态');
    fireEvent.mouseDown(statusSelect);
    fireEvent.click(screen.getByText('进行中'));

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/testcases/testplans/?status=running');
    });
  });

  it('searches test plans by keyword', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    // Mock search response
    const searchResults = mockTestPlans.filter(tp => tp.name.includes('Sprint 1'));
    axios.get.mockResolvedValue({ data: searchResults });

    // Find and use search input
    const searchInput = screen.getByPlaceholderText('搜索测试计划...');
    fireEvent.change(searchInput, { target: { value: 'Sprint 1' } });

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/testcases/testplans/?search=Sprint 1');
    });
  });

  it('shows error message when form validation fails', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增测试计划' }));

    // Try to submit without required fields
    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(screen.getByText('请输入计划名称')).toBeInTheDocument();
      expect(axios.post).not.toHaveBeenCalled();
    });
  });

  it('shows error message when create operation fails', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增测试计划' }));

    fireEvent.change(screen.getByLabelText('计划名称'), { target: { value: 'Failing Test Plan' } });

    axios.post.mockRejectedValue(new Error('Creation failed'));

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalledWith('保存失败');
    });
  });

  it('displays test plan statistics correctly', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    // Check that test case counts are displayed
    const testCasesCounts = screen.getAllByText(/\d+/);
    expect(testCasesCounts).toBeTruthy();
    
    // Check status badges
    expect(screen.getByText('待执行')).toBeInTheDocument();
    expect(screen.getByText('进行中')).toBeInTheDocument();
  });

  it('updates test plan status correctly', async () => {
    render(<TestPlanPage />);

    await waitFor(() => {
      expect(screen.getByText('Sprint 1 Test Plan')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: '编辑' });
    fireEvent.click(editButtons[0]);

    // Change status to running
    fireEvent.mouseDown(screen.getByLabelText('状态'));
    fireEvent.click(screen.getByText('进行中'));

    axios.put.mockResolvedValue({ data: { ...mockTestPlans[0], status: 'running' } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.put).toHaveBeenCalledWith(`/testcases/testplans/${mockTestPlans[0].id}/`, expect.objectContaining({
        status: 'running',
      }));
      expect(message.success).toHaveBeenCalledWith('更新成功');
    });
  });
});