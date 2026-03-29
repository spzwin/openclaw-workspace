// 调度中心共享类型定义

export interface Project {
  id: string;
  name: string;
  description?: string;
  version: number;  // 乐观锁版本号
  status: 'pending' | 'in_progress' | 'completed' | 'paused' | 'failed';
  createdAt: string;
  updatedAt: string;
  progress: {
    currentPhase: string;
    completedTasks: string[];
    pendingTasks: string[];
    assignedTasks?: string[];
    percentComplete: number;
  };
  currentAgent: {
    expertId: string;
    agentId: string;
    sessionKey: string;
    assignedAt: string;
    task: string;
  } | null;
  deliverables: {
    taskId: string;
    path: string;
    submittedAt: string;
    submittedBy: string;
  }[];
  metadata?: {
    owner?: string;
    priority?: string;
    tags?: string[];
  };
}

export interface Pipeline {
  projectId: string;
  name: string;
  phases: {
    id: string;
    name: string;
    description?: string;
    tasks: Task[];
  }[];
  metadata?: {
    totalTasks: number;
    estimatedTotalHours?: number;
    criticalPath?: string[];
  };
}

export interface Task {
  id: string;
  name: string;
  expertId: string;
  description: string;
  dependencies?: string[];
  outputPath: string;
  estimatedHours?: number;
}

export interface Notification {
  id: string;
  projectId: string;
  taskId: string;
  agentId: string;
  expertId: string;
  deliverablePath: string;
  status: 'completed' | 'failed' | 'partial';
  timestamp: string;
  signature?: string;
  message?: string;
}

export interface NotificationAck {
  notificationId: string;
  status: 'received' | 'processing' | 'completed' | 'failed';
  message?: string;
  timestamp: string;
  agentSessionKey?: string;
}

export interface TaskProgress {
  taskId: string;
  status: 'completed' | 'failed' | 'partial';
  deliverablePath?: string;
  completedAt: string;
  completedBy: string;
}

export interface SessionInfo {
  sessionKey: string;
  agentId: string;
  expertId: string;
  createdAt: string;
  lastUsedAt: string;
  status: 'active' | 'idle' | 'error';
  lastHealthCheck?: string;
}

export interface SessionRegistry {
  [expertId: string]: SessionInfo;
}

export interface DispatchResult {
  success: boolean;
  error?: string;
  retryable: boolean;
}

export interface TaskFailure {
  taskId: string;
  projectId: string;
  reason: 'capability_gap' | 'temporary_error' | 'dependency_missing' | 'unknown';
  details: string;
  suggestion?: string;
  retryable: boolean;
}

// ============ Agent 状态相关 ============

/**
 * Agent 个人状态文件 (每个 agent 独立维护)
 * 路径：agents/{expertId}/status.json
 */
export interface AgentStatus {
  expertId: string;
  agentId: string;
  sessionKey: string;
  
  // 当前任务
  currentTask: {
    projectId: string;
    taskId: string;
    taskName: string;
    assignedAt: string;
    status: 'working' | 'blocked' | 'completed' | 'failed';
    progress: number;  // 0-100
    lastUpdate: string;
  } | null;
  
  // 历史任务记录
  taskHistory: Array<{
    projectId: string;
    taskId: string;
    taskName: string;
    status: 'completed' | 'failed' | 'partial';
    deliverablePath?: string;
    startedAt: string;
    completedAt: string;
    durationMinutes: number;
  }>;
  
  // 能力标签
  capabilities: string[];
  
  // 状态元数据
  lastHeartbeat: string;
  status: 'idle' | 'busy' | 'error' | 'offline';
  errorMessage?: string;
  updatedAt: string;
}

/**
 * Agent 工作区状态文件 (每个项目每个 agent 独立)
 * 路径：workspace/{projectId}/agent-status/{expertId}.json
 */
export interface AgentWorkspaceStatus {
  projectId: string;
  expertId: string;
  
  // RT 任务目录
  rtDirectory: string;
  
  // 当前工作阶段
  phase: 'research' | 'drafting' | 'reviewing' | 'finalizing' | 'submitting';
  
  // 工作产物
  drafts: string[];
  research: string[];
  deliverables: string[];
  
  // 状态日志
  log: Array<{
    timestamp: string;
    action: string;
    details?: string;
  }>;
  
  updatedAt: string;
}

// ============ 通知队列相关 ============

export interface QueuedNotification {
  queueId: string;
  notification: Notification;
  enqueuedAt: string;
  retryCount: number;
  lastAttemptAt?: string;
  error?: string;
}

export interface NotificationQueueState {
  pending: QueuedNotification[];
  processing: QueuedNotification[];
  completed: QueuedNotification[];
  failed: QueuedNotification[];
}
