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
    console.log('Request path:', req.query.path);
    console.log('Looking for file:', fullPath);
    console.log('Directory contents:', fs.readdirSync(path.join(process.cwd(), 'temp', 'output')));

    if (!fs.existsSync(fullPath)) {
      const availableFiles = fs.readdirSync(path.join(process.cwd(), 'temp', 'output'));
      console.log('Available files:', availableFiles);
      return res.status(404).json({
        error: 'File not found',
        path: fullPath,
        availableFiles
      });
    }

    // Set proper MIME type for GLB files
    res.setHeader('Content-Type', 'model/gltf-binary');
    res.setHeader('Content-Disposition', `inline; filename="${path.basename(filePath)}"`);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Cache-Control', 'public, max-age=31536000');

    const fileContent = fs.readFileSync(fullPath);
    return res.send(fileContent);

  } catch (error) {
    console.error('File serving error:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
} 