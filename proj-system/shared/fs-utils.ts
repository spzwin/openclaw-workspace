// 文件系统工具 - 支持原子操作和文件锁

import * as fs from 'fs/promises';
import * as path from 'path';

const locks = new Map<string, Promise<any>>();

/**
 * 读取 JSON 文件
 */
export async function readJson<T>(filepath: string, defaultValue?: T): Promise<T> {
  try {
    const content = await fs.readFile(filepath, 'utf-8');
    return JSON.parse(content);
  } catch (error: any) {
    if (error.code === 'ENOENT' && defaultValue !== undefined) {
      return defaultValue;
    }
    throw error;
  }
}

/**
 * 写入 JSON 文件 (原子操作：先写临时文件，再重命名)
 */
export async function writeJson<T>(filepath: string, data: T): Promise<void> {
  const dir = path.dirname(filepath);
  await fs.mkdir(dir, { recursive: true });
  
  const tempPath = filepath + '.tmp';
  await fs.writeFile(tempPath, JSON.stringify(data, null, 2), 'utf-8');
  await fs.rename(tempPath, filepath);
}

/**
 * 带文件锁的原子写入
 */
export async function withFileLock<T>(
  lockPath: string,
  operation: () => Promise<T>
): Promise<T> {
  // 等待之前的锁释放
  while (locks.has(lockPath)) {
    await locks.get(lockPath);
  }
  
  // 获取锁
  let releaseLock: () => void;
  const lockPromise = new Promise<void>(resolve => {
    releaseLock = resolve;
  });
  locks.set(lockPath, lockPromise);
  
  try {
    return await operation();
  } finally {
    // 释放锁
    releaseLock!();
    locks.delete(lockPath);
  }
}

/**
 * 乐观锁写入 (带版本检查)
 */
export async function atomicWriteWithVersionCheck(
  filepath: string,
  data: any & { version: number },
  expectedVersion: number
): Promise<boolean> {
  const tempPath = filepath + '.tmp';
  
  // 写入临时文件
  await fs.writeFile(tempPath, JSON.stringify(data, null, 2), 'utf-8');
  
  try {
    // 读取当前文件，检查版本
    const current = await readJson(filepath);
    if (current.version !== expectedVersion) {
      // 版本冲突，放弃写入
      await fs.unlink(tempPath);
      return false;
    }
    
    // 原子重命名
    await fs.rename(tempPath, filepath);
    return true;
  } catch (error: any) {
    if (error.code === 'ENOENT') {
      // 文件不存在，直接写入
      await fs.rename(tempPath, filepath);
      return true;
    }
    throw error;
  }
}

/**
 * 检查文件是否存在
 */
export async function fileExists(filepath: string): Promise<boolean> {
  try {
    await fs.access(filepath);
    return true;
  } catch {
    return false;
  }
}

/**
 * 确保目录存在
 */
export async function ensureDir(dirpath: string): Promise<void> {
  await fs.mkdir(dirpath, { recursive: true });
}
