import type { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import fs from 'fs';
import path from 'path';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Disable the default body parser to handle form-data
export const config = {
  api: {
    bodyParser: false,
  },
};

// Create temp directories if they don't exist
const tempDir = path.join(process.cwd(), 'temp');
const uploadsDir = path.join(tempDir, 'uploads');
const outputDir = path.join(tempDir, 'output');

[tempDir, uploadsDir, outputDir].forEach((dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Parse the incoming form data
    const form = formidable({
      uploadDir: uploadsDir,
      keepExtensions: true,
    });

    const [_fields, files] = await new Promise<[formidable.Fields, formidable.Files]>((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });

    const imageFile = Array.isArray(files.image) ? files.image[0] : files.image;
    if (!imageFile) {
      return res.status(400).json({ error: 'No image file provided' });
    }

    // Step 1: Remove background using Python script
    const bgRemovedPath = path.join(outputDir, `bg_removed_${path.basename(imageFile.filepath)}`);
    
    console.log('Starting background removal...');
    await execAsync(`python3 -c "
from rembg import remove
from PIL import Image
input_image = Image.open('${imageFile.filepath}')
output_image = remove(input_image)
output_image.save('${bgRemovedPath}')
"`);
    console.log('Background removal completed');

    // Step 2: Convert to 3D using Blender
    const outputPath = path.join(outputDir, `${path.basename(imageFile.filepath)}.glb`);
    const blenderScriptPath = path.join(process.cwd(), 'scripts', 'convert_to_3d.py');

    console.log('Starting Blender conversion...');
    console.log('Input path:', bgRemovedPath);
    console.log('Output path:', outputPath);
    console.log('Blender script path:', blenderScriptPath);

    const blenderProcess = spawn(process.env.BLENDER_PATH!, [
      '--background',
      '--python',
      blenderScriptPath,
      '--',
      bgRemovedPath,
      outputPath
    ]);

    let blenderOutput = '';
    let blenderError = '';

    blenderProcess.stdout.on('data', (data) => {
      blenderOutput += data.toString();
      console.log(`Blender stdout: ${data}`);
    });

    blenderProcess.stderr.on('data', (data) => {
      blenderError += data.toString();
      console.error(`Blender stderr: ${data}`);
    });

    await new Promise((resolve, reject) => {
      blenderProcess.on('close', (code) => {
        console.log('Blender process completed with code:', code);
        console.log('Full Blender output:', blenderOutput);
        console.log('Full Blender error:', blenderError);
        
        if (code === 0) resolve(null);
        else reject(new Error(`Blender process exited with code ${code}`));
      });
    });

    // Check if the output file was created and has size
    if (!fs.existsSync(outputPath)) {
      throw new Error('Output file was not created');
    }

    const fileStats = fs.statSync(outputPath);
    if (fileStats.size === 0) {
      throw new Error('Output file is empty');
    }

    console.log('Conversion completed successfully');
    console.log('Output file size:', fileStats.size);

    // Copy the GLB file to the public directory for serving
    const publicOutputDir = path.join(process.cwd(), 'public', 'output');
    if (!fs.existsSync(publicOutputDir)) {
      fs.mkdirSync(publicOutputDir, { recursive: true });
    }

    const publicOutputPath = path.join(publicOutputDir, path.basename(outputPath));
    fs.copyFileSync(outputPath, publicOutputPath);

    console.log('File copied to public directory:', publicOutputPath);

    res.status(200).json({ 
      success: true,
      downloadUrl: `/output/${path.basename(outputPath)}`,
    });

  } catch (error) {
    console.error('Conversion error:', error);
    res.status(500).json({ error: 'Error processing the image' });
  }
} 