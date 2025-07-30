import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { message } from 'antd';
import UserManagementPage from './UserManagementPage';

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

describe('UserManagementPage', () => {
  const mockUsers = [
    {
      id: 1,
      username: 'johndoe',
      email: 'john@example.com',
      first_name: 'John',
      last_name: 'Doe',
      role: 'user',
      department: 'IT',
      phone: '123-456-7890',
      is_active: true,
      created_at: new Date().toISOString(),
    },
    {
      id: 2,
      username: 'janesmith',
      email: 'jane@example.com',
      first_name: 'Jane',
      last_name: 'Smith',
      role: 'admin',
      department: 'QA',
      phone: '098-765-4321',
      is_active: true,
      created_at: new Date().toISOString(),
    },
    {
      id: 3,
      username: 'inactive_user',
      email: 'inactive@example.com',
      first_name: 'Inactive',
      last_name: 'User',
      role: 'user',
      department: 'Support',
      phone: '555-123-4567',
      is_active: false,
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
    axios.get.mockResolvedValue({ data: mockUsers });
  });

  it('renders the component and fetches users successfully', async () => {
    render(<UserManagementPage />);

    expect(screen.getByText('用户管理')).toBeInTheDocument();
    expect(axios.get).toHaveBeenCalledWith('/api/user/users/');

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
      expect(screen.getByText('janesmith')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
      expect(screen.getByText('jane@example.com')).toBeInTheDocument();
      expect(screen.getByText('IT')).toBeInTheDocument();
      expect(screen.getByText('QA')).toBeInTheDocument();
    });
    expect(message.error).not.toHaveBeenCalled();
  });

  it('shows an error message when fetching users fails', async () => {
    axios.get.mockRejectedValue(new Error('Network Error'));

    render(<UserManagementPage />);

    await waitFor(() => {
      expect(message.error).toHaveBeenCalledWith('获取用户列表失败');
    });
    expect(screen.queryByText('johndoe')).not.toBeInTheDocument();
  });

  it('opens the add user modal and allows adding a new user', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增用户' }));

    expect(screen.getByText('新增用户')).toBeInTheDocument();

    const newUser = {
      username: 'newuser',
      email: 'newuser@example.com',
      first_name: 'New',
      last_name: 'User',
      password: 'password123',
      role: 'user',
      department: 'Development',
      phone: '111-222-3333',
    };

    fireEvent.change(screen.getByLabelText('用户名'), { target: { value: newUser.username } });
    fireEvent.change(screen.getByLabelText('邮箱'), { target: { value: newUser.email } });
    fireEvent.change(screen.getByLabelText('姓名'), { target: { value: newUser.first_name } });
    fireEvent.change(screen.getByLabelText('姓氏'), { target: { value: newUser.last_name } });
    fireEvent.change(screen.getByLabelText('密码'), { target: { value: newUser.password } });
    fireEvent.change(screen.getByLabelText('部门'), { target: { value: newUser.department } });
    fireEvent.change(screen.getByLabelText('电话'), { target: { value: newUser.phone } });

    // Select role
    fireEvent.mouseDown(screen.getByLabelText('角色'));
    fireEvent.click(screen.getByText('普通用户'));

    axios.post.mockResolvedValue({ data: { id: 4, ...newUser, created_at: new Date().toISOString() } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/api/user/users/', newUser);
      expect(message.success).toHaveBeenCalledWith('创建成功');
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  it('opens the edit user modal and allows editing an existing user', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: '编辑' });
    fireEvent.click(editButtons[0]);

    expect(screen.getByText('编辑用户')).toBeInTheDocument();
    expect(screen.getByLabelText('用户名')).toHaveValue('johndoe');

    const updatedEmail = 'john.updated@example.com';
    fireEvent.change(screen.getByLabelText('邮箱'), { target: { value: updatedEmail } });

    axios.put.mockResolvedValue({ data: { ...mockUsers[0], email: updatedEmail } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.put).toHaveBeenCalledWith(`/api/user/users/${mockUsers[0].id}/`, {
        ...mockUsers[0],
        email: updatedEmail,
      });
      expect(message.success).toHaveBeenCalledWith('更新成功');
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  it('allows toggling user active status', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    // Find toggle buttons (assuming they exist)
    const toggleButtons = screen.getAllByRole('button', { name: /启用|禁用/ });
    const firstToggleButton = toggleButtons[0];

    axios.post.mockResolvedValue({ data: { message: '用户已禁用', is_active: false } });

    fireEvent.click(firstToggleButton);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(`/api/user/users/${mockUsers[0].id}/toggle_active/`);
      expect(message.success).toHaveBeenCalledWith('用户状态更新成功');
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  it('allows deleting a user', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(true);
    axios.delete.mockResolvedValue({});

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个用户吗？');
      expect(axios.delete).toHaveBeenCalledWith(`/api/user/users/${mockUsers[0].id}/`);
      expect(message.success).toHaveBeenCalledWith('删除成功');
      expect(axios.get).toHaveBeenCalledTimes(2);
    });
  });

  it('does not delete a user if confirmation is cancelled', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    mockConfirm.mockReturnValue(false);

    const deleteButtons = screen.getAllByRole('button', { name: '删除' });
    fireEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(mockConfirm).toHaveBeenCalledWith('确定要删除这个用户吗？');
      expect(axios.delete).not.toHaveBeenCalled();
      expect(message.success).not.toHaveBeenCalled();
      expect(axios.get).toHaveBeenCalledTimes(1);
    });
  });

  it('filters users by role', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    // Mock filtered response
    const adminUsers = mockUsers.filter(user => user.role === 'admin');
    axios.get.mockResolvedValue({ data: adminUsers });

    // Find and click role filter
    const roleSelect = screen.getByLabelText('角色');
    fireEvent.mouseDown(roleSelect);
    fireEvent.click(screen.getByText('管理员'));

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/user/users/?role=admin');
    });
  });

  it('filters users by active status', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    // Mock filtered response
    const activeUsers = mockUsers.filter(user => user.is_active);
    axios.get.mockResolvedValue({ data: activeUsers });

    // Find and click status filter
    const statusSelect = screen.getByLabelText('状态');
    fireEvent.mouseDown(statusSelect);
    fireEvent.click(screen.getByText('启用'));

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/user/users/?is_active=true');
    });
  });

  it('searches users by keyword', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    // Mock search response
    const searchResults = mockUsers.filter(user => user.username.includes('john'));
    axios.get.mockResolvedValue({ data: searchResults });

    // Find and use search input
    const searchInput = screen.getByPlaceholderText('搜索用户...');
    fireEvent.change(searchInput, { target: { value: 'john' } });

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('/api/user/users/?search=john');
    });
  });

  it('shows error message when form validation fails', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增用户' }));

    // Try to submit without required fields
    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(screen.getByText('请输入用户名')).toBeInTheDocument();
      expect(screen.getByText('请输入邮箱')).toBeInTheDocument();
      expect(axios.post).not.toHaveBeenCalled();
    });
  });

  it('shows error message when create operation fails', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增用户' }));

    fireEvent.change(screen.getByLabelText('用户名'), { target: { value: 'failuser' } });
    fireEvent.change(screen.getByLabelText('邮箱'), { target: { value: 'fail@example.com' } });

    axios.post.mockRejectedValue(new Error('Creation failed'));

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalled();
      expect(message.error).toHaveBeenCalledWith('保存失败');
    });
  });

  it('displays user roles and statuses correctly', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    // Check that roles are displayed
    expect(screen.getByText('普通用户')).toBeInTheDocument();
    expect(screen.getByText('管理员')).toBeInTheDocument();

    // Check that status badges are displayed
    const activeStatuses = screen.getAllByText('启用');
    expect(activeStatuses.length).toBeGreaterThan(0);
    
    const inactiveStatuses = screen.getAllByText('禁用');
    expect(inactiveStatuses.length).toBeGreaterThan(0);
  });

  it('validates email format', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole('button', { name: '新增用户' }));

    fireEvent.change(screen.getByLabelText('用户名'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByLabelText('邮箱'), { target: { value: 'invalid-email' } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    await waitFor(() => {
      expect(screen.getByText('请输入有效的邮箱地址')).toBeInTheDocument();
      expect(axios.post).not.toHaveBeenCalled();
    });
  });

  it('shows loading state during operations', async () => {
    render(<UserManagementPage />);

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });

    // Mock a slow response
    axios.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    fireEvent.click(screen.getByRole('button', { name: '新增用户' }));

    fireEvent.change(screen.getByLabelText('用户名'), { target: { value: 'slowuser' } });
    fireEvent.change(screen.getByLabelText('邮箱'), { target: { value: 'slow@example.com' } });

    fireEvent.click(screen.getByRole('button', { name: '确 定' }));

    // Check for loading state (button should be disabled or show loading)
    expect(screen.getByRole('button', { name: '确 定' })).toBeDisabled();
  });
});