#!/usr/bin/env node
/**
 * UI 自动化回归（真实点击流）
 * 覆盖：创建群 -> @提及选择 -> 发送 -> 刷新回显 -> 会话切换草稿恢复
 */
import fs from 'node:fs';
import { chromium } from 'playwright-core';

const BASE_URL = process.env.CHAT_UI_E2E_URL || 'http://localhost:3001/chat.html';
const APP_ID = process.env.CHAT_UI_E2E_APP_ID || 'cli_xxxxxxxxxxxxxxxx';
const APP_SECRET = process.env.CHAT_UI_E2E_APP_SECRET || 'your_app_secret_here_change_in_production';
const USER_ID = process.env.CHAT_UI_E2E_USER_ID || 'ui_e2e_user';

const CANDIDATE_BROWSERS = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium'
].filter(Boolean);

function resolveBrowserPath() {
  const p = CANDIDATE_BROWSERS.find(x => fs.existsSync(x));
  if (!p) throw new Error('未找到可用 Chromium/Chrome，可通过 CHROME_PATH 指定浏览器路径');
  return p;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function assert(cond, msg) { if (!cond) throw new Error(msg); }

async function waitToast(page) {
  const t = page.locator('#toast');
  try {
    await t.waitFor({ state: 'visible', timeout: 2500 });
    return await t.textContent();
  } catch {
    return '';
  }
}

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: resolveBrowserPath() });
  const page = await browser.newPage();
  try {
    console.log('[ui-e2e] 1) open chat page');
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });

    console.log('[ui-e2e] 2) fill config & connect');
    await page.fill('#appId', APP_ID);
    await page.fill('#appSecret', APP_SECRET);
    await page.fill('#userId', USER_ID);
    await page.click('#btnConnect');
    await page.waitForSelector('#statusText');
    await page.waitForFunction(() => document.querySelector('#statusText')?.textContent?.includes('已连接'), null, { timeout: 15000 });

    console.log('[ui-e2e] 3) create group');
    await page.fill('#groupTitle', `ui_e2e_group_${Date.now()}`);
    const firstAgent = page.locator('.group-agent-cb').first();
    await firstAgent.check();
    await page.fill('#groupCustomMembers', 'ui_e2e_peer');
    await page.click('#btnCreateGroup');
    await sleep(1200);

    console.log('[ui-e2e] 4) @mention select + send');
    await page.fill('#text', '@');
    await page.waitForSelector('#mentionMenu .mention-item', { timeout: 5000 });
    await page.keyboard.press('ArrowDown');
    await page.keyboard.press('Enter');
    await page.type('#text', ' ui_e2e ping');
    await page.click('#sendBtn');

    await page.waitForFunction(() => {
      const msgs = [...document.querySelectorAll('#msgs .bubble')].map(el => el.textContent || '');
      return msgs.some(x => x.includes('ui_e2e ping'));
    }, null, { timeout: 10000 });

    console.log('[ui-e2e] 5) refresh echo check');
    await page.click('#btnRefreshConvs');
    await sleep(1200);
    const mentionPillCount = await page.locator('#msgs .bubble .pill[data-mention]').count();
    assert(mentionPillCount > 0, 'mention pill not rendered');

    console.log('[ui-e2e] 6) draft restore across conversation switching');
    await page.fill('#directTarget', 'ui_e2e_dm_target');
    await page.click('#btnCreateDirect');
    await sleep(1200);

    const convItems = page.locator('#convList .item');
    const convCount = await convItems.count();
    assert(convCount >= 2, `not enough conversations for switch test: ${convCount}`);

    await convItems.first().click();
    await page.fill('#text', 'draft_restore_probe');
    await convItems.nth(1).click();
    await sleep(300);
    await convItems.first().click();
    await sleep(300);
    const draft = await page.inputValue('#text');
    assert(draft.includes('draft_restore_probe'), 'draft not restored after conversation switch');

    const toastText = await waitToast(page);
    if (toastText) console.log('[ui-e2e] toast:', toastText);

    console.log('[ui-e2e] ✅ PASS');
  } catch (e) {
    console.error('[ui-e2e] ❌ FAIL:', e.message);
    process.exitCode = 1;
  } finally {
    await browser.close();
  }
})();
