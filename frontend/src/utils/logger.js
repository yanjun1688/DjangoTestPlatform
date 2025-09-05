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

// 最大存储日志数量
const MAX_LOGS = 1000;

// localStorage键名
const STORAGE_KEY = 'debug_logs';

class Logger {
  // 存储日志到localStorage
  static _storeLog(level, message, context = null) {
    try {
      const logEntry = {
        level: level.toUpperCase(),
        message,
        timestamp: new Date().toISOString()
      };
      
      if (context !== null) {
        logEntry.context = context;
      }
      
      const existingLogs = this.getLogs();
      existingLogs.push(logEntry);
      
      // 限制日志数量
      if (existingLogs.length > MAX_LOGS) {
        existingLogs.splice(0, existingLogs.length - MAX_LOGS);
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(existingLogs));
    } catch (error) {
      // localStorage可能已满或不可用，静默处理
    }
  }
  
  static debug(message, context = null) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.DEBUG) {
      console.log(`[DEBUG] ${message}`, context || '');
      this._storeLog('DEBUG', message, context);
    }
  }

  static info(message, context = null) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.INFO) {
      console.log(`[INFO] ${message}`, context || '');
      this._storeLog('INFO', message, context);
    }
  }

  static warn(message, context = null) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.WARN) {
      console.warn(`[WARN] ${message}`, context || '');
      this._storeLog('WARN', message, context);
    }
  }

  static error(message, context = null) {
    if (CURRENT_LOG_LEVEL <= LOG_LEVELS.ERROR) {
      console.error(`[ERROR] ${message}`, context || '');
      this._storeLog('ERROR', message, context);
    }
  }
  
  // 获取存储的日志
  static getLogs() {
    try {
      const logs = localStorage.getItem(STORAGE_KEY);
      return logs ? JSON.parse(logs) : [];
    } catch (error) {
      return [];
    }
  }
  
  // 清除存储的日志
  static clearLogs() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
      // 静默处理错误
    }
  }

  // API请求日志
  static apiRequest(method, url, data = null) {
    this.info(`API Request: ${method} ${url}`, data ? { data } : null);
  }

  // API响应日志
  static apiResponse(method, url, status, data = null) {
    if (status >= 400) {
      this.error(`API Response: ${method} ${url} - ${status}`, data ? { data } : null);
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