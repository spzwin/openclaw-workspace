export const CHAT_CONFIG = {
  defaults: {
    apiUrl: 'http://192.168.91.107:3001',
    appId: 'cli_xxxxxxxxxxxxxxxx',
    appSecret: 'your_app_secret_here_change_in_production',
    userId: 'user_123456'
  },
  agents: {
    coder: { userId: 'coder', display: '码爪 Coder' },
    researcher: { userId: 'researcher', display: '研爪 Researcher' },
    atlas: { userId: 'atlas', display: 'Atlas' }
  }
};

export function resolveBuiltinAgents() {
  const injected = window.__XUANGUAN_CHAT_CONFIG__?.agents;
  const merged = { ...CHAT_CONFIG.agents, ...(injected || {}) };
  return [
    { userId: merged.coder?.userId || 'coder', name: merged.coder?.display || '码爪 Coder', kind: 'agent' },
    { userId: merged.researcher?.userId || 'researcher', name: merged.researcher?.display || '研爪 Researcher', kind: 'agent' },
    { userId: merged.atlas?.userId || 'atlas', name: merged.atlas?.display || 'Atlas', kind: 'agent' }
  ];
}
