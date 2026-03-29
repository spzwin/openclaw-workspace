/**
 * 玄关消息系统 - 认证模块
 */

import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import type { TokenRequest, TokenResponse, TokenPayload } from './types.js';

// 应用配置（实际应该从数据库读取）
const apps = new Map<string, { appId: string; appSecret: string; name: string }>([
  ['cli_xxxxxxxxxxxxxxxx', { 
    appId: 'cli_xxxxxxxxxxxxxxxx',
    appSecret: 'your_app_secret_here_change_in_production',
    name: 'OpenClaw 玄关插件'
  }]
]);

// Token 缓存
const tokenCache = new Map<string, { token: string; expiresAt: number }>();

/**
 * 生成访问令牌
 */
export function generateToken(appId: string, jwtSecret: string, expiresIn: string = '2h'): string {
  const payload: TokenPayload = {
    appId,
    type: 'app'
  };
  
  return jwt.sign(payload, jwtSecret as jwt.Secret, { expiresIn: expiresIn as any });
}

/**
 * 验证访问令牌
 */
export function verifyToken(token: string, jwtSecret: string): TokenPayload | null {
  try {
    return jwt.verify(token, jwtSecret) as TokenPayload;
  } catch (error) {
    return null;
  }
}

/**
 * 获取访问令牌（带缓存）
 */
export async function getAccessToken(
  appId: string,
  appSecret: string,
  jwtSecret: string
): Promise<{ success: boolean; token?: string; error?: string }> {
  // 检查缓存
  const cached = tokenCache.get(appId);
  if (cached && cached.expiresAt > Date.now() + 60000) {
    return { success: true, token: cached.token };
  }
  
  // 验证应用
  const app = apps.get(appId);
  if (!app || app.appSecret !== appSecret) {
    return { success: false, error: 'Invalid appId or appSecret' };
  }
  
  // 生成 token
  const token = generateToken(appId, jwtSecret, '2h');
  const expiresAt = Date.now() + 2 * 60 * 60 * 1000; // 2 小时
  
  // 缓存
  tokenCache.set(appId, { token, expiresAt });
  
  return { success: true, token };
}

/**
 * 处理认证请求
 */
export async function handleTokenRequest(
  request: TokenRequest,
  jwtSecret: string
): Promise<TokenResponse> {
  const requestId = `req_${uuidv4()}`;
  const timestamp = Date.now();
  
  // 验证参数
  if (!request.appId || !request.appSecret) {
    return {
      code: 400002,
      message: 'Missing appId or appSecret',
      data: null,
      meta: { requestId, timestamp }
    };
  }
  
  if (request.grantType !== 'client_credentials') {
    return {
      code: 400001,
      message: 'Unsupported grant type',
      data: null,
      meta: { requestId, timestamp }
    };
  }
  
  // 获取 token
  const result = await getAccessToken(request.appId, request.appSecret, jwtSecret);
  
  if (!result.success) {
    return {
      code: 401001,
      message: result.error || 'Authentication failed',
      data: null,
      meta: { requestId, timestamp }
    };
  }
  
  return {
    code: 0,
    message: 'success',
    data: {
      accessToken: result.token!,
      expiresIn: 7200,
      tokenType: 'Bearer',
      scope: request.scope || 'message:send message:receive media:upload'
    },
    meta: { requestId, timestamp }
  };
}

/**
 * 认证中间件（Express）
 */
export function authMiddleware(jwtSecret: string) {
  return (req: any, res: any, next: any) => {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        code: 401003,
        message: 'Missing authorization header',
        data: null
      });
    }
    
    const token = authHeader.substring(7);
    const payload = verifyToken(token, jwtSecret);
    
    if (!payload) {
      return res.status(401).json({
        code: 401002,
        message: 'Invalid or expired token',
        data: null
      });
    }
    
    // 附加到请求对象
    req.appId = payload.appId;
    req.tokenPayload = payload;
    
    next();
  };
}
