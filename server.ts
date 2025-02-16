import express from 'express';
import path from 'path';

const app = express();

// Serve static files from the temp/output directory
app.use('/api/files', express.static(path.join(process.cwd(), 'temp', 'output'))); 