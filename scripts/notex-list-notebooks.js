const fs = require('fs');
const path = require('path');
const https = require('https');

const PROD_NOTEX_HOST = 'notex.aishuo.co';
const PROD_NOTEX_BASE_URL = 'https://notex.aishuo.co/noteX';

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {};
  for (let i = 0; i < args.length; i += 1) {
    const key = args[i];
    if (!key.startsWith('--')) continue;
    const normalized = key.replace(/^--/, '');
    const next = args[i + 1];
    if (!next || next.startsWith('--')) {
      result[normalized] = 'true';
      continue;
    }
    result[normalized] = next;
    i += 1;
  }
  return result;
}

function requestJson(url, options = {}) {
  return new Promise((resolve, reject) => {
    const req = https.request(url, {
      method: options.method || 'GET',
      headers: options.headers || {},
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const payload = JSON.parse(data);
          if (!res.ok && payload.resultCode !== 1) {
            reject(new Error(payload.resultMsg || 'API error'));
          } else {
            resolve(payload);
          }
        } catch (e) {
          reject(new Error('响应解析失败：' + data.slice(0, 200)));
        }
      });
    });
    req.on('error', reject);
    if (options.body) req.write(options.body);
    req.end();
  });
}

function buildHeaders(accessToken) {
  return {
    'Content-Type': 'application/json',
    'access-token': accessToken,
  };
}

async function exchangeTokenByKey(cworkKey) {
  const url = `https://cwork-web.mediportal.com.cn/user/login/appkey?appCode=cms_gpt&appKey=${encodeURIComponent(cworkKey)}`;
  const response = await requestJson(url);
  
  if (!response.data || !response.data.xgToken) {
    throw new Error('CWork Key 换 token 失败');
  }
  
  return response.data.xgToken;
}

/**
 * 将数据保存到本地
 * 路径格式：notex/{sessionid}/RT01/年月日时分秒 xxx.md
 */
function saveToLocalFile(data, sessionId) {
  const session = sessionId || 'default_session';
  const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 14);
  const randomSuffix = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
  const filename = `${timestamp}${randomSuffix}.md`;
  
  // 获取当前工作目录下的 notex 目录
  const projectRoot = process.cwd();
  const dirPath = path.join(projectRoot, 'notex', session, 'RT01');
  
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
  
  const filePath = path.join(dirPath, filename);
  const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
  
  fs.writeFileSync(filePath, content, 'utf8');
  
  return path.relative(projectRoot, filePath);
}

async function listNotebooks(accessToken, baseUrl) {
  const url = `${baseUrl}/openapi/notebooks`;
  const response = await requestJson(url, {
    headers: buildHeaders(accessToken),
  });
  
  if (response.resultCode !== 1) {
    throw new Error(response.resultMsg || '查询笔记本失败');
  }
  
  return response.data;
}

function printUsage() {
  console.log(`
用法:
  node scripts/notex-list-notebooks.js --key <CWorkKey> [--session-id <id>]

可选参数:
  --key <CWorkKey>       CWork Key（必需）
  --session-id <id>      会话 ID（用于生成存储路径，默认 default_session）
  --base-url <url>       生产地址（默认 https://notex.aishuo.co/noteX）
`);
}

async function main() {
  const args = parseArgs();
  
  if (args.help || !args.key) {
    printUsage();
    if (!args.key) {
      throw new Error('缺少必需参数：--key');
    }
    return;
  }

  const baseUrl = args['base-url'] || PROD_NOTEX_BASE_URL;
  const sessionId = args['session-id'] || 'default_session';
  
  console.log('[auth] 正在换取 access-token...');
  const accessToken = await exchangeTokenByKey(args.key);
  console.log('[auth] 鉴权成功，token: ' + accessToken.slice(0, 8) + '...');
  
  console.log('[query] 正在获取笔记本列表...');
  const result = await listNotebooks(accessToken, baseUrl);
  
  // 保存到文件
  const relativePath = saveToLocalFile(result, sessionId);
  console.log('[save] 数据已保存至：' + relativePath);
  
  // 输出摘要
  console.log('\\n=== NoteX 笔记本列表 ===');
  console.log('总计：' + result.total + ' 个笔记本');
  console.log('当前页：' + result.page + '/' + Math.ceil(result.total / result.pageSize));
  console.log('\\n前 20 个笔记本：');
  result.items.forEach((nb, idx) => {
    console.log((idx + 1) + '. ' + nb.title + ' [' + nb.category + '] - ' + nb.sourceCount + ' 个来源');
  });
}

main().catch((error) => {
  console.error('\\n❌ ' + error.message);
  process.exit(1);
});
