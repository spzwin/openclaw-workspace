const http = require('http');
const fs = require('fs');
const path = require('path');

const WORKSPACE_ROOT = '/Users/spzhong/.openclaw/workspace/proj-system';
const PORT = 3456;

// 读取 JSON 文件（安全处理）
function readJsonFile(filePath) {
  try {
    if (!fs.existsSync(filePath)) return null;
    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content);
  } catch (e) {
    return null;
  }
}

// 获取所有项目
function getProjects() {
  const workspacePath = path.join(WORKSPACE_ROOT, 'workspace');
  if (!fs.existsSync(workspacePath)) return [];
  
  const projects = [];
  const items = fs.readdirSync(workspacePath);
  
  for (const item of items) {
    const projectPath = path.join(workspacePath, item);
    if (fs.statSync(projectPath).isDirectory()) {
      const projectJson = readJsonFile(path.join(projectPath, 'project.json'));
      if (projectJson) {
        projects.push({
          ...projectJson,
          path: item
        });
      }
    }
  }
  return projects;
}

// 获取所有 Agent 列表
function getAgents() {
  const agentsPath = path.join(WORKSPACE_ROOT, 'agents');
  const agents = [];
  
  if (fs.existsSync(agentsPath)) {
    const agentDirs = fs.readdirSync(agentsPath);
    for (const agentDir of agentDirs) {
      const agentPath = path.join(agentsPath, agentDir);
      if (fs.statSync(agentPath).isDirectory()) {
        const status = readJsonFile(path.join(agentPath, 'status.json'));
        agents.push({
          id: agentDir,
          status: status || { status: 'unknown' }
        });
      }
    }
  }
  return agents;
}

// 获取项目详情（包含各 agent 状态）
function getProjectDetails(projectId) {
  const projectPath = path.join(WORKSPACE_ROOT, 'workspace', projectId);
  if (!fs.existsSync(projectPath)) return null;
  
  const project = readJsonFile(path.join(projectPath, 'project.json'));
  const pipeline = readJsonFile(path.join(projectPath, 'pipeline.json'));
  
  // 获取所有 agent 状态
  const agentsPath = path.join(WORKSPACE_ROOT, 'agents');
  const agentStatuses = {};
  
  if (fs.existsSync(agentsPath)) {
    const agentDirs = fs.readdirSync(agentsPath);
    for (const agentDir of agentDirs) {
      const statusFile = path.join(agentsPath, agentDir, 'status.json');
      const status = readJsonFile(statusFile);
      if (status) {
        agentStatuses[agentDir] = status;
      }
    }
  }
  
  // 获取项目下的产出文件（根目录）
  const rootDeliverables = getDeliverablesInPath(projectPath, ['project.json', 'pipeline.json']);
  
  return {
    project,
    pipeline,
    agentStatuses,
    rootDeliverables
  };
}

// 获取指定目录下的交付文件
function getDeliverablesInPath(dirPath, excludeFiles = []) {
  const deliverables = [];
  if (!fs.existsSync(dirPath)) return deliverables;
  
  const items = fs.readdirSync(dirPath);
  for (const item of items) {
    const itemPath = path.join(dirPath, item);
    if (fs.statSync(itemPath).isFile() && 
        (item.endsWith('.md') || item.endsWith('.json') || item.endsWith('.txt')) &&
        !excludeFiles.includes(item)) {
      deliverables.push({
        name: item,
        path: itemPath,
        size: fs.statSync(itemPath).size,
        modified: fs.statSync(itemPath).mtime
      });
    }
  }
  return deliverables;
}

// 获取指定 Agent 在项目下的产出文件
function getAgentDeliverables(projectId, agentId) {
  // 路径：workspace/{projectId}/{agentId}/ 或 workspace/{projectId}/agents/{agentId}/
  const possiblePaths = [
    path.join(WORKSPACE_ROOT, 'workspace', projectId, agentId),
    path.join(WORKSPACE_ROOT, 'workspace', projectId, 'agents', agentId),
    path.join(WORKSPACE_ROOT, 'agents', agentId, 'workspace', projectId)
  ];
  
  for (const checkPath of possiblePaths) {
    if (fs.existsSync(checkPath)) {
      const deliverables = getDeliverablesInPath(checkPath);
      // 递归查找子目录
      const subDeliverables = getDeliverablesFromSubdirs(checkPath);
      return [...deliverables, ...subDeliverables];
    }
  }
  
  return [];
}

// 递归获取子目录中的文件
function getDeliverablesFromSubdirs(basePath) {
  const deliverables = [];
  
  function scanDir(dirPath) {
    if (!fs.existsSync(dirPath)) return;
    const items = fs.readdirSync(dirPath);
    for (const item of items) {
      const itemPath = path.join(dirPath, item);
      const stat = fs.statSync(itemPath);
      if (stat.isFile() && 
          (item.endsWith('.md') || item.endsWith('.json') || item.endsWith('.txt'))) {
        deliverables.push({
          name: item,
          path: itemPath,
          relativePath: path.relative(basePath, itemPath),
          size: stat.size,
          modified: stat.mtime
        });
      } else if (stat.isDirectory() && !item.startsWith('.')) {
        scanDir(itemPath);
      }
    }
  }
  
  scanDir(basePath);
  return deliverables;
}

// 分析工作流状态（基于 pipeline 和实际文件）
function analyzeWorkflowState(pipeline, project, deliverables) {
  if (!pipeline || !pipeline.phases) return null;
  
  const state = {
    phases: [],
    currentPhase: project?.progress?.currentPhase || null,
    completedTasks: project?.progress?.completedTasks || [],
    pendingTasks: project?.progress?.pendingTasks || []
  };
  
  // 检查每个 phase 的完成情况
  pipeline.phases.forEach((phase, phaseIndex) => {
    const phaseState = {
      ...phase,
      index: phaseIndex,
      status: 'pending',
      tasks: phase.tasks.map(task => {
        // 检查任务输出文件是否存在
        const isCompleted = state.completedTasks.includes(task.id);
        const isPending = state.pendingTasks.includes(task.id);
        const isCurrent = state.currentPhase === phase.id && !isCompleted;
        
        return {
          ...task,
          status: isCompleted ? 'completed' : (isCurrent ? 'active' : 'pending')
        };
      })
    };
    
    // 判断 phase 状态
    const allTasksCompleted = phaseState.tasks.every(t => t.status === 'completed');
    const hasActiveTask = phaseState.tasks.some(t => t.status === 'active');
    
    if (allTasksCompleted) {
      phaseState.status = 'completed';
    } else if (hasActiveTask) {
      phaseState.status = 'active';
    } else if (phaseIndex === 0 || pipeline.phases[phaseIndex - 1].status === 'completed') {
      phaseState.status = 'active';
    }
    
    state.phases.push(phaseState);
  });
  
  // 预测下一步
  state.nextStep = predictNextStep(state);
  
  return state;
}

// 预测下一步
function predictNextStep(state) {
  // 查找第一个非 completed 的 task
  for (const phase of state.phases) {
    for (const task of phase.tasks) {
      if (task.status !== 'completed') {
        return {
          phaseId: phase.id,
          phaseName: phase.name,
          taskId: task.id,
          taskName: task.name,
          expertId: task.expertId
        };
      }
    }
  }
  return null;
}

// API 路由
const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Content-Type', 'application/json');
  
  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  if (url.pathname === '/api/projects') {
    res.end(JSON.stringify(getProjects()));
  } else if (url.pathname === '/api/agents') {
    res.end(JSON.stringify(getAgents()));
  } else if (url.pathname.startsWith('/api/project/')) {
    const parts = url.pathname.split('/');
    const projectId = parts[3];
    
    // /api/project/{id}/workflow
    if (parts[4] === 'workflow') {
      const details = getProjectDetails(projectId);
      if (!details) {
        res.end(JSON.stringify({ error: 'Project not found' }));
        return;
      }
      const workflowState = analyzeWorkflowState(
        details.pipeline,
        details.project,
        details.rootDeliverables
      );
      res.end(JSON.stringify(workflowState || { error: 'No pipeline' }));
    }
    // /api/project/{id}/deliverables
    else if (parts[4] === 'deliverables') {
      const agentId = parts[5];
      if (agentId) {
        const deliverables = getAgentDeliverables(projectId, agentId);
        res.end(JSON.stringify(deliverables));
      } else {
        const details = getProjectDetails(projectId);
        res.end(JSON.stringify(details?.rootDeliverables || []));
      }
    } else {
      const details = getProjectDetails(projectId);
      res.end(JSON.stringify(details || { error: 'Project not found' }));
    }
  } else if (url.pathname === '/') {
    // 服务静态页面
    res.setHeader('Content-Type', 'text/html');
    const htmlPath = path.join(__dirname, 'index.html');
    if (fs.existsSync(htmlPath)) {
      res.end(fs.readFileSync(htmlPath, 'utf-8'));
    } else {
      res.statusCode = 404;
      res.end('index.html not found');
    }
  } else {
    res.statusCode = 404;
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(PORT, () => {
  console.log(`🔍 Agent Monitor running at http://localhost:${PORT}`);
  console.log(`📊 Workspace: ${WORKSPACE_ROOT}`);
});
