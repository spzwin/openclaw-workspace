import { $, state, esc, now, saveConfig, loadConfig, loadContactsStore, loadCustomContacts, saveContacts, isBuiltinAgent, saveDraft, loadDraft, totalUnread, MAX_DRAFT_LENGTH } from './state.js';
import { api, auth, assertApiOk, connectWebSocket, disconnectWebSocket, startPolling, stopPolling } from './api.js';
import { renderGroupAgentPicker, buildGroupMembers } from './group-builder.js';
import { wireMention, extractMentions, renderWithMentions } from './mention.js';
import { buildMessageContent, validateConversation, validateMessage } from './dto.js';

const channelSync = 'BroadcastChannel' in window ? new BroadcastChannel('xuanguan_chat_sync') : null;
const tabId = `tab_${Math.random().toString(36).slice(2, 8)}`;
const syncKey = 'xuanguan_chat_sync_v24';

const VIRTUAL = {
  contacts: { itemHeight: 70, overscan: 6 },
  convs: { itemHeight: 80, overscan: 6 },
  msgs: { itemHeight: 90, overscan: 12 }
};

function toast(msg) {
  const t = $('toast');
  t.textContent = msg;
  t.style.display = 'block';
  setTimeout(() => (t.style.display = 'none'), 1800);
}

function warnDto(scope, issues) { if (issues?.length) console.warn(`[chat-dto:${scope}]`, issues.join(', ')); }

function setConn(type, text) {
  $('statusText').textContent = text;
  $('dot').className = `status-dot${type === 'ok' ? ' ok' : type === 'reconnecting' ? ' recon' : type === 'down' ? ' err' : ''}`;
  $('wsState').textContent = `WS: ${type === 'ok' ? '在线' : type === 'reconnecting' ? '重连中' : '断开'}`;

  if (type === 'ok') {
    $('loginScreen').style.display = 'none';
    $('mainApp').style.display = 'grid';
    if (state.myUserId) {
      $('userAvatar').textContent = state.myUserId.slice(0, 1).toUpperCase();
    }
  }
}

function setSendState(v) { $('sendState').textContent = `发送状态: ${v}`; }
function setSending(v) { state.isSending = v; $('sendBtn').disabled = v; $('sendBtn').textContent = v ? '...' : '🚀'; }

function updateDocTitle() {
  const n = totalUnread();
  document.title = n > 0 ? `(${n}) 玄关` : '玄关';
  const badge = $('totalUnread');
  if (badge) {
    badge.textContent = n > 99 ? '99+' : n;
    badge.style.display = n > 0 ? 'block' : 'none';
  }
}

function previewText(m) { return (m?.content?.text || '').replace(/\s+/g, ' ').slice(0, 50) || '[空消息]'; }

function broadcastSync(payload) {
  const data = { ...payload, fromTab: tabId, ts: Date.now() };
  try { if (channelSync) channelSync.postMessage(data); } catch { }
  try { localStorage.setItem(syncKey, JSON.stringify(data)); } catch { }
}

function renderVirtualList({ container, items, itemHeight, overscan = 6, renderRange }) {
  const total = items.length;
  const viewH = container.clientHeight || 600;
  const scrollTop = container.scrollTop || 0;
  const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const count = Math.ceil(viewH / itemHeight) + overscan * 2;
  const end = Math.min(total, start + count);
  const top = start * itemHeight;
  const bottom = Math.max(0, (total - end) * itemHeight);
  renderRange(start, end, top, bottom);
}

function updateNotifyState() {
  const text = !('Notification' in window)
    ? '不支持'
    : Notification.permission === 'granted'
      ? '已开启'
      : Notification.permission === 'denied'
        ? '已拒绝'
        : '未授权';
  $('btnNotify').textContent = `通知权限: ${text}`;
}

function mentionCandidates(q = '') {
  const conv = state.conversations.find(c => c.conversationId === state.currentConversationId);
  const members = (conv?.members || []).map(id => ({ userId: id, name: id, kind: 'member' }));
  const contacts = loadContactsStore();
  const m = new Map();
  for (const c of [...members, ...contacts]) {
    if (!c?.userId || c.userId === state.myUserId) continue;
    if (!m.has(c.userId)) m.set(c.userId, c);
  }
  const arr = [...m.values()];
  state.mentionIndex = new Map(arr.map(x => [x.userId, x]));
  if (!q) return arr;
  return arr.filter(x => x.userId.toLowerCase().includes(q) || (x.name || '').toLowerCase().includes(q));
}

function renderContacts() {
  const kw = ($('contactSearch').value || '').trim().toLowerCase();
  const all = loadContactsStore();
  const list = kw ? all.filter(c => c.userId.toLowerCase().includes(kw) || (c.name || '').toLowerCase().includes(kw)) : all;
  const box = $('contactList');
  if (!list.length) { box.innerHTML = '<div class="hint" style="text-align:center; padding:20px;">暂无匹配联系人</div>'; return; }

  renderVirtualList({
    container: box,
    items: list,
    itemHeight: VIRTUAL.contacts.itemHeight,
    overscan: VIRTUAL.contacts.overscan,
    renderRange: (start, end, top, bottom) => {
      let html = `<div style="height:${top}px"></div>`;
      for (let i = start; i < end; i++) {
        const c = list[i];
        const builtin = isBuiltinAgent(c.userId);
        html += `
          <div class="item" data-open-item="${esc(c.userId)}">
            <div class="item-avatar">${esc((c.name || c.userId).slice(0, 1).toUpperCase())}</div>
            <div class="item-info">
              <div class="item-name">${esc(c.name || c.userId)}</div>
              <div class="item-preview">${esc(c.userId)}${builtin ? ' · Agent' : ''}</div>
            </div>
            <div class="item-actions">
               <button class="login-btn" style="width:auto; padding:2px 8px; font-size:11px;" data-open="${esc(c.userId)}">发消息</button>
            </div>
          </div>`;
      }
      html += `<div style="height:${bottom}px"></div>`;
      box.innerHTML = html;
    }
  });
}

function renderConversations() {
  const kw = ($('convSearch').value || '').trim().toLowerCase();
  const list = kw ? state.conversations.filter(c => (c.title || '').toLowerCase().includes(kw) || c.conversationId.toLowerCase().includes(kw)) : state.conversations;
  const box = $('convList');
  if (!list.length) { box.innerHTML = '<div class="hint" style="text-align:center; padding:20px;">暂无匹配会话</div>'; return; }

  renderVirtualList({
    container: box,
    items: list,
    itemHeight: VIRTUAL.convs.itemHeight,
    overscan: VIRTUAL.convs.overscan,
    renderRange: (start, end, top, bottom) => {
      let html = `<div style="height:${top}px"></div>`;
      for (let i = start; i < end; i++) {
        const c = list[i];
        const isActive = c.conversationId === state.currentConversationId;
        const unread = isActive ? 0 : (state.unreadMap.get(c.conversationId) || 0);
        const last = state.lastPreviewMap.get(c.conversationId) || c.lastMessagePreview || '';
        const time = c.updatedAt ? new Date(Number(c.updatedAt)).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
        html += `
          <div class="item${c.conversationId === state.currentConversationId ? ' active' : ''}" data-conv-id="${esc(c.conversationId)}">
            <div class="item-avatar">${esc((c.title || c.conversationId).slice(0, 1).toUpperCase())}</div>
            <div class="item-info">
              <div class="item-top">
                <div class="item-name">${esc(c.title || c.conversationId)}</div>
                <div class="item-time">${time}</div>
              </div>
              <div class="item-preview">${esc(last || '...')}</div>
            </div>
            ${unread > 0 ? `<div class="badge">${unread > 99 ? '99+' : unread}</div>` : ''}
          </div>`;
      }
      html += `<div style="height:${bottom}px"></div>`;
      box.innerHTML = html;
    }
  });
  updateDocTitle();
}

function isNearBottom() {
  const box = $('msgs');
  return box.scrollHeight - box.scrollTop - box.clientHeight < 120;
}
function scrollToBottom(force = false) {
  const box = $('msgs');
  if (force || isNearBottom()) box.scrollTop = box.scrollHeight;
  $('jumpNew').style.display = 'none';
}

function renderMessageHtml(m) {
  const c = m.content || {};
  const text = c.text || '';
  const mentions = c.mentions || [];
  const mentionTokens = c.mentionTokens || [];
  return renderWithMentions(text, mentions, mentionTokens);
}

function renderMessages(list) {
  const box = $('msgs');
  const stick = isNearBottom();
  if (!list.length) { box.innerHTML = '<div class="hint" style="text-align:center; padding-top:40px;">该会话还没有消息</div>'; return; }

  renderVirtualList({
    container: box,
    items: list,
    itemHeight: VIRTUAL.msgs.itemHeight,
    overscan: VIRTUAL.msgs.overscan,
    renderRange: (start, end, top, bottom) => {
      let html = `<div style="height:${top}px"></div>`;
      for (let i = start; i < end; i++) {
        const m = list[i];
        const me = m.senderId === state.myUserId;
        const time = new Date(Number(m.timestamp || now())).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        let senderName = m.senderName || m.senderId || '';
        let isSystem = false;

        if (m.content?.type === 'text') {
          const plainText = m.content.text || '';
          if (plainText.startsWith('[系统]') || plainText.startsWith('【系统】')) {
            isSystem = true;
          }
        }

        if (isSystem) {
          const sysText = esc(m.content?.text || '');
          html += `<div class="msg-group-time" style="margin:20px auto; text-align:center;">${sysText}</div>`;
        } else {
          let htmlContent = renderMessageHtml(m);

          if (m.content?.type === 'text') {
            const plainText = m.content.text || '';
            const match = plainText.match(/^【(.*?)】\s*/);
            if (match) {
              senderName = match[1];
              const escapedPrefix = esc(match[0]);
              if (htmlContent.startsWith(escapedPrefix)) {
                htmlContent = htmlContent.substring(escapedPrefix.length);
              }
            } else if (state.currentConversationType === 'single') {
              // Strip auto-mention prefix in single chat: @otherId\n or @otherId
              const conv = state.conversations.find(c => c.conversationId === state.currentConversationId);
              const otherId = (conv?.members || []).find(id => id !== state.myUserId) || conv?.conversationId;
              if (otherId) {
                const mentionPrefix = `<span class="pill" data-mention="${esc(otherId)}" title="${esc(state.mentionIndex?.get(otherId)?.name || otherId)}">@${esc(state.mentionIndex?.get(otherId)?.name || otherId)}</span>`;
                if (htmlContent.startsWith(mentionPrefix + '<br/>')) {
                  htmlContent = htmlContent.substring(mentionPrefix.length + 5);
                } else if (htmlContent.startsWith(mentionPrefix + ' ')) {
                  htmlContent = htmlContent.substring(mentionPrefix.length + 1);
                } else if (htmlContent === mentionPrefix) {
                  htmlContent = '';
                }
              }
            }
          }

          html += `
             <div class="message ${me ? 'me' : ''}">
               <div class="msg-bubble">${htmlContent}</div>
               <div class="msg-meta">
                  ${!me ? `<span>${esc(senderName)}</span>` : ''}
                  <span>${time}</span>
               </div>
             </div>`;
        }
      }
      html += `<div style="height:${bottom}px"></div>`;
      box.innerHTML = html;
    }
  });

  if (stick) box.scrollTop = box.scrollHeight;
}

async function loadMessages(conversationId) {
  const data = assertApiOk(await api(`/api/v1/message/conversations/${encodeURIComponent(conversationId)}/messages?limit=200`, 'GET'));
  state.messagesCache = (data.data || []).map(x => {
    const r = validateMessage(x);
    if (!r.ok) warnDto('message', r.issues);
    return r.data;
  });
  if (conversationId === state.currentConversationId) renderMessages(state.messagesCache);
  const last = state.messagesCache[state.messagesCache.length - 1];
  if (last) state.lastPreviewMap.set(conversationId, `${last.senderName || last.senderId}: ${previewText(last)}`);
}

async function loadConversations() {
  const uid = $('userId').value.trim();
  const data = assertApiOk(await api(`/api/v1/message/conversations?userId=${encodeURIComponent(uid)}`, 'GET'));
  state.conversations = (data.data || []).map(x => {
    const r = validateConversation(x);
    if (!r.ok) warnDto('conversation', r.issues);
    return r.data;
  }).sort((a, b) => Number(b.updatedAt || 0) - Number(a.updatedAt || 0));
  renderConversations();
  if (!state.currentConversationId && state.conversations.length) await selectConversation(state.conversations[0].conversationId);
}

async function selectConversation(conversationId) {
  const c = state.conversations.find(x => x.conversationId === conversationId);
  if (!c) return;
  state.currentConversationId = c.conversationId;
  state.currentConversationType = c.type;
  state.unreadMap.set(c.conversationId, 0);
  broadcastSync({ type: 'active-conversation', conversationId: c.conversationId });
  broadcastSync({ type: 'unread-sync', unread: Object.fromEntries(state.unreadMap.entries()) });

  $('chatTitle').textContent = c.title || c.conversationId;
  $('selectedConv').textContent = `ID: ${c.conversationId.slice(0, 8)}...`;

  renderConversations();
  await loadMessages(c.conversationId);
  const draft = loadDraft();
  $('text').value = draft;
  $('draftCount').textContent = `${draft.length} 字`;
  scrollToBottom(true);
}

function addContact() {
  const userId = $('contactId').value.trim();
  const name = $('contactName').value.trim();
  if (!userId) return toast('请填写 userId');
  const custom = loadCustomContacts();
  if (loadContactsStore().some(x => x.userId === userId)) return toast('联系人已存在');
  custom.unshift({ userId, name, kind: 'user' });
  saveContacts(custom);
  renderContacts();
  $('contactId').value = ''; $('contactName').value = '';
  if (window.closeModal) window.closeModal('contactModal');
  toast('已添加联系人');
}

async function createDirectFromInput() {
  const to = state.pendingDirect;
  if (!to) return;
  const me = $('userId').value.trim();
  const data = assertApiOk(await api('/api/v1/message/inbound/send', 'POST', { toUserId: to, msgType: 'text', content: { type: 'text', text: '[系统] 私聊会话已创建' }, senderId: me, senderName: me }));
  await loadConversations();
  if (data.data?.conversationId) await selectConversation(data.data.conversationId);
  state.pendingDirect = null;
}

async function createGroup() {
  const me = $('userId').value.trim();
  const { members } = buildGroupMembers(me);
  if (members.length < 2) return toast('请至少选择 1 个成员');
  const data = assertApiOk(await api('/api/v1/message/conversations', 'POST', {
    type: 'group',
    title: $('groupTitle').value.trim() || `群聊_${Date.now().toString().slice(-4)}`,
    members,
    createdBy: me
  }));
  if (window.closeModal) window.closeModal('groupModal');
  await loadConversations();
  await selectConversation(data.data.conversationId || data.data?.id || members[0]);
}

function handleIncomingMessage(rawMsg, fromSync = false) {
  const parsed = validateMessage(rawMsg || {});
  if (!parsed.ok) warnDto('incoming', parsed.issues);
  const msg = parsed.data;
  if (!msg?.conversationId) return;
  const isCurrent = msg.conversationId === state.currentConversationId;
  if (isCurrent) {
    const stick = isNearBottom();
    state.unreadMap.set(msg.conversationId, 0); // Active conversation has no unread
    state.messagesCache.push(msg);
    renderMessages(state.messagesCache);
    if (stick) scrollToBottom(true); else $('jumpNew').style.display = 'block';
  } else {
    state.unreadMap.set(msg.conversationId, (state.unreadMap.get(msg.conversationId) || 0) + 1);
  }
  state.lastPreviewMap.set(msg.conversationId, `${msg.senderName || msg.senderId}: ${previewText(msg)}`);
  if (!fromSync) broadcastSync({ type: 'incoming-message', message: msg });
  broadcastSync({ type: 'unread-sync', unread: Object.fromEntries(state.unreadMap.entries()) });
  renderConversations();
}

async function sendMessage(payloadOverride = null) {
  if (!state.currentConversationId) return toast('请先选择会话');
  if (state.isSending) return;
  let text = payloadOverride?.text ?? $('text').value.trim();
  if (!text) return;

  try {
    setSending(true); setSendState('sending');
    const role = payloadOverride?.role ?? $('sendRole')?.value ?? 'user';
    const msgType = payloadOverride?.msgType ?? $('msgType')?.value ?? 'text';

    // Auto-mention logic for single chats (silent frontend, explicit backend)
    const conv = state.conversations.find(c => c.conversationId === state.currentConversationId);
    if (conv && conv.type === 'single' && !payloadOverride) {
      const otherId = (conv.members || []).find(id => id !== state.myUserId) || conv.conversationId;
      if (!text.includes(`@${otherId}`)) {
        text = `@${otherId}\n${text}`;
      }
    }

    const { mentions: mentionsToUse, mentionTokens: tokensToUse } = extractMentions(text, state.mentionIndex);
    const content = buildMessageContent({ type: msgType, text, mentions: mentionsToUse, mentionTokens: tokensToUse });

    assertApiOk(
      role === 'user'
        ? await api('/api/v1/message/inbound/send', 'POST', { conversationId: state.currentConversationId, conversationType: state.currentConversationType, msgType, content, senderId: state.myUserId, senderName: state.myUserId })
        : await api('/api/v1/message/send', 'POST', { conversationId: state.currentConversationId, conversationType: state.currentConversationType, msgType, content })
    );
    state.lastFailedPayload = null;
    $('retryBtn').style.display = 'none';
    $('text').value = ''; $('draftCount').textContent = '0 字'; saveDraft('');
    broadcastSync({ type: 'draft-sync', conversationId: state.currentConversationId, draft: '' });
    await loadMessages(state.currentConversationId);
    scrollToBottom(true); setSendState('已发送');
  } catch (e) {
    state.lastFailedPayload = { text: $('text').value.trim(), role: $('sendRole')?.value || 'user', msgType: $('msgType')?.value || 'text' };
    $('retryBtn').style.display = state.lastFailedPayload.text ? 'inline-block' : 'none';
    setSendState('失败'); toast(`发送失败：${e.message}`);
  } finally { setSending(false); }
}

function retryLastFailed() { if (!state.lastFailedPayload?.text) return toast('没有可重试内容'); sendMessage(state.lastFailedPayload); }

function scheduleReconnect() {
  if (state.wsManuallyClosed || state.reconnectTimer) return;
  state.reconnectAttempt += 1;
  const delay = Math.min(15000, 1000 * Math.pow(1.8, state.reconnectAttempt));
  setConn('reconnecting', `重连中 (${Math.round(delay / 1000)}s)`);
  state.reconnectTimer = setTimeout(() => { state.reconnectTimer = null; connect(false); }, delay);
}

async function connect(manual = true) {
  try {
    state.wsManuallyClosed = false;
    if (manual) state.reconnectAttempt = 0;
    state.myUserId = $('userId').value.trim();
    if (!state.myUserId) return toast('请先填写 userId');
    saveConfig();
    await auth();
    setConn('reconnecting', '鉴权中...');
    connectWebSocket({
      onOpen: async () => {
        setConn('ok', '在线');
        state.reconnectAttempt = 0;
        await loadConversations();
        startPolling({
          onPollMessages: async () => { if (!state.currentConversationId || !state.token) return; try { await loadMessages(state.currentConversationId); } catch { } },
          onPollConversations: async () => { if (!state.token) return; try { await loadConversations(); } catch { } }
        });
      },
      onClose: () => { setConn('down', '断开'); stopPolling(); scheduleReconnect(); },
      onError: () => { setConn('down', '异常'); },
      onMessage: ev => { try { const p = JSON.parse(ev.data); if (p.type === 'message' && p.data) handleIncomingMessage(p.data); } catch { } }
    });
  } catch (e) { setConn('down', '鉴权失败'); toast(`鉴权说明：${e.message}`); scheduleReconnect(); }
}

function disconnect(manual = true) {
  state.wsManuallyClosed = manual;
  if (state.reconnectTimer) { clearTimeout(state.reconnectTimer); state.reconnectTimer = null; }
  disconnectWebSocket();
  state.token = null;
  stopPolling();
  setConn('down', manual ? '已退出' : '断开');
  if (manual) {
    $('loginScreen').style.display = 'flex';
    $('mainApp').style.display = 'none';
  }
}

function bindEvents() {
  $('btnConnect').addEventListener('click', () => connect(true));
  $('btnDisconnect').addEventListener('click', () => disconnect(true));
  $('btnNotify').addEventListener('click', async () => {
    if (!('Notification' in window)) return toast('当前浏览器不支持通知');
    await Notification.requestPermission();
    updateNotifyState();
  });

  $('btnAddContact').addEventListener('click', addContact);
  $('btnCreateGroup').addEventListener('click', () => createGroup().catch(e => toast(e.message)));
  $('sendBtn').addEventListener('click', () => sendMessage());
  $('retryBtn').addEventListener('click', retryLastFailed);
  $('jumpNew').addEventListener('click', () => scrollToBottom(true));

  $('convSearch').addEventListener('input', renderConversations);
  $('contactSearch').addEventListener('input', renderContacts);

  $('msgs').addEventListener('scroll', () => {
    renderMessages(state.messagesCache);
    if (isNearBottom()) $('jumpNew').style.display = 'none';
  });

  $('convList').addEventListener('click', e => {
    const item = e.target.closest('.item[data-conv-id]');
    if (item) selectConversation(item.dataset.convId).catch(err => toast(err.message));
  });

  $('contactList').addEventListener('click', e => {
    const open = e.target.getAttribute('data-open');
    if (open) {
      state.pendingDirect = open;
      createDirectFromInput().catch(err => toast(err.message));
      if (window.switchTab) window.switchTab('convs');
    }
  });

  $('text').addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') sendMessage(); });
  $('text').addEventListener('input', () => {
    if ($('text').value.length > MAX_DRAFT_LENGTH) {
      $('text').value = $('text').value.slice(0, MAX_DRAFT_LENGTH);
      toast(`截断：太长`);
    }
    $('draftCount').textContent = `${$('text').value.length} 字`;
    saveDraft($('text').value);
    broadcastSync({ type: 'draft-sync', conversationId: state.currentConversationId, draft: $('text').value });
  });

  ['apiUrl', 'appId', 'appSecret', 'userId'].forEach(id => $(id).addEventListener('change', saveConfig));
}

export function initUI() {
  loadConfig();
  renderGroupAgentPicker();
  renderContacts();
  updateNotifyState();
  setConn('down', '未激活');
  setSendState('空闲');

  wireMention({
    getCandidates: mentionCandidates,
    onInsert: () => {
      if ($('text').value.length > MAX_DRAFT_LENGTH) $('text').value = $('text').value.slice(0, MAX_DRAFT_LENGTH);
      $('draftCount').textContent = `${$('text').value.length} 字`;
      saveDraft($('text').value);
    }
  });

  function applySyncEvent(d = {}) {
    if (!d || d.fromTab === tabId) return;
    if (d.type === 'incoming-message' && d.message) handleIncomingMessage(d.message, true);
    if (d.type === 'draft-sync' && d.conversationId === state.currentConversationId) {
      $('text').value = String(d.draft || '').slice(0, MAX_DRAFT_LENGTH);
      $('draftCount').textContent = `${$('text').value.length} 字`;
    }
    if (d.type === 'active-conversation' && !state.currentConversationId && d.conversationId) {
      selectConversation(d.conversationId).catch(() => { });
    }
    if (d.type === 'unread-sync' && d.unread && typeof d.unread === 'object') {
      state.unreadMap = new Map(Object.entries(d.unread));
      renderConversations();
    }
  }

  if (channelSync) {
    channelSync.onmessage = e => applySyncEvent(e.data || {});
  }
  window.addEventListener('storage', e => {
    if (e.key !== syncKey || !e.newValue) return;
    try { applySyncEvent(JSON.parse(e.newValue)); } catch { }
  });

  bindEvents();
}

