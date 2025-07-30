/**
 * 前端日志工具
 */

// 日志级别
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

// 当前日志级别（可以通过环境变量设置）
const CURRENT_LOG_LEVEL = (import.meta.env.MODE === 'development') ? LOG_LEVELS.DEBUG : LOG_LEVELS.INFO;

class Logger {
  static debug(message, ...args) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.DEBUG) {
      console.log(`[DEBUG] ${message}`, ...args);
    }
  }

  static info(message, ...args) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.INFO) {
      console.log(`[INFO] ${message}`, ...args);
    }
  }

  static warn(message, ...args) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.WARN) {
      console.warn(`[WARN] ${message}`, ...args);
    }
  }

  static error(message, ...args) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.ERROR) {
      console.error(`[ERROR] ${message}`, ...args);
    }
  }

  // API请求日志
  static apiRequest(method, url, data = null) {
    this.info(`API Request: ${method} ${url}`, data ? { data } : '');
  }

  // API响应日志
  static apiResponse(method, url, status, data = null) {
    if (status >= 400) {
      this.error(`API Response: ${method} ${url} - ${status}`, data ? { data } : '');
    } else {
      this.info(`API Response: ${method} ${url} - ${status}`);
    }
  }

  // 表单数据日志
  static formData(formName, data) {
    this.debug(`Form Data [${formName}]:`, data);
  }

  // 错误日志
  static errorWithContext(context, error, additionalData = {}) {
    this.error(`Error in ${context}:`, {
      message: error.message,
      stack: error.stack,
      ...additionalData
    });
  }
}

export default Logger; 