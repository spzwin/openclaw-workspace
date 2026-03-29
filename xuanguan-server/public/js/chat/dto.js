// Chat DTO schema + runtime validators + normalizers

export const Dto = {
  ApiResp: { code: 'number', message: 'string', data: 'any' },
  Mention: { userId: 'string', display: 'string' },
  MentionToken: { type: 'mention', userId: 'string', display: 'string', start: 'number', end: 'number', raw: 'string' },
  MessageContent: { type: 'text|markdown', text: 'string', mentions: 'Mention[]', mentionTokens: 'MentionToken[]' },
  Message: {
    id: 'string',
    conversationId: 'string',
    senderId: 'string',
    senderName: 'string',
    timestamp: 'number',
    content: 'MessageContent'
  },
  Conversation: { conversationId: 'string', type: 'single|group', title: 'string', members: 'string[]', updatedAt: 'number' }
};

const text = v => (typeof v === 'string' ? v : String(v ?? ''));
const num = v => (Number.isFinite(Number(v)) ? Number(v) : Date.now());
const isObj = v => !!v && typeof v === 'object' && !Array.isArray(v);

function ok(data) { return { ok: true, data, issues: [] }; }
function fail(data, issues) { return { ok: false, data, issues }; }

export function normalizeMention(v = {}) {
  return { userId: text(v.userId), display: text(v.display || v.userId) };
}

export function normalizeMentionToken(v = {}) {
  return {
    type: 'mention',
    userId: text(v.userId),
    display: text(v.display || v.userId),
    start: Number.isFinite(Number(v.start)) ? Number(v.start) : 0,
    end: Number.isFinite(Number(v.end)) ? Number(v.end) : 0,
    raw: text(v.raw || `@${v.userId || ''}`)
  };
}

export function validateMessageContent(input) {
  const issues = [];
  const src = isObj(input) ? input : {};
  const out = {
    type: src.type === 'markdown' ? 'markdown' : 'text',
    text: text(src.text),
    mentions: Array.isArray(src.mentions) ? src.mentions.map(normalizeMention).filter(x => x.userId) : [],
    mentionTokens: Array.isArray(src.mentionTokens) ? src.mentionTokens.map(normalizeMentionToken).filter(x => x.userId) : []
  };

  if (!isObj(input)) issues.push('content:not-object');
  if (src.type && !['text', 'markdown'].includes(src.type)) issues.push('content:type-invalid');

  return issues.length ? fail(out, issues) : ok(out);
}

export function buildMessageContent({ type = 'text', text: body = '', mentions = [], mentionTokens = [] } = {}) {
  return validateMessageContent({ type, text: body, mentions, mentionTokens }).data;
}

export function validateMessage(input) {
  const issues = [];
  const src = isObj(input) ? input : {};
  const contentRes = validateMessageContent(src.content || {});
  const out = {
    id: text(src.id || src.messageId || ''),
    conversationId: text(src.conversationId),
    senderId: text(src.senderId),
    senderName: text(src.senderName || src.senderId),
    timestamp: num(src.timestamp),
    content: contentRes.data
  };

  if (!isObj(input)) issues.push('message:not-object');
  if (!out.conversationId) issues.push('message:conversationId-empty');
  if (!out.senderId) issues.push('message:senderId-empty');
  if (!contentRes.ok) issues.push(...contentRes.issues.map(x => `message.${x}`));

  return issues.length ? fail(out, issues) : ok(out);
}

export function normalizeMessage(v = {}) {
  return validateMessage(v).data;
}

export function validateConversation(input) {
  const issues = [];
  const src = isObj(input) ? input : {};
  const out = {
    conversationId: text(src.conversationId),
    type: src.type === 'single' ? 'single' : 'group',
    title: text(src.title || src.conversationId),
    members: Array.isArray(src.members) ? src.members.map(text).filter(Boolean) : [],
    updatedAt: num(src.updatedAt)
  };

  if (!isObj(input)) issues.push('conversation:not-object');
  if (!out.conversationId) issues.push('conversation:conversationId-empty');

  return issues.length ? fail(out, issues) : ok(out);
}

export function normalizeConversation(v = {}) {
  return validateConversation(v).data;
}
