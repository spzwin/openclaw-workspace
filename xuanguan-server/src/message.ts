/**
 * 玄关消息系统 - 消息与会话路由
 */

import { Router } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { authMiddleware } from './auth.js';
import { pushMessage, pushMessageToMultiple } from './websocket.js';
import {
  bootstrapDefaults,
  createConversation,
  ensureDirectConversation,
  getConversation,
  getMessage,
  listConversationsByUser,
  listMessages,
  resolveRecipients,
  saveMessage,
} from './store.js';
import type { SendMessageRequest } from './types.js';

bootstrapDefaults();

const OPENCLAW_ACCOUNT_ID = process.env.OPENCLAW_ACCOUNT_ID || 'default';

function normalizeContent(content: any, msgType: string) {
  if (content?.type) return content;
  return { type: msgType, ...content };
}

function buildMessage(request: SendMessageRequest, senderId = 'bot', senderName = 'AI 助手') {
  const timestamp = Date.now();
  const messageId = `msg_${timestamp}_${uuidv4().slice(0, 8)}`;
  return {
    messageId,
    conversationId: request.conversationId,
    conversationType: request.conversationType as 'single' | 'group',
    senderId,
    senderName,
    content: normalizeContent(request.content, request.msgType),
    timestamp,
    groupId: request.conversationType === 'group' ? request.conversationId : null,
    groupName: null,
    platform: 'xuanguan' as const,
    platformMessageId: messageId,
  };
}

export function createMessageRouter(jwtSecret: string): Router {
  const router = Router();
  const auth = authMiddleware(jwtSecret);

  router.get('/conversations', auth, (req: any, res: any) => {
    const userId = req.query.userId as string | undefined;
    const data = listConversationsByUser(userId);
    res.json({ code: 0, message: 'success', data });
  });

  router.post('/conversations', auth, (req: any, res: any) => {
    const { type = 'group', title, members = [], createdBy = 'web_user' } = req.body || {};
    if (!Array.isArray(members) || members.length === 0) {
      return res.status(400).json({ code: 400002, message: 'members must be non-empty array', data: null });
    }
    const conversation = createConversation({ type, title, members, createdBy });
    res.json({ code: 0, message: 'success', data: conversation });
  });

  router.get('/conversations/:conversationId/messages', auth, (req: any, res: any) => {
    const { conversationId } = req.params;
    const limit = Number(req.query.limit || 50);
    const data = listMessages(conversationId, limit);
    res.json({ code: 0, message: 'success', data });
  });

  router.post('/inbound/send', auth, (req: any, res: any) => {
    const request = req.body as SendMessageRequest & { senderId?: string; senderName?: string; toUserId?: string };

    if (request.toUserId && !request.conversationId) {
      const direct = ensureDirectConversation(request.senderId || 'web_user', request.toUserId);
      request.conversationId = direct.conversationId;
      request.conversationType = 'single';
    }

    if (!request.conversationId || !request.conversationType || !request.msgType || !request.content) {
      return res.status(400).json({ code: 400002, message: 'Missing required field', data: null });
    }

    const conv = getConversation(request.conversationId);
    if (!conv) {
      return res.status(404).json({ code: 404001, message: 'Conversation not found', data: null });
    }

    const message = buildMessage(request, request.senderId || 'web_user', request.senderName || 'Web User');
    saveMessage(message);

    const recipients = resolveRecipients(request.conversationId);
    const deliveredToUsers = pushMessageToMultiple(recipients, message);
    const deliveredToAgent = pushMessage(OPENCLAW_ACCOUNT_ID, message);

    res.json({
      code: 0,
      message: 'success',
      data: { messageId: message.messageId, deliveredToUsers, deliveredToAgent, conversationId: request.conversationId },
    });
  });

  router.post('/send', auth, (req: any, res: any) => {
    const request: SendMessageRequest = req.body;

    if (!request.conversationId || !request.conversationType || !request.msgType || !request.content) {
      return res.status(400).json({ code: 400002, message: 'Missing required field', data: null });
    }

    const conv = getConversation(request.conversationId);
    if (!conv) {
      return res.status(404).json({ code: 404001, message: 'Conversation not found', data: null });
    }

    const message = buildMessage(request, 'bot', 'AI 助手');
    saveMessage(message);

    const recipients = resolveRecipients(request.conversationId);
    const deliveredToUsers = pushMessageToMultiple(recipients, message);

    res.json({
      code: 0,
      message: 'success',
      data: { messageId: message.messageId, status: 'sent', sentAt: message.timestamp, deliveredToUsers },
    });
  });

  router.post('/batch', auth, (req: any, res: any) => {
    const { messages = [] } = req.body || {};
    if (!Array.isArray(messages)) {
      return res.status(400).json({ code: 400002, message: 'messages must be an array', data: null });
    }

    const results = messages.map((m: SendMessageRequest) => {
      if (!m.conversationId || !m.conversationType || !m.msgType || !m.content) {
        return { messageId: null, status: 'failed', error: 'missing required field' };
      }
      const conv = getConversation(m.conversationId);
      if (!conv) return { messageId: null, status: 'failed', error: 'conversation not found' };

      const message = buildMessage(m, 'bot', 'AI 助手');
      saveMessage(message);
      const recipients = resolveRecipients(m.conversationId);
      pushMessageToMultiple(recipients, message);
      return { messageId: message.messageId, status: 'sent', conversationId: m.conversationId };
    });

    res.json({ code: 0, message: 'success', data: { total: messages.length, results } });
  });

  router.post('/recall', auth, (req: any, res: any) => {
    const { messageId } = req.body || {};
    if (!messageId) return res.status(400).json({ code: 400002, message: 'Missing messageId', data: null });
    const msg = getMessage(messageId);
    if (!msg) return res.status(404).json({ code: 404004, message: 'Message not found', data: null });

    const recallNotice = {
      ...msg,
      content: { type: 'text', text: '[消息已撤回]' },
      timestamp: Date.now(),
    };

    const recipients = resolveRecipients(msg.conversationId);
    pushMessageToMultiple(recipients, recallNotice as any);
    res.json({ code: 0, message: 'success', data: { messageId, status: 'recalled' } });
  });

  router.get('/:messageId', auth, (req: any, res: any) => {
    const message = getMessage(req.params.messageId);
    if (!message) return res.status(404).json({ code: 404004, message: 'Message not found', data: null });
    res.json({ code: 0, message: 'success', data: message });
  });

  return router;
}
