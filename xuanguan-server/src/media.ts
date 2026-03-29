/**
 * 玄关消息系统 - 媒体路由
 */

import express, { Router } from 'express';
import multer from 'multer';
import { v4 as uuidv4 } from 'uuid';
import { join } from 'path';
import { mkdirSync, existsSync, readFileSync, writeFileSync } from 'fs';
import { authMiddleware } from './auth.js';
import type { MediaUploadResponse } from './types.js';

// 配置文件存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = process.env.MEDIA_STORAGE_PATH || '/tmp/xuanguan/media';

    // 确保目录存在
    if (!existsSync(uploadDir)) {
      mkdirSync(uploadDir, { recursive: true });
    }

    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}_${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB
  }
});

export function createMediaRouter(jwtSecret: string): Router {
  const router = Router();
  const auth = authMiddleware(jwtSecret);

  /**
   * POST /upload
   * 上传媒体文件
   */
  router.post('/upload', auth, upload.single('file'), async (req: any, res: any) => {
    const requestId = `req_${uuidv4()}`;
    const timestamp = Date.now();

    try {
      if (!req.file) {
        return res.status(400).json({
          code: 400002,
          message: 'No file uploaded',
          data: null,
          meta: { requestId, timestamp }
        });
      }

      const mediaId = `media_${uuidv4()}`;
      const mediaBaseUrl = process.env.MEDIA_BASE_URL || 'http://localhost:3000';
      const mediaUrl = `${mediaBaseUrl}/media/${req.file.filename}`;

      const response: MediaUploadResponse = {
        code: 0,
        message: 'success',
        data: {
          mediaId,
          mediaUrl,
          fileSize: req.file.size,
          mimeType: req.file.mimetype
        }
      };

      // 添加额外信息（如果有）
      if (req.body.type === 'image') {
        // TODO: 读取图片尺寸
        // response.data.width = ...
        // response.data.height = ...
      }

      if (req.body.type === 'video' || req.body.type === 'voice') {
        // TODO: 读取时长
        // response.data.duration = ...
      }

      console.log(`[Media] Uploaded ${mediaId}: ${req.file.originalname}`);

      res.json(response);

    } catch (error: any) {
      console.error('[Media] Upload error:', error);

      res.status(500).json({
        code: 500001,
        message: 'Internal server error',
        data: null,
        meta: { requestId, timestamp }
      });
    }
  });

  /**
   * GET /:mediaId
   * 下载媒体文件
   */
  router.get('/:mediaId', auth, async (req: any, res: any) => {
    const requestId = `req_${uuidv4()}`;
    const timestamp = Date.now();
    const { mediaId } = req.params;

    try {
      // 实际应该从数据库查询媒体文件路径
      // 这里简化处理，直接返回错误
      res.status(404).json({
        code: 404003,
        message: 'Media not found',
        data: null,
        meta: { requestId, timestamp }
      });

    } catch (error: any) {
      console.error('[Media] Download error:', error);

      res.status(500).json({
        code: 500001,
        message: 'Internal server error',
        data: null,
        meta: { requestId, timestamp }
      });
    }
  });

  return router;
}

/**
 * 创建静态文件服务中间件
 */
export function createMediaStaticMiddleware() {
  const mediaDir = process.env.MEDIA_STORAGE_PATH || '/tmp/xuanguan/media';

  // 确保目录存在
  if (!existsSync(mediaDir)) {
    mkdirSync(mediaDir, { recursive: true });
  }

  return express.static(mediaDir);
}
