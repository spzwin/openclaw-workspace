#!/usr/bin/env node
/**
 * 导出最新会话到 QLM 文件夹
 * 用法：node scripts/export-session.js
 */

const fs = require('fs');
const path = require('path');

function findLatestSession() {
  const agentsDir = path.join(process.env.HOME, '.openclaw/agents/main/sessions');
  
  if (!fs.existsSync(agentsDir)) {
    console.error('❌ 会话目录不存在:', agentsDir);
    process.exit(1);
  }
  
  const files = fs.readdirSync(agentsDir)
    .filter(f => f.endsWith('.jsonl'))
    .map(f => ({
      name: f,
      path: path.join(agentsDir, f),
      mtime: fs.statSync(path.join(agentsDir, f)).mtimeMs
    }))
    .sort((a, b) => b.mtime - a.mtime);
  
  if (files.length === 0) {
    console.error('❌ 未找到会话文件');
    process.exit(1);
  }
  
  return files[0];
}

function exportSession() {
  const latest = findLatestSession();
  console.log('📖 读取最新会话:', latest.name);
  
  // 读取 JSONL 文件
  const lines = fs.readFileSync(latest.path, 'utf8').trim().split('\n');
  const messages = [];
  
  for (const line of lines) {
    if (line.trim()) {
      try {
        const obj = JSON.parse(line);
        // JSONL 格式：{"type":"message", "message": {"role": "...", "content": [...]}}
        if (obj.type === 'message' && obj.message && obj.message.role) {
          messages.push(obj.message);
        }
        // 或者直接是 role 在顶层
        else if (obj.role && ['user', 'assistant', 'toolResult'].includes(obj.role)) {
          messages.push(obj);
        }
      } catch (e) {
        console.error('解析失败:', e.message);
      }
    }
  }
  
  // 创建输出目录
  const outputDir = path.join(process.cwd(), 'QLM');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  // 生成时间戳
  const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
  
  // 写入完整数据
  const outputFile = path.join(outputDir, `session-history-${timestamp}.json`);
  const output = {
    sessionId: latest.name.replace('.jsonl', ''),
    channel: 'webchat',
    model: 'qwen3.5-plus',
    exportedAt: new Date().toISOString(),
    totalMessages: messages.length,
    messages: messages
  };
  
  fs.writeFileSync(outputFile, JSON.stringify(output, null, 2), 'utf8');
  console.log('✅ 会话已导出:', outputFile);
  
  // 更新 latest-session.json
  const latestFile = path.join(outputDir, 'latest-session.json');
  fs.writeFileSync(latestFile, JSON.stringify(output, null, 2), 'utf8');
  console.log('🔄 已更新:', latestFile);
  
  // 输出统计
  console.log('\n📊 统计:');
  console.log('  总消息数:', messages.length);
  console.log('  用户消息:', messages.filter(m => m.role === 'user').length);
  console.log('  AI 回复:', messages.filter(m => m.role === 'assistant').length);
  console.log('  工具调用:', messages.filter(m => m.role === 'toolResult').length);
  console.log('  文件大小:', (fs.statSync(outputFile).size / 1024).toFixed(2), 'KB');
  
  // 输出查看器地址
  console.log('\n🌐 查看器地址:');
  console.log('  file://' + outputFile.replace(process.env.HOME, '~'));
  console.log('\n👉 打开浏览器查看:');
  console.log('  open ' + path.join(outputDir, 'viewer.html'));
}

exportSession();
