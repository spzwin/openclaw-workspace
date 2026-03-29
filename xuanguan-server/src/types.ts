/**
 * 玄关消息系统 - 类型定义
 */

// ============ 认证相关 ============

export interface TokenRequest {
  appId: string;
  appSecret: string;
  grantType: 'client_credentials';
  scope?: string;
}

export interface TokenResponse {
  code: number;
  message: string;
  data: {
    accessToken: string;
    expiresIn: number;
    tokenType: string;
    scope?: string;
    refreshToken?: string;
  } | null;
  meta?: {
    requestId: string;
    timestamp: number;
  };
}

export interface TokenPayload {
  appId: string;
  type: 'app';
  iat?: number;
  exp?: number;
}

// ============ 消息相关 ============

export type ConversationType = 'single' | 'group' | 'channel' | 'broadcast';
export type MessageType = 
  | 'text' | 'markdown' | 'html'
  | 'image' | 'voice' | 'video' | 'file'
  | 'link' | 'contact' | 'location'
  | 'card' | 'mixed' | 'custom';

export interface MessageContent {
  // 文本
  text?: string;
  html?: string;
  mentions?: string[];
  replyTo?: string;
  
  // 媒体
  mediaId?: string;
  mediaUrl?: string;
  thumbnailUrl?: string;
  width?: number;
  height?: number;
  fileSize?: number;
  mimeType?: string;
  fileExtension?: string;
  duration?: number;
  caption?: string;
  transcription?: string;
  
  // 链接
  url?: string;
  title?: string;
  description?: string;
  siteName?: string;
  domain?: string;
  
  // 联系人
  contactId?: string;
  name?: string;
  phoneNumber?: string;
  avatar?: string;
  organization?: string;
  contactTitle?: string;
  
  // 位置
  latitude?: number;
  longitude?: number;
  address?: string;
  accuracy?: number;
  
  // 卡片
  cardType?: string;
  templateId?: string;
  data?: Record<string, any>;
  
  // 混合
  blocks?: Array<{
    type: string;
    [key: string]: any;
  }>;
  
  // 自定义
  customType?: string;
  platform?: string;
  [key: string]: any;
}

export interface XuanguanMessage {
  messageId: string;
  conversationId: string;
  conversationType: ConversationType;
  senderId: string;
  senderName?: string;
  senderAvatar?: string;
  content: MessageContent;
  timestamp: number;
  groupId?: string | null;
  groupName?: string | null;
  platform?: string;
  platformMessageId?: string;
}

export interface SendMessageRequest {
  conversationId: string;
  conversationType: ConversationType;
  msgType: MessageType;
  content: MessageContent;
  receiverId?: string | null;
  groupId?: string | null;
  options?: {
    priority?: 'low' | 'normal' | 'high' | 'urgent';
    ttl?: number;
    requireAck?: boolean;
    fallbackToText?: boolean;
    fallbackText?: string;
  };
}

export interface SendMessageResponse {
  code: number;
  message: string;
  data: {
    messageId: string;
    status: 'sent' | 'pending' | 'failed' | 'recalled';
    sentAt?: number;
    deliveredAt?: number;
    readAt?: number;
    degraded?: boolean;
    degradedReason?: string;
  };
  meta?: {
    requestId: string;
    timestamp: number;
  };
}

// ============ 媒体相关 ============

export interface MediaUploadResponse {
  code: number;
  message: string;
  data: {
    mediaId: string;
    mediaUrl: string;
    thumbnailUrl?: string;
    expiresAt?: number;
    fileSize: number;
    mimeType: string;
    width?: number;
    height?: number;
    duration?: number;
  };
}

// ============ WebSocket 相关 ============

export type WSMessageType = 
  | 'auth' | 'auth_result'
  | 'message' | 'batch_messages'
  | 'heartbeat' | 'heartbeat_ack'
  | 'connection_status'
  | 'error' | 'disconnect'
  | 'welcome';

export interface WSMessage {
  type: WSMessageType;
  data?: any;
  messageId?: string;
  timestamp?: number;
  success?: boolean;
  error?: {
    code: number;
    message: string;
  };
  [key: string]: any;
}

export interface WSConnection {
  ws: any; // WebSocket
  accountId: string;
  appId: string;
  connectedAt: number;
  lastHeartbeat: number;
  isAlive: boolean;
}

// ============ 错误相关 ============

export interface ErrorResponse {
  code: number;
  message: string;
  data: null;
  meta?: {
    requestId: string;
    timestamp: number;
    path: string;
    method: string;
  };
  error?: {
    type: string;
    code: string;
    details?: Record<string, any>;
    suggestion?: string;
    retryAfter?: number | null;
    docs?: string;
  };
}

// ============ 配置相关 ============

export interface ServerConfig {
  port: number;
  wsPort: number;
  host: string;
  appId: string;
  appSecret: string;
  jwtSecret: string;
  jwtExpiresIn: string;
  mediaStoragePath: string;
  mediaBaseUrl: string;
  logLevel: string;
  rateLimitPerMinute: number;
  rateLimitPerHour: number;
  wsHeartbeatInterval: number;
  wsMaxReconnectCycles: number;
}

// ============ 存储接口 ============

export interface MessageStore {
  save(message: XuanguanMessage): Promise<void>;
  findById(messageId: string): Promise<XuanguanMessage | null>;
  findByConversation(conversationId: string, since: number, limit: number): Promise<XuanguanMessage[]>;
}

export interface TokenStore {
  save(appId: string, token: string, expiresAt: number): Promise<void>;
  find(appId: string): Promise<{token: string; expiresAt: number} | null>;
  delete(appId: string): Promise<void>;
}

export interface MediaStore {
  save(file: Buffer, filename: string, mimeType: string): Promise<{
    mediaId: string;
    mediaUrl: string;
    fileSize: number;
  }>;
  findById(mediaId: string): Promise<Buffer | null>;
  delete(mediaId: string): Promise<void>;
}
