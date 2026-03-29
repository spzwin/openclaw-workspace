# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## NoteX / CWork

- **CWork Key:** `QBDrI4sogQG3SmNIracphY8iMFpqClt4`
- **Base URL:** https://notex.aishuo.co/noteX
- **Auth URL:** https://cwork-web.mediportal.com.cn

## Subagents

### Math Subagent（数学运算）
- **路径：** `workspace/subagents/math/`
- **触发：** 自然语言请求数学计算时自动 spawn
- **模式：** `runtime: "subagent"`, `mode: "run"`（一次性任务）
- **职责：** 算术、代数、微积分、线性代数、概率统计等所有数学运算
