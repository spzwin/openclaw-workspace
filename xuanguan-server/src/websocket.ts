/**
 * 玄关消息系统 - WebSocket 服务
 */

import { WebSocketServer, WebSocket } from 'ws';
import { v4 as uuidv4 } from 'uuid';
import { verifyToken } from './auth.js';
import type { WSMessage, WSConnection, XuanguanMessage } from './types.js';

// 连接存储：accountId -> Set<WSConnection>
const connections = new Map<string, Set<WSConnection>>();

// 心跳间隔
const HEARTBEAT_INTERVAL = 30000; // 30 秒

export interface WebSocketServiceOptions {
  jwtSecret: string;
  heartbeatInterval?: number;
  onMessage?: (accountId: string, message: XuanguanMessage) => void;
}

/**
 * 设置 WebSocket 服务
 */
export function setupWebSocket(
  server: any,
  options: WebSocketServiceOptions
): WebSocketServer {
  const { jwtSecret, heartbeatInterval = HEARTBEAT_INTERVAL } = options;
  
  const wss = new WebSocketServer({
    server,
    path: '/ws/messages'
  });
  
  wss.on('connection', (ws: WebSocket, req: any) => {
    console.log('[WebSocket] New connection');
    
    const url = new URL(req.url, `http://${req.headers.host}`);
    const appId = url.searchParams.get('appId') || '';
    const accountId = url.searchParams.get('accountId') || 'default';
    const token = url.searchParams.get('token');
    
    let connection: WSConnection | null = null;
    let heartbeatTimer: NodeJS.Timeout | null = null;
    
    // 认证（方式 1: URL 参数）
    if (token) {
      const payload = verifyToken(token, jwtSecret);
      if (!payload) {
        console.log(`[WebSocket] Auth failed for ${accountId}`);
        ws.close(4001, 'Invalid token');
        return;
      }
      console.log(`[WebSocket] Authenticated via URL: ${appId}`);
    }
    
    // 保存连接
    connection = {
      ws,
      accountId,
      appId,
      connectedAt: Date.now(),
      lastHeartbeat: Date.now(),
      isAlive: true
    };
    
    if (!connections.has(accountId)) {
      connections.set(accountId, new Set());
    }
    connections.get(accountId)!.add(connection);
    
    console.log(`[WebSocket] Connection added for ${accountId}, total: ${connections.get(accountId)!.size}`);
    
    // 发送欢迎消息
    sendToConnection(connection, {
      type: 'welcome',
      message: 'Connected to Xuanguan WebSocket',
      accountId,
      timestamp: Date.now()
    });
    
    // 心跳检测
    heartbeatTimer = setInterval(() => {
      if (!connection || !connection.isAlive) {
        console.log(`[WebSocket] Connection timeout for ${accountId}`);
        if (heartbeatTimer) clearInterval(heartbeatTimer);
        ws.terminate();
        return;
      }
      
      connection.isAlive = false;
      ws.ping();
    }, heartbeatInterval);
    
    // 消息处理
    ws.on('message', (data: Buffer) => {
      try {
        const message: WSMessage = JSON.parse(data.toString());
        
        // 认证消息
        if (message.type === 'auth') {
          const payload = verifyToken(message.token, jwtSecret);
          if (payload) {
            sendToConnection(connection!, {
              type: 'auth_result',
              success: true,
              message: 'Authenticated',
              serverTime: Date.now()
            });
            console.log(`[WebSocket] Authenticated via message: ${payload.appId}`);
          } else {
            sendToConnection(connection!, {
              type: 'auth_result',
              success: false,
              error: {
                code: 401002,
                message: 'Invalid or expired token'
              }
            });
          }
          return;
        }
        
        // 心跳消息
        if (message.type === 'heartbeat') {
          connection!.isAlive = true;
          connection!.lastHeartbeat = Date.now();
          
          sendToConnection(connection!, {
            type: 'heartbeat_ack',
            timestamp: message.timestamp || Date.now(),
            serverTime: Date.now(),
            latency: Date.now() - (message.timestamp || Date.now())
          });
          return;
        }
        
        console.log(`[WebSocket] Message from ${accountId}: ${message.type}`);
        
      } catch (error) {
        console.error('[WebSocket] Message parse error:', error);
      }
    });
    
    // 连接关闭
    ws.on('close', () => {
      console.log(`[WebSocket] Closed for ${accountId}`);
      if (heartbeatTimer) clearInterval(heartbeatTimer);
      
      const accountConnections = connections.get(accountId);
      if (accountConnections && connection) {
        accountConnections.delete(connection);
        if (accountConnections.size === 0) {
          connections.delete(accountId);
        }
      }
    });
    
    // 错误处理
    ws.on('error', (error) => {
      console.error(`[WebSocket] Error for ${accountId}:`, error);
    });
    
    // pong 响应
    ws.on('pong', () => {
      if (connection) {
        connection.isAlive = true;
      }
    });
  });
  
  console.log('[WebSocket] Server ready');
  return wss;
}

/**
 * 发送消息到指定连接
 */
function sendToConnection(connection: WSConnection, message: WSMessage): void {
  if (connection.ws.readyState === WebSocket.OPEN) {
    connection.ws.send(JSON.stringify(message));
  }
}

/**
 * 推送消息到指定账户的所有连接
 */
export function pushMessage(accountId: string, message: XuanguanMessage): boolean {
  const accountConnections = connections.get(accountId);
  
  if (!accountConnections || accountConnections.size === 0) {
    console.log(`[WebSocket] No connections for ${accountId}`);
    return false;
  }
  
  const payload: WSMessage = {
    type: 'message',
    data: message,
    timestamp: Date.now()
  };
  
  let sentCount = 0;
  for (const connection of accountConnections) {
    if (connection.ws.readyState === WebSocket.OPEN) {
      connection.ws.send(JSON.stringify(payload));
      sentCount++;
    }
  }
  
  console.log(`[WebSocket] Pushed message to ${sentCount}/${accountConnections.size} connections for ${accountId}`);
  return sentCount > 0;
}

/**
 * 推送消息到多个账户
 */
export function pushMessageToMultiple(accountIds: string[], message: XuanguanMessage): number {
  let totalSent = 0;
  
  for (const accountId of accountIds) {
    if (pushMessage(accountId, message)) {
      totalSent++;
    }
  }
  
  return totalSent;
}

/**
 * 获取连接统计
 */
export function getConnectionStats(): {
  totalAccounts: number;
  totalConnections: number;
  byAccount: Map<string, number>;
} {
  let totalConnections = 0;
  const byAccount = new Map<string, number>();
  
  for (const [accountId, conns] of connections) {
    const count = conns.size;
    totalConnections += count;
    byAccount.set(accountId, count);
  }
  
  return {
    totalAccounts: connections.size,
    totalConnections,
    byAccount
  };
}

/**
 * 关闭指定账户的所有连接
 */
export function closeConnections(accountId: string, reason: string = 'Server shutdown'): void {
  const accountConnections = connections.get(accountId);
  
  if (accountConnections) {
    for (const connection of accountConnections) {
      sendToConnection(connection, {
        type: 'disconnect',
        reason,
        timestamp: Date.now()
      });
      connection.ws.close(1000, reason);
    }
    
    connections.delete(accountId);
    console.log(`[WebSocket] Closed ${accountConnections.size} connections for ${accountId}`);
  }
}

/**
 * 关闭所有连接
 */
export function closeAllConnections(reason: string = 'Server shutdown'): void {
  for (const accountId of connections.keys()) {
    closeConnections(accountId, reason);
  }
  console.log('[WebSocket] All connections closed');
}
