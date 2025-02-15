import type { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';

const VM_BASE_PATH = '/home/mml_admin/2dto3d';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('Starting image analysis process');
  
  try {
    const form = new formidable.IncomingForm();
    const [_fields, files] = await new Promise<[formidable.Fields, formidable.Files]>((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });

    const imageFile = Array.isArray(files.image) ? files.image[0] : files.image;
    if (!imageFile) {
      console.error('No image file provided');
      return res.status(400).json({ error: 'No image file provided' });
    }

    console.log('Image received:', imageFile.filepath);

    // Run OpenCV analysis
    const scriptPath = path.join(VM_BASE_PATH, 'scripts', 'analyze_image.py');
    console.log('Running analysis script:', scriptPath);

    const analysisProcess = spawn('python3', [scriptPath, imageFile.filepath]);
    
    let outputData = '';
    let errorData = '';

    analysisProcess.stdout.on('data', (data) => {
      outputData += data.toString();
      console.log('Analysis output:', data.toString());
    });

    analysisProcess.stderr.on('data', (data) => {
      errorData += data.toString();
      console.error('Analysis error:', data.toString());
    });

    const analysisResult = await new Promise((resolve, reject) => {
      analysisProcess.on('close', (code) => {
        console.log(`Analysis process exited with code ${code}`);
        if (code === 0) {
          resolve(outputData);
        } else {
          reject(new Error(`Analysis failed with code ${code}: ${errorData}`));
        }
      });
    });

    // Parse and return the analysis results
    const analysis = JSON.parse(analysisResult);
    console.log('Analysis completed successfully');

    res.status(200).json({
      success: true,
      analysis: analysis,
      prompt: analysis.generated_prompt
    });

  } catch (error) {
    console.error('Conversion error:', error);
    res.status(500).json({ 
      error: 'Analysis failed', 
      details: error instanceof Error ? error.message : 'Unknown error' 
    });
  }
} 