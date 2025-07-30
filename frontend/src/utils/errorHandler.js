import { message } from 'antd';

// 错误处理工具类
class ErrorHandler {
  // 显示错误消息
  static showError(error, defaultMessage = '操作失败') {
    let errorMessage = defaultMessage;
    
    if (error?.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error?.response?.data?.error) {
      errorMessage = error.response.data.error;
    } else if (error?.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error?.message) {
      errorMessage = error.message;
    }
    
    message.error(errorMessage);
    return errorMessage;
  }
  
  // 显示成功消息
  static showSuccess(msg = '操作成功') {
    message.success(msg);
  }
  
  // 显示警告消息
  static showWarning(msg) {
    message.warning(msg);
  }
  
  // 显示信息消息
  static showInfo(msg) {
    message.info(msg);
  }
  
  // 显示加载消息
  static showLoading(msg = '加载中...') {
    return message.loading(msg);
  }
  
  // 处理API错误
  static handleApiError(error, customMessage) {
    console.error('API Error:', error);
    
    // 网络错误
    if (!error.response) {
      this.showError(null, customMessage || '网络连接失败，请检查网络设置');
      return '网络连接失败';
    }
    
    // HTTP状态码错误
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        this.showError(error, customMessage || '请求参数错误');
        break;
      case 401:
        this.showError(error, customMessage || '身份验证失败，请重新登录');
        break;
      case 403:
        this.showError(error, customMessage || '权限不足，无法执行此操作');
        break;
      case 404:
        this.showError(error, customMessage || '请求的资源不存在');
        break;
      case 500:
        this.showError(error, customMessage || '服务器内部错误');
        break;
      default:
        this.showError(error, customMessage || `请求失败 (${status})`);
    }
    
    return data?.message || data?.error || data?.detail || `HTTP ${status}`;
  }
  
  // 处理表单验证错误
  static handleFormError(error) {
    if (error?.response?.data) {
      const data = error.response.data;
      
      // Django REST framework 验证错误格式
      if (typeof data === 'object' && data !== null) {
        const errors = [];
        
        for (const [field, messages] of Object.entries(data)) {
          if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`);
          } else if (typeof messages === 'string') {
            errors.push(`${field}: ${messages}`);
          }
        }
        
        if (errors.length > 0) {
          message.error(errors.join('\n'));
          return errors;
        }
      }
    }
    
    return this.handleApiError(error, '表单验证失败');
  }
}

export default ErrorHandler;