/**
 * 玄关消息系统 - 主入口
 */

import express from 'express';
import { createServer } from 'http';
import cors from 'cors';
import dotenv from 'dotenv';
import { join } from 'path';
import { authMiddleware, handleTokenRequest } from './auth.js';
import { setupWebSocket, pushMessage, getConnectionStats, closeAllConnections } from './websocket.js';
import { createMessageRouter } from './message.js';
import { createMediaRouter, createMediaStaticMiddleware } from './media.js';
import type { XuanguanMessage } from './types.js';

// 加载环境变量
dotenv.config();

const app = express();
const httpServer = createServer(app);

// 配置
const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  host: process.env.HOST || '0.0.0.0',
  appId: process.env.APP_ID || 'cli_xxxxxxxxxxxxxxxx',
  appSecret: process.env.APP_SECRET || 'your_app_secret_here',
  jwtSecret: process.env.JWT_SECRET || 'your_jwt_secret_here',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '2h',
  mediaStoragePath: process.env.MEDIA_STORAGE_PATH || '/tmp/xuanguan/media',
  mediaBaseUrl: process.env.MEDIA_BASE_URL || 'http://192.168.91.107:3001',
  logLevel: process.env.LOG_LEVEL || 'info',
  rateLimitPerMinute: parseInt(process.env.RATE_LIMIT_PER_MINUTE || '300', 10),
  wsHeartbeatInterval: parseInt(process.env.WS_HEARTBEAT_INTERVAL || '30000', 10)
};

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件服务（Web Chat）
app.use(express.static(join(process.cwd(), 'public')));

// 请求日志
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`[HTTP] ${req.method} ${req.path} ${res.statusCode} ${duration}ms`);
  });
  next();
});

// 健康检查
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: Date.now(),
    uptime: process.uptime(),
    memory: process.memoryUsage()
  });
});

// WebSocket 连接统计
app.get('/stats', (req, res) => {
  const stats = getConnectionStats();
  res.json({
    status: 'ok',
    timestamp: Date.now(),
    websocket: stats
  });
});

// 认证接口
app.post('/oauth/token', async (req, res) => {
  try {
    const result = await handleTokenRequest(req.body, config.jwtSecret);

    if (result.code !== 0) {
      return res.status(401).json(result);
    }

    res.json(result);
  } catch (error: any) {
    console.error('[Auth] Token error:', error);
    res.status(500).json({
      code: 500001,
      message: 'Internal server error',
      data: null
    });
  }
});

// 消息接口
app.use('/api/v1/message', createMessageRouter(config.jwtSecret));
app.use('/api/v2/message', createMessageRouter(config.jwtSecret));

// 媒体接口
app.use('/api/v1/media', createMediaRouter(config.jwtSecret));
app.use('/api/v2/media', createMediaRouter(config.jwtSecret));

// 静态媒体文件服务
app.use('/media', createMediaStaticMiddleware());

// 错误处理
app.use((err: any, req: any, res: any, next: any) => {
  console.error('[Error]', err);
  res.status(500).json({
    code: 500001,
    message: 'Internal server error',
    data: null
  });
});

// 404 处理
app.use((req, res) => {
  res.status(404).json({
    code: 404000,
    message: 'Not found',
    data: null
  });
});

// 启动 HTTP 服务
httpServer.listen(config.port, config.host, () => {
  console.log('='.repeat(60));
  console.log('🚀 玄关消息系统服务端已启动');
  console.log('='.repeat(60));
  console.log(`📡 HTTP: http://${config.host}:${config.port}`);
  console.log(`🔌 WebSocket: ws://${config.host}:${config.port}/ws/messages`);
  console.log(`📊 健康检查：http://${config.host}:${config.port}/health`);
  console.log(`📈 连接统计：http://${config.host}:${config.port}/stats`);
  console.log('='.repeat(60));
  console.log(`ℹ️  App ID: ${config.appId}`);
  console.log(`⚠️  请确保修改 .env 中的默认密钥！`);
  console.log('='.repeat(60));
});

// 启动 WebSocket 服务
setupWebSocket(httpServer, {
  jwtSecret: config.jwtSecret,
  heartbeatInterval: config.wsHeartbeatInterval,
  onMessage: (accountId, message) => {
    console.log(`[WebSocket] Message for ${accountId}:`, message.messageId);
  }
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('[Server] SIGTERM received, shutting down gracefully...');

  closeAllConnections('Server shutdown');

  httpServer.close(() => {
    console.log('[Server] HTTP server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('[Server] SIGINT received, shutting down gracefully...');

  closeAllConnections('Server shutdown');

  httpServer.close(() => {
    console.log('[Server] HTTP server closed');
    process.exit(0);
  });
});

// 导出推送消息函数（供外部使用）
export { pushMessage };
export type { XuanguanMessage };
