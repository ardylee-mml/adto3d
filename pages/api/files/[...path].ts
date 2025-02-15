import { NextApiRequest, NextApiResponse } from 'next';
import path from 'path';
import fs from 'fs';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const { path: filePath } = req.query;
  const fullPath = path.join(process.cwd(), 'temp', 'output', filePath as string);

  if (fs.existsSync(fullPath)) {
    const fileStream = fs.createReadStream(fullPath);
    res.setHeader('Content-Type', 'model/gltf-binary');
    fileStream.pipe(res);
  } else {
    res.status(404).json({ error: 'File not found' });
  }
} 