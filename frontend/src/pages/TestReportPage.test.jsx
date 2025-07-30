import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import TestReportPage from './TestReportPage';

// Mock Chart.js
jest.mock('chart.js', () => ({
  Chart: {
    register: jest.fn(),
  },
  CategoryScale: jest.fn(),
  LinearScale: jest.fn(),
  BarElement: jest.fn(),
  ArcElement: jest.fn(),
  Title: jest.fn(),
  Tooltip: jest.fn(),
  Legend: jest.fn(),
}));

// Mock react-chartjs-2
jest.mock('react-chartjs-2', () => ({
  Bar: ({ data, options }) => (
    <div data-testid="bar-chart">
      <div>Bar Chart</div>
      <div>{JSON.stringify(data)}</div>
    </div>
  ),
  Pie: ({ data, options }) => (
    <div data-testid="pie-chart">
      <div>Pie Chart</div>
      <div>{JSON.stringify(data)}</div>
    </div>
  ),
}));

// Mock API
jest.mock('../utils/api', () => ({
  get: jest.fn(),
}));

// Mock Logger
jest.mock('../utils/logger', () => ({
  info: jest.fn(),
  debug: jest.fn(),
  errorWithContext: jest.fn(),
}));

// Mock useParams
const mockUseParams = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => mockUseParams(),
  useNavigate: () => jest.fn(),
}));

import api from '../utils/api';

const mockTestRun = {
  id: 1,
  name: '测试执行1',
  status: 'completed',
  test_plan_detail: {
    name: '测试计划1'
  },
  executed_by_username: 'testuser',
  start_time: '2024-01-01T10:00:00Z',
  end_time: '2024-01-01T10:30:00Z',
  duration_display: '30分钟',
  total_tests: 10,
  passed_tests: 7,
  failed_tests: 2,
  error_tests: 1,
  success_rate: 70.0,
  avg_response_time: 150.5,
  description: '测试描述',
  results: [
    {
      id: 1,
      test_case_name: '测试用例1',
      api_name: 'API1',
      api_method: 'GET',
      api_url: 'https://api.example.com/test1',
      status: 'passed',
      response_code: 200,
      response_time: 100.0,
      executed_at: '2024-01-01T10:05:00Z',
    },
    {
      id: 2,
      test_case_name: '测试用例2',
      api_name: 'API2',
      api_method: 'POST',
      api_url: 'https://api.example.com/test2',
      status: 'failed',
      response_code: 500,
      response_time: 200.0,
      executed_at: '2024-01-01T10:10:00Z',
      error_message: '服务器内部错误',
      response_body: '{"error": "Internal server error"}',
    }
  ]
};

const mockStatistics = {
  total_tests: 10,
  passed_tests: 7,
  failed_tests: 2,
  error_tests: 1,
  success_rate: 70.0,
  avg_response_time: 150.5,
  status_distribution: {
    passed: 7,
    failed: 2,
    error: 1
  },
  response_time_distribution: [
    { range: '0-100ms', count: 3 },
    { range: '100-200ms', count: 4 },
    { range: '200ms+', count: 3 }
  ]
};

describe('TestReportPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockUseParams.mockReturnValue({ runId: '1' });
    
    // Mock API responses
    api.get.mockImplementation((url) => {
      if (url.includes('/statistics/')) {
        return Promise.resolve({ data: mockStatistics });
      }
      if (url.includes('/export_html/')) {
        return Promise.resolve({ 
          data: new Blob(['<html></html>'], { type: 'text/html' }) 
        });
      }
      return Promise.resolve({ data: mockTestRun });
    });
  });

  const renderWithRouter = (component) => {
    return render(
      <BrowserRouter>
        {component}
      </BrowserRouter>
    );
  };

  test('renders test report page with basic information', async () => {
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByText('测试执行1')).toBeInTheDocument();
    });
    
    expect(screen.getByText('已完成')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument(); // 总用例数
    expect(screen.getByText('7')).toBeInTheDocument(); // 通过数
    expect(screen.getByText('2')).toBeInTheDocument(); // 失败数
  });

  test('displays charts correctly', async () => {
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByTestId('pie-chart')).toBeInTheDocument();
      expect(screen.getByTestId('bar-chart')).toBeInTheDocument();
    });
  });

  test('shows test results table', async () => {
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByText('测试用例1')).toBeInTheDocument();
      expect(screen.getByText('测试用例2')).toBeInTheDocument();
    });
    
    expect(screen.getByText('GET')).toBeInTheDocument();
    expect(screen.getByText('POST')).toBeInTheDocument();
  });

  test('opens detail drawer when clicking details button', async () => {
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByText('测试用例1')).toBeInTheDocument();
    });
    
    // Click the first details button
    const detailButtons = screen.getAllByText('详情');
    fireEvent.click(detailButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByText('测试结果详情')).toBeInTheDocument();
    });
  });

  test('exports HTML report when clicking export button', async () => {
    // Mock URL.createObjectURL and related functions
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
    
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByText('导出HTML')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('导出HTML'));
    
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        '/api/reports/test-runs/1/export_html/', 
        { responseType: 'blob' }
      );
    });
  });

  test('shows error state when test run not found', async () => {
    api.get.mockRejectedValue(new Error('Not found'));
    
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByText('未找到测试报告')).toBeInTheDocument();
    });
  });

  test('shows loading state initially', () => {
    api.get.mockImplementation(() => new Promise(() => {})); // Never resolves
    
    renderWithRouter(<TestReportPage />);
    
    expect(screen.getByText('加载测试报告中...')).toBeInTheDocument();
  });

  test('navigates back to reports list when clicking back button', async () => {
    const mockNavigate = jest.fn();
    jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
    
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByText('返回列表')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('返回列表'));
    
    expect(mockNavigate).toHaveBeenCalledWith('/reports');
  });

  test('refreshes data when clicking refresh button', async () => {
    renderWithRouter(<TestReportPage />);
    
    await waitFor(() => {
      expect(screen.getByText('刷新')).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByText('刷新'));
    
    expect(api.get).toHaveBeenCalledTimes(4); // Initial load (2 calls) + refresh (2 calls)
  });
});