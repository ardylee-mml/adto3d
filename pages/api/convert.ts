import type { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import process from 'process';

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

    // Step 1: Analyze image
    const analysisProcess = spawn('python3', [
      path.join(process.cwd(), 'scripts', 'analyze_image.py'),
      imageFile.filepath
    ]);

    const analysisResult = await new Promise((resolve, reject) => {
      let output = '';
      analysisProcess.stdout.on('data', (data) => output += data);
      analysisProcess.on('close', (code) => {
        if (code === 0) resolve(output);
        else reject(new Error(`Analysis failed with code ${code}`));
      });
    });

    const analysis = JSON.parse(analysisResult);

    // Step 2: Create 3D model using Blender
    const outputDir = path.join(VM_BASE_PATH, 'output');
    const outputPath = path.join(outputDir, `${path.basename(imageFile.filepath)}.glb`);
    const analysisPath = path.join(outputDir, `${path.basename(imageFile.filepath)}.json`);
    
    // Save analysis for Blender script
    fs.writeFileSync(analysisPath, JSON.stringify(analysis));

    const blenderProcess = spawn('blender', [
      '--background',
      '--python',
      path.join(process.cwd(), 'scripts', 'convert_to_3d.py'),
      '--',
      analysisPath,
      outputPath
    ]);

    let blenderOutput = '';
    let blenderError = '';

    blenderProcess.stdout.on('data', (data) => {
      blenderOutput += data.toString();
      console.log('Blender output:', data.toString());
    });

    blenderProcess.stderr.on('data', (data) => {
      blenderError += data.toString();
      console.error('Blender error:', data.toString());
    });

    const blenderResult = await new Promise((resolve, reject) => {
      blenderProcess.on('close', (code) => {
        console.log(`Blender process exited with code ${code}`);
        if (code === 0) {
          resolve(blenderOutput);
        } else {
          reject(new Error(`Blender failed with code ${code}: ${blenderError}`));
        }
      });
    });

    console.log('Blender completed successfully');

    res.status(200).json({
      success: true,
      analysis: analysis,
      modelUrl: `/output/${path.basename(outputPath)}`,
    });

  } catch (error) {
    console.error('Conversion error:', error);
    res.status(500).json({ error: 'Error processing the image' });
  }
} 