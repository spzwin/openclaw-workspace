import { $, builtinAgents } from './state.js';

export function renderGroupAgentPicker() {
  const box = $('groupAgentPicker');
  if (!box) return;
  box.innerHTML = builtinAgents
    .map(
      a => `<label class="agent-pill"><input type="checkbox" value="${a.userId}" class="group-agent-cb" /><span>${a.name}</span></label>`
    )
    .join('');
}

export function selectedGroupAgents() {
  return [...document.querySelectorAll('.group-agent-cb:checked')].map(el => el.value);
}

export function buildGroupMembers(me) {
  const custom = ($('groupCustomMembers').value || '')
    .split(',')
    .map(v => v.trim())
    .filter(Boolean);
  const members = [...new Set([me, ...selectedGroupAgents(), ...custom])];
  return { members, custom };
}
