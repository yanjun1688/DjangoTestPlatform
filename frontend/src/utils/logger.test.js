import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import Logger from './logger';

describe('Logger', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    
    // Mock console methods
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should log debug messages', () => {
    Logger.debug('Test debug message');
    
    expect(console.log).toHaveBeenCalledWith(
      expect.stringContaining('[DEBUG]'),
      expect.stringContaining('Test debug message')
    );
  });

  it('should log info messages', () => {
    Logger.info('Test info message');
    
    expect(console.log).toHaveBeenCalledWith(
      expect.stringContaining('[INFO]'),
      expect.stringContaining('Test info message')
    );
  });

  it('should log warning messages', () => {
    Logger.warn('Test warning message');
    
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('[WARN]'),
      expect.stringContaining('Test warning message')
    );
  });

  it('should log error messages', () => {
    Logger.error('Test error message');
    
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('[ERROR]'),
      expect.stringContaining('Test error message')
    );
  });

  it('should store logs in localStorage', () => {
    Logger.info('Test storage message');
    
    const storedLogs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    expect(storedLogs).toHaveLength(1);
    expect(storedLogs[0]).toMatchObject({
      level: 'INFO',
      message: 'Test storage message',
      timestamp: expect.any(String)
    });
  });

  it('should limit the number of stored logs', () => {
    // Add more logs than the limit
    for (let i = 0; i < 1500; i++) {
      Logger.info(`Test message ${i}`);
    }
    
    const storedLogs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    expect(storedLogs).toHaveLength(1000); // Should be limited to 1000
    
    // Should keep the most recent logs
    expect(storedLogs[storedLogs.length - 1].message).toBe('Test message 1499');
  });

  it('should include context information in logs', () => {
    const context = { userId: 123, action: 'login' };
    Logger.info('User action', context);
    
    const storedLogs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    expect(storedLogs[0]).toMatchObject({
      level: 'INFO',
      message: 'User action',
      context: context,
      timestamp: expect.any(String)
    });
  });

  it('should get logs from localStorage', () => {
    Logger.info('Test message 1');
    Logger.error('Test message 2');
    
    const logs = Logger.getLogs();
    expect(logs).toHaveLength(2);
    expect(logs[0]).toMatchObject({
      level: 'INFO',
      message: 'Test message 1'
    });
    expect(logs[1]).toMatchObject({
      level: 'ERROR',
      message: 'Test message 2'
    });
  });

  it('should clear logs from localStorage', () => {
    Logger.info('Test message');
    expect(Logger.getLogs()).toHaveLength(1);
    
    Logger.clearLogs();
    expect(Logger.getLogs()).toHaveLength(0);
    expect(localStorage.getItem('debug_logs')).toBeNull();
  });

  it('should handle localStorage errors gracefully', () => {
    // Mock localStorage to throw an error
    const originalSetItem = localStorage.setItem;
    localStorage.setItem = vi.fn(() => {
      throw new Error('localStorage is full');
    });
    
    // Should not throw an error
    expect(() => Logger.info('Test message')).not.toThrow();
    
    // Restore original method
    localStorage.setItem = originalSetItem;
  });

  it('should format timestamps correctly', () => {
    const now = new Date();
    Logger.info('Test timestamp');
    
    const storedLogs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    const logTimestamp = new Date(storedLogs[0].timestamp);
    
    // Should be within a reasonable time range (1 second)
    expect(Math.abs(logTimestamp.getTime() - now.getTime())).toBeLessThan(1000);
  });

  it('should handle different data types in context', () => {
    const context = {
      number: 42,
      boolean: true,
      null: null,
      undefined: undefined,
      object: { nested: 'value' },
      array: [1, 2, 3]
    };
    
    Logger.info('Complex context', context);
    
    const storedLogs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    expect(storedLogs[0].context).toEqual(context);
  });

  it('should work without context parameter', () => {
    Logger.info('Message without context');
    
    const storedLogs = JSON.parse(localStorage.getItem('debug_logs') || '[]');
    expect(storedLogs[0]).toMatchObject({
      level: 'INFO',
      message: 'Message without context',
      timestamp: expect.any(String)
    });
    expect(storedLogs[0]).not.toHaveProperty('context');
  });
});