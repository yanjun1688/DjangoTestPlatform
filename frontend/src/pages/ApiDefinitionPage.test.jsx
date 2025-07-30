import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { message } from 'antd';
import ApiDefinitionPage from './ApiDefinitionPage';

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

describe('ApiDefinitionPage', () => {
  const mockApis = [
    {
      id: 1,
      name: 'Get Users',
      method: 'GET',
      url: '/api/users',
      module: 'User Management',
      headers: '{}',
      params: '{}',
      body: '{}',
      description: 'Fetches all users',
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      name: 'Create User',
      method: 'POST',
      url: '/api/users',
      module: 'User Management',
      headers: '{"Content-Type": "application/json"}',
      params: '{}',
      body: '{"name": "test"}',
      description: 'Creates a new user',
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
    axios.get.mockResolvedValue({ data: mockApis });
  });

  it('renders the component and fetches data successfully', async () => {
    render(<ApiDefinitionPage />);

    expect(screen.getByText('API定义管理')).toBeInTheDocument();
    expect(axios.get).toHaveBeenCalledWith('/api-test/api-definitions/');

    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
      expect(screen.getByText('User Management')).toBeInTheDocument();
      expect(screen.getByText('Create User')).toBeInTheDocument();
    });
    expect(message.error).not.toHaveBeenCalled();
  });

  it('shows an error message when fetching API definitions fails', async () => {
    axios.get.mockRejectedValue(new Error('Network Error'));

    render(<ApiDefinitionPage />);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith('获取API定义失败');
    });
    expect(screen.queryByText('Get Users')).not.toBeInTheDocument();
  });

  it('opens the add API modal and allows adding a new API definition', async () => {
    render(<ApiDefinitionPage />);

    // Wait for initial data load
    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增API定义' }));

    expect(screen.getByText('新增API定义')).toBeInTheDocument(); // Modal title

    const newApi = {
      name: 'New Test API',
      url: 'http://example.com/new',
      method: 'POST',
      module: 'Test Module',
      headers: '{}',
      params: '{}',
      body: '{"key": "value"}',
      description: 'A new API for testing',
    };

    fireEvent.change(screen.getByLabelText('接口名称'), { target: { value: newApi.name } });
    fireEvent.change(screen.getByLabelText('接口URL'), { target: { value: newApi.url } });
    fireEvent.mouseDown(screen.getByLabelText('请求方法')); // Open select dropdown
    fireEvent.click(screen.getByText('POST')); // Select POST
    fireEvent.change(screen.getByLabelText('所属模块'), { target: { value: newApi.module } });
    fireEvent.change(screen.getByLabelText('请求头 (JSON格式)'), { target: { value: newApi.headers } });
    fireEvent.change(screen.getByLabelText('URL参数 (JSON格式)'), { target: { value: newApi.params } });
    fireEvent.change(screen.getByLabelText('请求体 (JSON格式)'), { target: { value: newApi.body } });
    fireEvent.change(screen.getByLabelText('接口描述'), { target: { value: newApi.description } });

    axios.post.mockResolvedValue({ data: { id: 3, ...newApi, created_at: new Date().toISOString() } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/api-test/api-definitions/', newApi);
      expect(message.success).toHaveBeenCalledWith('创建成功');
      expect(axios.get).toHaveBeenCalledTimes(2); // Initial fetch + fetch after creation
    });
  });

  it('shows an error message when adding a new API definition fails', async () => {
    render(<ApiDefinitionPage />);
    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增API定义' }));
    fireEvent.change(screen.getByLabelText('接口名称'), { target: { value: 'Failing API' } });
    fireEvent.change(screen.getByLabelText('接口URL'), { target: { value: 'http://fail.com' } });
    fireEvent.mouseDown(screen.getByLabelText('请求方法'));
    fireEvent.click(screen.getByText('GET'));

    axios.post.mockRejectedValue(new Error('API creation failed'));

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalledWith('保存失败');
    });
  });

  it('opens the edit API modal and allows editing an existing API definition', async () => {
    render(<ApiDefinitionPage />);

    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    // Find the edit button for the first API (Get Users)
    const editButtons = screen.getAllByRole('button', { name: '编辑' });
    fireEvent.click(editButtons[0]);

    expect(screen.getByText('编辑API定义')).toBeInTheDocument(); // Modal title
    expect(screen.getByLabelText('接口名称')).toHaveValue('Get Users');

    const updatedName = 'Updated Get Users API';
    fireEvent.change(screen.getByLabelText('接口名称'), { target: { value: updatedName } });

    axios.put.mockResolvedValue({ data: { ...mockApis[0], name: updatedName } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.put).toHaveBeenCalledWith(`/api-test/api-definitions/${mockApis[0].id}/`, {
        ...mockApis[0],
        name: updatedName,
      });
      expect(message.success).toHaveBeenCalledWith('更新成功');
      expect(axios.get).toHaveBeenCalledTimes(2); // Initial fetch + fetch after update
    });
  });

  it('shows an error message when editing an API definition fails', async () => {
    render(<ApiDefinitionPage />);
    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: '编辑' });
    fireEvent.click(editButtons[0]);

    fireEvent.change(screen.getByLabelText('接口名称'), { target: { value: 'Failing Update' } });

    axios.put.mockRejectedValue(new Error('API update failed'));

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.put).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalledWith('保存失败');
    });
  });

  it('allows deleting an API definition', async () => {
    render(<ApiDefinitionPage />);

    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(true); // Simulate user confirming deletion
    axios.delete.mockResolvedValue({});

    // Find the delete button for the first API (Get Users)
    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个API定义吗？');
      expect(axios.delete).toHaveBeenCalledWith(`/api-test/api-definitions/${mockApis[0].id}/`);
      expect(message.success).toHaveBeenCalledWith('删除成功');
      expect(axios.get).toHaveBeenCalledTimes(2); // Initial fetch + fetch after deletion
    });
  });

  it('does not delete an API definition if confirmation is cancelled', async () => {
    render(<ApiDefinitionPage />);

    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(false); // Simulate user cancelling deletion

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个API定义吗？');
      expect(axios.delete).not.toHaveBeenCalled();
      expect(message.success).not.toHaveBeenCalled();
      expect(message.error).not.toHaveBeenCalled();
      expect(axios.get).toHaveBeenCalledTimes(1); // Only initial fetch
    });
  });

  it('shows an error message when deleting an API definition fails', async () => {
    render(<ApiDefinitionPage />);
    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(true);
    axios.delete.mockRejectedValue(new Error('Delete failed'));

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(axios.delete).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalledWith('删除失败');
    });
  });

  it('validates JSON fields during add/edit', async () => {
    render(<ApiDefinitionPage />);
    await waitFor(() => {
      expect(screen.getByText('Get Users')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增API定义' }));

    // Fill required fields
    fireEvent.change(screen.getByLabelText('接口名称'), { target: { value: 'Invalid JSON API' } });
    fireEvent.change(screen.getByLabelText('接口URL'), { target: { value: 'http://invalid.com' } });
    fireEvent.mouseDown(screen.getByLabelText('请求方法'));
    fireEvent.click(screen.getByText('GET'));

    // Enter invalid JSON
    fireEvent.change(screen.getByLabelText('请求头 (JSON格式)'), { target: { value: '{invalid json' } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(screen.getByText('请求头 必须是有效的JSON格式')).toBeInTheDocument();
      expect(axios.post).not.toHaveBeenCalled();
      expect(message.error).not.toHaveBeenCalledWith('保存失败'); // Should not show generic save error yet
    });

    // Correct the JSON and try again
    fireEvent.change(screen.getByLabelText('请求头 (JSON格式)'), { target: { value: '{"valid": "json"}' } });
    axios.post.mockResolvedValue({ data: {} });
    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
      expect(message.success).toHaveBeenCalledWith('创建成功');
    });
  });
});