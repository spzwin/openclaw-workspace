import { CHAT_CONFIG, resolveBuiltinAgents } from './config.js';

export const state = {
  ws: null,
  token: null,
  myUserId: '',
  currentConversationId: '',
  currentConversationType: 'group',
  conversations: [],
  messagesCache: [],
  unreadMap: new Map(),
  lastPreviewMap: new Map(),
  reconnectAttempt: 0,
  pollingTimer: null,
  convPollingTimer: null,
  reconnectTimer: null,
  wsManuallyClosed: false,
  isSending: false,
  lastFailedPayload: null,
  pendingDirect: null,
  mentionIndex: new Map(),
  mentionState: { list: [], active: 0, range: null }
};

export const keys = {
  contacts: 'xuanguan_contacts_v3',
  config: 'xuanguan_chat_config_v2',
  draftPrefix: 'xuanguan_draft_'
};

export const builtinAgents = resolveBuiltinAgents();

export function $(id) { return document.getElementById(id); }
export function esc(s) { return String(s || '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
export function now() { return Date.now(); }

export function loadConfig() {
  let c = {};
  try { c = JSON.parse(localStorage.getItem(keys.config) || '{}'); } catch { }
  const merged = { ...CHAT_CONFIG.defaults, ...c };
  $('apiUrl').value = merged.apiUrl;
  $('appId').value = merged.appId;
  $('appSecret').value = merged.appSecret;
  $('userId').value = merged.userId;
}

export function saveConfig() {
  const conf = {
    apiUrl: $('apiUrl').value.trim(),
    appId: $('appId').value.trim(),
    appSecret: $('appSecret').value.trim(),
    userId: $('userId').value.trim()
  };
  localStorage.setItem(keys.config, JSON.stringify(conf));
}

export function loadCustomContacts() {
  try { return JSON.parse(localStorage.getItem(keys.contacts) || '[]'); } catch { return []; }
}

export function saveContacts(customOnly) {
  localStorage.setItem(keys.contacts, JSON.stringify(customOnly || []));
}

export function loadContactsStore() {
  const custom = loadCustomContacts().map(x => ({ ...x, kind: x.kind || 'user' }));
  const merged = [...builtinAgents, ...custom];
  const m = new Map();
  for (const c of merged) if (c?.userId && !m.has(c.userId)) m.set(c.userId, c);
  return [...m.values()];
}

export function isBuiltinAgent(userId) {
  return builtinAgents.some(a => a.userId === userId);
}

export const MAX_DRAFT_LENGTH = 4000;
export function draftKey(convId) { return `${keys.draftPrefix}${convId || 'none'}`; }
export function saveDraft(text) {
  if (!state.currentConversationId) return;
  const value = String(text || '').slice(0, MAX_DRAFT_LENGTH);
  if (!value.trim()) {
    localStorage.removeItem(draftKey(state.currentConversationId));
    return;
  }
  localStorage.setItem(draftKey(state.currentConversationId), value);
}
export function loadDraft() {
  if (!state.currentConversationId) return '';
  const d = localStorage.getItem(draftKey(state.currentConversationId)) || '';
  return d.slice(0, MAX_DRAFT_LENGTH);
}

export function totalUnread() {
  let n = 0;
  state.unreadMap.forEach(v => (n += Number(v || 0)));
  return n;
}
