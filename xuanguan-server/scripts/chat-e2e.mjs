#!/usr/bin/env node
/**
 * 最小 e2e：创建群 -> @提及 -> 发送 -> 刷新回显
 * 用法：npm run chat:e2e
 */

const API = process.env.CHAT_E2E_API_URL || process.env.API_URL || 'http://localhost:3001';
const APP_ID = process.env.CHAT_E2E_APP_ID || process.env.APP_ID || 'cli_xxxxxxxxxxxxxxxx';
const APP_SECRET = process.env.CHAT_E2E_APP_SECRET || process.env.APP_SECRET || 'your_app_secret_here_change_in_production';
const USER_ID = process.env.CHAT_E2E_USER_ID || 'e2e_user';

const AGENTS = [
  { userId: process.env.CHAT_E2E_AGENT_CODER || 'coder', display: '码爪（coder）' },
  { userId: process.env.CHAT_E2E_AGENT_RESEARCHER || 'researcher', display: '研爪（researcher）' },
  { userId: process.env.CHAT_E2E_AGENT_ATLAS || 'atlas', display: 'Atlas（atlas）' }
];

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

async function req(path, method = 'GET', body, token) {
  const res = await fetch(`${API}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: method === 'GET' ? undefined : JSON.stringify(body || {})
  });
  return res.json();
}

(async () => {
  console.log('[e2e] 1) auth');
  const auth = await req('/oauth/token', 'POST', { appId: APP_ID, appSecret: APP_SECRET, grantType: 'client_credentials' });
  assert(auth.code === 0 && auth.data?.accessToken, `auth failed: ${auth.message || auth.code}`);
  const token = auth.data.accessToken;

  console.log('[e2e] 2) create group');
  const members = [USER_ID, ...AGENTS.map(a => a.userId)];
  const create = await req('/api/v1/message/conversations', 'POST', {
    type: 'group',
    title: `e2e_group_${Date.now()}`,
    members,
    createdBy: USER_ID
  }, token);
  assert(create.code === 0, `create group failed: ${create.message || create.code}`);
  const convId = create.data?.conversationId || create.data?.id;
  assert(convId, 'conversationId missing');

  console.log('[e2e] 3) send @ mention message');
  const text = `@${AGENTS[0].userId} e2e ping`;
  const mentionRaw = `@${AGENTS[0].userId}`;
  const send = await req('/api/v1/message/inbound/send', 'POST', {
    conversationId: convId,
    conversationType: 'group',
    msgType: 'text',
    senderId: USER_ID,
    senderName: USER_ID,
    content: {
      type: 'text',
      text,
      mentions: [{ userId: AGENTS[0].userId, display: AGENTS[0].display }],
      mentionTokens: [{ type: 'mention', userId: AGENTS[0].userId, display: AGENTS[0].display, start: 0, end: mentionRaw.length, raw: mentionRaw }]
    }
  }, token);
  assert(send.code === 0, `send failed: ${send.message || send.code}`);

  console.log('[e2e] 4) refresh messages and verify echo');
  const list = await req(`/api/v1/message/conversations/${encodeURIComponent(convId)}/messages?limit=20`, 'GET', undefined, token);
  assert(list.code === 0, `load messages failed: ${list.message || list.code}`);
  const msgs = list.data || [];
  const hit = msgs.find(m => (m?.content?.text || '').includes('e2e ping'));
  assert(hit, 'message echo not found');
  assert(Array.isArray(hit.content?.mentions) && hit.content.mentions.length > 0, 'mentions missing in echo');
  assert(Array.isArray(hit.content?.mentionTokens) && hit.content.mentionTokens.length > 0, 'mentionTokens missing in echo');

  console.log('[e2e] ✅ PASS');
})().catch(e => {
  console.error('[e2e] ❌ FAIL:', e.message);
  process.exit(1);
});
