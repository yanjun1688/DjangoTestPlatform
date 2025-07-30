import { useState, useEffect } from 'react';
import { Typography, Card, Button, Space, Divider, Tag } from 'antd';
import Logger from '../utils/logger';
import api from '../utils/api';
import BackButton from '../components/BackButton';

const { Title, Text } = Typography;

const DebugPage = () => {
  const [logs, setLogs] = useState([]);
  const [logLevel, setLogLevel] = useState('INFO');
  const [backendLog, setBackendLog] = useState([]);

  // 拉取后端接口测试日志
  const fetchBackendLog = async () => {
    try {
      const res = await api.get('/api-test/debug-log/');
      setBackendLog(res.data.log || '');
    } catch {
      setBackendLog('无法获取后端接口测试日志');
    }
  };

  useEffect(() => {
    fetchBackendLog();
    const timer = setInterval(fetchBackendLog, 5000);
    return () => clearInterval(timer);
  }, []);

  // 重写console方法来捕获日志
  useEffect(() => {
    const originalLog = console.log;
    const originalWarn = console.warn;
    const originalError = console.error;

    const addLog = (level, ...args) => {
      const timestamp = new Date().toLocaleTimeString();
      const message = args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
      ).join(' ');
      
      setLogs(prev => [...prev, { timestamp, level, message }]);
    };

    console.log = (...args) => {
      originalLog(...args);
      addLog('INFO', ...args);
    };

    console.warn = (...args) => {
      originalWarn(...args);
      addLog('WARN', ...args);
    };

    console.error = (...args) => {
      originalError(...args);
      addLog('ERROR', ...args);
    };

    return () => {
      console.log = originalLog;
      console.warn = originalWarn;
      console.error = originalError;
    };
  }, []);

  const clearLogs = () => {
    setLogs([]);
  };

  const testLogging = () => {
    Logger.debug('这是一条调试消息');
    Logger.info('这是一条信息消息');
    Logger.warn('这是一条警告消息');
    Logger.error('这是一条错误消息');
  };

  const getLogColor = (level) => {
    switch (level) {
      case 'ERROR': return 'red';
      case 'WARN': return 'orange';
      case 'INFO': return 'blue';
      case 'DEBUG': return 'green';
      default: return 'default';
    }
  };

  const filteredLogs = logs.filter(log => {
    const levels = ['DEBUG', 'INFO', 'WARN', 'ERROR'];
    const currentLevelIndex = levels.indexOf(logLevel);
    const logLevelIndex = levels.indexOf(log.level);
    return logLevelIndex >= currentLevelIndex;
  });

  return (
    <div style={{ padding: '20px', minHeight: '100vh', backgroundColor: '#f0f2f5' }}>
      <BackButton />
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>调试页面</Title>
        
        <Card title="日志控制" style={{ marginBottom: '20px' }}>
          <Space>
            <Text>日志级别:</Text>
            <select 
              value={logLevel} 
              onChange={(e) => setLogLevel(e.target.value)}
              style={{ padding: '4px 8px' }}
            >
              <option value="DEBUG">调试</option>
              <option value="INFO">信息</option>
              <option value="WARN">警告</option>
              <option value="ERROR">错误</option>
            </select>
            <Button onClick={clearLogs}>清空日志</Button>
            <Button onClick={testLogging} type="primary">测试日志</Button>
          </Space>
        </Card>

        <Card title={`日志记录 (${filteredLogs.length} 条)`}>
          <div style={{ 
            height: '500px', 
            overflowY: 'auto', 
            backgroundColor: '#1e1e1e',
            color: '#ffffff',
            padding: '10px',
            fontFamily: 'monospace',
            fontSize: '12px'
          }}>
            {filteredLogs.length === 0 ? (
              <Text style={{ color: '#888' }}>暂无日志</Text>
            ) : (
              filteredLogs.map((log, index) => (
                <div key={index} style={{ marginBottom: '4px' }}>
                  <Tag color={getLogColor(log.level)} size="small">
                    {log.level}
                  </Tag>
                  <span style={{ color: '#888', marginLeft: '8px' }}>
                    {log.timestamp}
                  </span>
                  <span style={{ marginLeft: '8px' }}>
                    {log.message}
                  </span>
                </div>
              ))
            )}
          </div>
        </Card>

        <Divider />

        <Card title="系统信息">
          <Space direction="vertical">
            <Text>用户代理: {navigator.userAgent}</Text>
            <Text>平台: {navigator.platform}</Text>
            <Text>语言: {navigator.language}</Text>
            <Text>在线状态: {navigator.onLine ? '在线' : '离线'}</Text>
            <Text>屏幕分辨率: {window.screen.width} x {window.screen.height}</Text>
            <Text>窗口大小: {window.innerWidth} x {window.innerHeight}</Text>
          </Space>
        </Card>

        <Card title="后端接口测试日志" style={{ marginTop: '20px' }}>
          <Text>{backendLog}</Text>
        </Card>
      </div>
    </div>
  );
};

export default DebugPage; 