import { NextApiRequest, NextApiResponse } from 'next';
import path from 'path';
import fs from 'fs';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const filePath = Array.isArray(req.query.path) 
      ? req.query.path.join('/') 
      : req.query.path;

    if (!filePath) {
      return res.status(400).json({ error: 'No file path provided' });
    }

    const fullPath = path.join(process.cwd(), 'temp', 'output', filePath);
    console.log('Attempting to serve file:', fullPath);

    if (fs.existsSync(fullPath)) {
      const fileStream = fs.createReadStream(fullPath);
      res.setHeader('Content-Type', 'model/gltf-binary');
      fileStream.pipe(res);
    } else {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    console.error('File serving error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
} 