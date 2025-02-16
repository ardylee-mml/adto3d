import { NextApiRequest, NextApiResponse } from 'next';
import path from 'path';
import fs from 'fs';

export const config = {
  api: {
    responseLimit: false,
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const filePath = Array.isArray(req.query.path)
      ? req.query.path.join('/')
      : req.query.path;

    if (!filePath) {
      return res.status(400).json({ error: 'No file path provided' });
    }

    const fullPath = path.join(process.cwd(), 'temp', 'output', filePath);

    if (!fs.existsSync(fullPath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    res.setHeader('Content-Type', 'model/gltf-binary');
    res.setHeader('Cache-Control', 'public, max-age=31536000');

    const fileContent = fs.readFileSync(fullPath);
    res.send(fileContent);

  } catch (error) {
    console.error('File serving error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
} 