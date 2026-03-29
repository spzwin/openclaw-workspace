// 日志工具

import * as fs from 'fs/promises';
import * as path from 'path';

const LOG_DIR = path.join(process.cwd(), 'proj-system', 'logs');

export const logger = {
  info(message: string, data?: any) {
    log('INFO', message, data);
  },
  
  warn(message: string, data?: any) {
    log('WARN', message, data);
  },
  
  error(message: string, data?: any) {
    log('ERROR', message, data);
  },
  
  debug(message: string, data?: any) {
    log('DEBUG', message, data);
  }
};

function log(level: string, message: string, data?: any) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] [${level}] ${message}${data ? ' - ' + JSON.stringify(data) : ''}`;
  
  console.log(logLine);
  
  // 异步写入日志文件
  writeLogFile(logLine).catch(err => {
    console.error('Failed to write log file:', err);
  });
}

async function writeLogFile(logLine: string) {
  try {
    await fs.mkdir(LOG_DIR, { recursive: true });
    
    const date = new Date().toISOString().split('T')[0];
    const logFile = path.join(LOG_DIR, `orchestrator-${date}.log`);
    
    await fs.appendFile(logFile, logLine + '\n', 'utf-8');
  } catch (error) {
    console.error('Log write error:', error);
  }
}
