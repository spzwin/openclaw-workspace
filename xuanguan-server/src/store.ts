import { v4 as uuidv4 } from 'uuid';

export type ConversationType = 'single' | 'group';

export interface UserProfile {
  userId: string;
  name?: string;
  createdAt: number;
}

export interface Conversation {
  conversationId: string;
  type: ConversationType;
  title?: string;
  members: string[];
  createdBy: string;
  createdAt: number;
  updatedAt: number;
}

export interface StoredMessage {
  messageId: string;
  conversationId: string;
  conversationType: ConversationType;
  senderId: string;
  senderName?: string;
  content: Record<string, any>;
  timestamp: number;
  platform: 'xuanguan';
  platformMessageId: string;
}

const users = new Map<string, UserProfile>();
const conversations = new Map<string, Conversation>();
const messagesByConversation = new Map<string, StoredMessage[]>();
const messagesById = new Map<string, StoredMessage>();

function ensureUser(userId: string, name?: string): UserProfile {
  const existing = users.get(userId);
  if (existing) return existing;
  const profile: UserProfile = { userId, name, createdAt: Date.now() };
  users.set(userId, profile);
  return profile;
}

export function createConversation(input: {
  type: ConversationType;
  title?: string;
  members: string[];
  createdBy: string;
  conversationId?: string;
}): Conversation {
  const now = Date.now();
  const dedupMembers = Array.from(new Set(input.members.filter(Boolean)));
  if (!dedupMembers.includes(input.createdBy)) dedupMembers.push(input.createdBy);
  dedupMembers.forEach((id) => ensureUser(id));

  const conversationId = input.conversationId || `${input.type}_${uuidv4().slice(0, 10)}`;
  const record: Conversation = {
    conversationId,
    type: input.type,
    title: input.title,
    members: dedupMembers,
    createdBy: input.createdBy,
    createdAt: now,
    updatedAt: now,
  };
  conversations.set(conversationId, record);
  if (!messagesByConversation.has(conversationId)) messagesByConversation.set(conversationId, []);
  return record;
}

export function getConversation(conversationId: string): Conversation | null {
  return conversations.get(conversationId) ?? null;
}

export function listConversationsByUser(userId?: string): Conversation[] {
  const all = Array.from(conversations.values());
  if (!userId) return all.sort((a, b) => b.updatedAt - a.updatedAt);
  return all.filter((c) => c.members.includes(userId)).sort((a, b) => b.updatedAt - a.updatedAt);
}

export function ensureDirectConversation(userA: string, userB: string): Conversation {
  const members = [userA, userB].sort();
  const existing = Array.from(conversations.values()).find(
    (c) => c.type === 'single' && c.members.length === 2 && c.members.slice().sort().join('|') === members.join('|')
  );
  if (existing) return existing;
  return createConversation({ type: 'single', members: [userA, userB], createdBy: userA });
}

export function saveMessage(message: StoredMessage): void {
  messagesById.set(message.messageId, message);
  const list = messagesByConversation.get(message.conversationId) ?? [];
  list.push(message);
  messagesByConversation.set(message.conversationId, list);

  const conv = conversations.get(message.conversationId);
  if (conv) {
    conv.updatedAt = Date.now();
    conversations.set(conv.conversationId, conv);
  }
}

export function getMessage(messageId: string): StoredMessage | null {
  return messagesById.get(messageId) ?? null;
}

export function listMessages(conversationId: string, limit = 50): StoredMessage[] {
  const list = messagesByConversation.get(conversationId) ?? [];
  return list.slice(Math.max(0, list.length - limit));
}

export function resolveRecipients(conversationId: string): string[] {
  const conv = conversations.get(conversationId);
  if (!conv) return [];
  return conv.members;
}

export function bootstrapDefaults(): void {
  ensureUser('default', 'OpenClaw Agent');
}
