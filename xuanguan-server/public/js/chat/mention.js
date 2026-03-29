import { $, state, esc } from './state.js';

export function getMentionQuery(text, cursor) {
  const before = text.slice(0, cursor);
  const m = before.match(/(^|\s)@([^\s@]{0,32})$/);
  if (!m) return null;
  return { query: (m[2] || '').toLowerCase(), start: before.length - m[2].length - 1, end: cursor };
}

export function wireMention({ getCandidates, onInsert }) {
  const ta = $('text');
  const menu = $('mentionMenu');

  function hide() {
    menu.style.display = 'none';
    state.mentionState = { list: [], active: 0, range: null };
  }

  function render(items, range) {
    if (!items.length) return hide();
    state.mentionState = { list: items, active: 0, range };
    menu.innerHTML = items
      .map(
        (it, idx) => `<div class="mention-item ${idx === 0 ? 'active' : ''}" data-idx="${idx}"><div>${esc(it.name || it.userId)}</div><div class="meta">@${esc(it.userId)}${it.kind === 'agent' ? ' · Agent' : ''}</div></div>`
      )
      .join('');
    menu.style.display = 'block';
    [...menu.querySelectorAll('.mention-item')].forEach(el => {
      el.onclick = () => apply(Number(el.dataset.idx || 0));
    });
  }

  function refresh() {
    const range = getMentionQuery(ta.value, ta.selectionStart || 0);
    if (!range) return hide();
    const candidates = getCandidates(range.query).slice(0, 8);
    render(candidates, range);
  }

  function apply(idx) {
    const it = state.mentionState.list[idx];
    const range = state.mentionState.range;
    if (!it || !range) return hide();
    const insert = `@${it.userId} `;
    const t = ta.value;
    ta.value = t.slice(0, range.start) + insert + t.slice(range.end);
    const pos = range.start + insert.length;
    ta.setSelectionRange(pos, pos);
    onInsert(it);
    hide();
    ta.focus();
  }

  function move(step) {
    if (menu.style.display === 'none') return;
    const len = state.mentionState.list.length;
    state.mentionState.active = (state.mentionState.active + step + len) % len;
    [...menu.querySelectorAll('.mention-item')].forEach((el, idx) => el.classList.toggle('active', idx === state.mentionState.active));
  }

  ta.addEventListener('keydown', e => {
    const visible = menu.style.display !== 'none';
    if (visible && e.key === 'ArrowDown') { e.preventDefault(); move(1); return; }
    if (visible && e.key === 'ArrowUp') { e.preventDefault(); move(-1); return; }
    if (visible && e.key === 'Enter' && !(e.ctrlKey || e.metaKey)) { e.preventDefault(); apply(state.mentionState.active); return; }
    if (visible && e.key === 'Escape') { e.preventDefault(); hide(); return; }
  });

  ta.addEventListener('input', refresh);
  ta.addEventListener('click', refresh);
  ta.addEventListener('keyup', e => {
    if (['ArrowLeft', 'ArrowRight', 'Home', 'End', 'Backspace', 'Delete'].includes(e.key)) refresh();
  });
  document.addEventListener('selectionchange', () => {
    if (document.activeElement === ta) refresh();
  });
  ta.addEventListener('blur', () => setTimeout(hide, 120));

  return { refresh, hide };
}

export function extractMentions(text, indexMap) {
  const regex = /@([a-zA-Z0-9_\-.]+)/g;
  const dedup = new Map();
  const tokens = [];
  let m;
  while ((m = regex.exec(text)) !== null) {
    const userId = m[1];
    const start = m.index;
    const end = start + m[0].length;
    const display = indexMap.get(userId)?.name || userId;
    if (!dedup.has(userId)) dedup.set(userId, { userId, display });
    tokens.push({ type: 'mention', userId, display, start, end, raw: m[0] });
  }
  return { mentions: [...dedup.values()], mentionTokens: tokens };
}

function renderByMentionTokens(text = '', mentionTokens = []) {
  if (!mentionTokens.length) return esc(text).replace(/\n/g, '<br/>');
  const sorted = [...mentionTokens].sort((a, b) => a.start - b.start);
  let cursor = 0;
  let html = '';
  for (const tk of sorted) {
    if (typeof tk.start !== 'number' || typeof tk.end !== 'number' || tk.start < cursor) continue;
    html += esc(text.slice(cursor, tk.start));
    html += `<span class="pill" data-mention="${esc(tk.userId)}" title="${esc(tk.display || tk.userId)}">@${esc(tk.display || tk.userId)}</span>`;
    cursor = tk.end;
  }
  html += esc(text.slice(cursor));
  return html.replace(/\n/g, '<br/>');
}

export function renderWithMentions(text = '', mentions = [], mentionTokens = []) {
  if (mentionTokens?.length) return renderByMentionTokens(text, mentionTokens);
  if (!mentions?.length) return esc(text).replace(/\n/g, '<br/>');

  // 向后兼容：历史消息只有 mentions 时，按扫描生成 token 后渲染
  const mentionMap = new Map(mentions.map(m => [m.userId, m]));
  const scanRegex = /@([a-zA-Z0-9_\-.]+)/g;
  const fallbackTokens = [];
  let m;
  while ((m = scanRegex.exec(text)) !== null) {
    const userId = m[1];
    if (!mentionMap.has(userId)) continue;
    const start = m.index;
    fallbackTokens.push({
      type: 'mention',
      userId,
      display: mentionMap.get(userId)?.display || userId,
      start,
      end: start + m[0].length,
      raw: m[0]
    });
  }
  return renderByMentionTokens(text, fallbackTokens);
}
