import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import ReportListPage from './ReportListPage';

// Mock API
jest.mock('../utils/api', () => ({
  get: jest.fn(),
  post: jest.fn(),
  delete: jest.fn(),
}));

// Mock Logger
jest.mock('../utils/logger', () => ({
  info: jest.fn(),
  debug: jest.fn(),
  errorWithContext: jest.fn(),
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

import api from '../utils/api';

const mockReports = [
  {
    id: 1,
    name: '测试报告1',
    test_plan_name: '测试计划1',
    status: 'completed',
    total_tests: 10,
    passed_tests: 8,
    failed_tests: 1,
    error_tests: 1,
    success_rate: 80.0,
    duration_display: '5分钟',
    executed_by_username: 'testuser',
    start_time: '2024-01-01T10:00:00Z',
  },
  {
    id: 2,
    name: '测试报告2',
    test_plan_name: '测试计划2',
    status: 'running',
    total_tests: 5,
    passed_tests: 3,
    failed_tests: 0,
    error_tests: 0,
    success_rate: 60.0,
    duration_display: '进行中',
    executed_by_username: 'testuser2',
    start_time: '2024-01-01T11:00:00Z',
  }
];

const mockTestPlans = [
  { id: 1, name: '测试计划1' },
  { id: 2, name: '测试计划2' },
];

describe('ReportListPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock API responses
    api.get.mockImplementation((url) => {
      if (url.includes('testplans')) {
        return Promise.resolve({ data: mockTestPlans });
      }
      return Promise.resolve({ data: mockReports });
    });
    
    api.post.mockResolvedValue({
      data: { id: 3, name: '新测试执行' }
    });
    
    api.delete.mockResolvedValue({});
  });

  const renderWithRouter = (component) => {
    return render(
      <BrowserRouter>
        {component}
      </BrowserRouter>
    );
  };

  test('renders report list page with reports', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      expect(screen.getByText('测试报告1')).toBeInTheDocument();
      expect(screen.getByText('测试报告2')).toBeInTheDocument();
    });
    
    expect(screen.getByText('测试计划1')).toBeInTheDocument();
    expect(screen.getByText('测试计划2')).toBeInTheDocument();
  });

  test('displays summary statistics correctly', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // 总报告数
    });
    
    expect(screen.getByText('1')).toBeInTheDocument(); // 已完成
    expect(screen.getByText('1')).toBeInTheDocument(); // 运行中
  });

  test('opens execute modal when clicking execute test button', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      expect(screen.getByText('执行测试')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('执行测试'));
    
    await waitFor(() => {
      expect(screen.getByText('执行测试计划')).toBeInTheDocument();
      expect(screen.getByText('选择测试计划')).toBeInTheDocument();
    });
  });

  test('filters reports by status', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      expect(screen.getByText('测试报告1')).toBeInTheDocument();
    });
    
    // Find status filter dropdown
    const statusSelects = screen.getAllByRole('combobox');
    const statusSelect = statusSelects.find(select => 
      select.parentElement.textContent.includes('选择状态') || 
      select.getAttribute('placeholder') === '选择状态'
    );
    
    if (statusSelect) {
      fireEvent.mouseDown(statusSelect);
      
      await waitFor(() => {
        const completedOption = screen.getByText('已完成');
        fireEvent.click(completedOption);
      });
      
      // API should be called with status filter
      expect(api.get).toHaveBeenCalledWith('/api/reports/test-runs/', {
        params: expect.objectContaining({ status: 'completed' })
      });
    }
  });

  test('searches reports by name', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      expect(screen.getByPlaceholderText('搜索报告名称')).toBeInTheDocument();
    });
    
    const searchInput = screen.getByPlaceholderText('搜索报告名称');
    fireEvent.change(searchInput, { target: { value: '测试报告1' } });
    
    // Trigger search
    fireEvent.keyDown(searchInput, { key: 'Enter', code: 'Enter' });
    
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith('/api/reports/test-runs/', {
        params: expect.objectContaining({ search: '测试报告1' })
      });
    });
  });

  test('navigates to report detail when clicking report name', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      expect(screen.getByText('测试报告1')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('测试报告1'));
    
    expect(mockNavigate).toHaveBeenCalledWith('/reports/1');
  });

  test('exports report when clicking export button', async () => {
    // Mock blob download
    global.URL.createObjectURL = jest.fn(() => 'blob:url');
    global.URL.revokeObjectURL = jest.fn();
    
    const mockLink = {
      href: '',
      download: '',
      click: jest.fn(),
    };
    jest.spyOn(document, 'createElement').mockReturnValue(mockLink);
    jest.spyOn(document.body, 'appendChild').mockImplementation(() => {});
    jest.spyOn(document.body, 'removeChild').mockImplementation(() => {});
    
    api.get.mockImplementation((url, config) => {
      if (url.includes('export_html')) {
        return Promise.resolve({
          data: new Blob(['<html></html>'], { type: 'text/html' })
        });
      }
      return Promise.resolve({ data: mockReports });
    });
    
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      // Find export buttons (download icons)
      const exportButtons = screen.getAllByLabelText('download');
      expect(exportButtons.length).toBeGreaterThan(0);
    });
    
    const exportButtons = screen.getAllByLabelText('download');
    fireEvent.click(exportButtons[0]);
    
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        '/api/reports/test-runs/1/export_html/',
        { responseType: 'blob' }
      );
    });
  });

  test('deletes report when clicking delete button', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      // Find delete buttons
      const deleteButtons = screen.getAllByLabelText('delete');
      expect(deleteButtons.length).toBeGreaterThan(0);
    });
    
    const deleteButtons = screen.getAllByLabelText('delete');
    fireEvent.click(deleteButtons[0]);
    
    // Confirm deletion in popconfirm
    await waitFor(() => {
      const confirmButton = screen.getByText('确定');
      fireEvent.click(confirmButton);
    });
    
    await waitFor(() => {
      expect(api.delete).toHaveBeenCalledWith('/api/reports/test-runs/1/');
    });
  });

  test('submits execute test plan form', async () => {
    renderWithRouter(<ReportListPage />);
    
    // Open execute modal
    await waitFor(() => {
      fireEvent.click(screen.getByText('执行测试'));
    });
    
    await waitFor(() => {
      expect(screen.getByText('选择测试计划')).toBeInTheDocument();
    });
    
    // Fill form
    const testPlanSelect = screen.getByRole('combobox');
    fireEvent.mouseDown(testPlanSelect);
    
    await waitFor(() => {
      fireEvent.click(screen.getByText('测试计划1'));
    });
    
    const runNameInput = screen.getByDisplayValue(/测试执行/);
    fireEvent.change(runNameInput, { target: { value: '新测试执行' } });
    
    // Submit form
    fireEvent.click(screen.getByText('开始执行'));
    
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith(
        '/api-test/api-test-cases/execute_test_plan/',
        expect.objectContaining({
          test_plan_id: 1,
          run_name: '新测试执行'
        })
      );
    });
    
    expect(mockNavigate).toHaveBeenCalledWith('/reports/3');
  });

  test('refreshes data when clicking refresh button', async () => {
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      expect(screen.getByText('刷新')).toBeInTheDocument();
    });
    
    // Clear previous calls
    api.get.mockClear();
    
    fireEvent.click(screen.getByText('刷新'));
    
    expect(api.get).toHaveBeenCalledWith('/api/reports/test-runs/', { params: {} });
  });

  test('handles API errors gracefully', async () => {
    api.get.mockRejectedValue(new Error('API Error'));
    
    // Mock console.error to avoid test output noise
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    renderWithRouter(<ReportListPage />);
    
    await waitFor(() => {
      // Should handle error and show empty state or error message
      expect(screen.queryByText('测试报告1')).not.toBeInTheDocument();
    });
    
    consoleSpy.mockRestore();
  });
});