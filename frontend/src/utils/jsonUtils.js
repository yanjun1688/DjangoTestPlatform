import Logger from './logger';

/**
 * JSON工具函数
 */

/**
 * 安全的JSON解析函数
 * @param {string} value - 要解析的JSON字符串
 * @param {any} defaultValue - 解析失败时的默认值
 * @param {string} fieldName - 字段名称，用于错误日志
 * @returns {any} 解析后的值或默认值
 */
export const safeJsonParse = (value, defaultValue, fieldName = 'unknown') => {
  if (!value || value.trim() === '') {
    Logger.debug(`Empty JSON field: ${fieldName}, using default:`, defaultValue);
    return defaultValue;
  }
  
  try {
    const parsed = JSON.parse(value.trim());
    Logger.debug(`Successfully parsed JSON for ${fieldName}:`, parsed);
    return parsed;
  } catch (error) {
    Logger.error(`JSON parse error for ${fieldName}:`, {
      error: error.message,
      value: value,
      position: error.message.match(/position (\d+)/)?.[1] || 'unknown'
    });
    throw new Error(`${fieldName} JSON格式错误: ${error.message}`);
  }
};

/**
 * 验证JSON字符串格式
 * @param {string} value - 要验证的JSON字符串
 * @param {string} fieldName - 字段名称
 * @returns {boolean} 是否为有效的JSON
 */
export const validateJson = (value, fieldName = 'unknown') => {
  if (!value || value.trim() === '') {
    return true; // 空值认为是有效的
  }
  
  try {
    JSON.parse(value.trim());
    return true;
  } catch (error) {
    Logger.warn(`Invalid JSON in ${fieldName}:`, {
      error: error.message,
      value: value
    });
    return false;
  }
};

/**
 * 格式化JSON字符串用于显示
 * @param {string} value - JSON字符串
 * @param {number} indent - 缩进空格数
 * @returns {string} 格式化后的JSON字符串
 */
export const formatJson = (value, indent = 2) => {
  if (!value || value.trim() === '') {
    return '';
  }
  
  try {
    const parsed = JSON.parse(value.trim());
    return JSON.stringify(parsed, null, indent);
  } catch (error) {
    Logger.warn('Failed to format JSON:', error.message);
    return value; // 返回原始值
  }
};

/**
 * 压缩JSON字符串
 * @param {string} value - JSON字符串
 * @returns {string} 压缩后的JSON字符串
 */
export const compressJson = (value) => {
  if (!value || value.trim() === '') {
    return '';
  }
  
  try {
    const parsed = JSON.parse(value.trim());
    return JSON.stringify(parsed);
  } catch (error) {
    Logger.warn('Failed to compress JSON:', error.message);
    return value; // 返回原始值
  }
};

/**
 * 获取JSON字段的默认值
 * @param {string} fieldType - 字段类型 ('object', 'array', 'string', 'number', 'boolean')
 * @returns {any} 默认值
 */
export const getJsonDefaultValue = (fieldType) => {
  const defaults = {
    object: '{}',
    array: '[]',
    string: '""',
    number: '0',
    boolean: 'false'
  };
  return defaults[fieldType] || '{}';
}; 