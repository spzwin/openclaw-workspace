import { $, state } from './state.js';

export const ERROR_TEXT = {
  timeout: '请求超时，请检查网络后重试',
  network: '网络连接失败，请检查服务或网络',
  auth: '鉴权失败，请检查 appId/appSecret',
  permission: '没有权限执行该操作',
  tokenExpired: '登录状态已过期，请重新连接',
  server: '服务返回异常，请稍后重试'
};

export const ERROR_CODE_MAP = {
  '401': ERROR_TEXT.auth,
  '403': ERROR_TEXT.permission,
  'token-expired': ERROR_TEXT.tokenExpired,
  'token_invalid': ERROR_TEXT.auth,
  'permission-denied': ERROR_TEXT.permission,
  'timeout': ERROR_TEXT.timeout,
  'network': ERROR_TEXT.network
};

function mapServerError(data = {}) {
  const code = String(data?.code ?? '');
  const raw = String(data?.message || '').toLowerCase();
  if (ERROR_CODE_MAP[code]) return ERROR_CODE_MAP[code];
  if (/token.*expired|expired.*token/.test(raw)) return ERROR_TEXT.tokenExpired;
  if (/permission|forbidden|denied|权限/.test(raw)) return ERROR_TEXT.permission;
  if (/auth|unauthorized|token|鉴权|认证/.test(raw)) return ERROR_TEXT.auth;
  return data?.message || ERROR_TEXT.server;
}

export function getUserError(input) {
  if (typeof input === 'string') return input;
  if (input && typeof input === 'object' && 'code' in input) return mapServerError(input);
  if (input instanceof Error) return normalizeError(input);
  return ERROR_TEXT.server;
}

function normalizeError(e, fallback = ERROR_TEXT.server) {
  if (!e) return fallback;
  if (e.name === 'AbortError') return ERROR_TEXT.timeout;
  if (e instanceof TypeError) return ERROR_TEXT.network;
  const msg = String(e.message || fallback);
  if (/401|403|auth|token|鉴权|认证/i.test(msg)) return ERROR_TEXT.auth;
  return msg;
}

function withTimeout(ms = 12000) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  return { signal: c.signal, done: () => clearTimeout(t) };
}

export async function auth() {
  const t = withTimeout();
  try {
    const res = await fetch(`${$('apiUrl').value.trim()}/oauth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ appId: $('appId').value.trim(), appSecret: $('appSecret').value.trim(), grantType: 'client_credentials' }),
      signal: t.signal
    });
    const data = await res.json();
    if (data.code !== 0) throw new Error(mapServerError(data));
    state.token = data.data.accessToken;
    return state.token;
  } catch (e) {
    throw new Error(normalizeError(e, ERROR_TEXT.auth));
  } finally { t.done(); }
}

export function assertApiOk(data, fallback = ERROR_TEXT.server) {
  if (data?.code === 0) return data;
  throw new Error(getUserError(data) || fallback);
}

export async function api(path, method = 'POST', body) {
  if (!state.token) await auth();
  const t = withTimeout();
  try {
    const res = await fetch(`${$('apiUrl').value.trim()}${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${state.token}` },
      body: method === 'GET' ? undefined : JSON.stringify(body || {}),
      signal: t.signal
    });
    const data = await res.json();
    if (data.code === 401 || data.code === 403) state.token = null;
    return data;
  } catch (e) {
    throw new Error(normalizeError(e));
  } finally { t.done(); }
}

export function connectWebSocket({ onOpen, onClose, onError, onMessage }) {
  const wsUrl = $('apiUrl').value.trim().replace('http', 'ws') + `/ws/messages?appId=${encodeURIComponent($('appId').value.trim())}&accountId=${encodeURIComponent(state.myUserId)}&token=${encodeURIComponent(state.token)}`;
  if (state.ws) { try { state.ws.close(); } catch {} }
  state.ws = new WebSocket(wsUrl);
  state.ws.onopen = onOpen;
  state.ws.onclose = onClose;
  state.ws.onerror = onError;
  state.ws.onmessage = onMessage;
}

export function disconnectWebSocket() {
  if (state.ws) {
    try { state.ws.close(); } catch {}
  }
  state.ws = null;
}

export function startPolling({ onPollMessages, onPollConversations }) {
  stopPolling();
  state.pollingTimer = setInterval(onPollMessages, 5000);
  state.convPollingTimer = setInterval(onPollConversations, 12000);
}

export function stopPolling() {
  if (state.pollingTimer) clearInterval(state.pollingTimer);
  if (state.convPollingTimer) clearInterval(state.convPollingTimer);
  state.pollingTimer = null;
  state.convPollingTimer = null;
}
