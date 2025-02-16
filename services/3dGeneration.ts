import path from 'path';
import { spawn } from 'child_process';

interface Generation3DParams {
    imageDescription: string;
    shapeAnalysis: {
        type: string;
        dimensions?: {
            width: number;
            height: number;
        };
        symmetry: string;
    };
    referenceImagePath: string;
}

export async function generate3DModel(params: Generation3DParams): Promise<string> {
    console.log('Starting 3D model generation...');
    console.log('Image Description:', params.imageDescription);
    console.log('Shape Analysis:', params.shapeAnalysis);

    // Create output filename
    const outputFileName = `${path.basename(params.referenceImagePath)}.glb`;
    const outputPath = path.join(process.cwd(), 'temp', 'output', outputFileName);
    const analysisPath = path.join(process.cwd(), 'temp', 'output', `${path.basename(params.referenceImagePath)}.json`);

    // Save analysis for Blender
    const analysis = {
        shape: params.shapeAnalysis,
        description: params.imageDescription,
        referenceImage: params.referenceImagePath
    };

    // Call Blender to generate 3D model
    const blenderProcess = spawn('blender', [
        '--background',
        '--python',
        path.join(process.cwd(), 'scripts', 'convert_to_3d.py'),
        '--',
        analysisPath,
        outputPath
    ]);

    return new Promise((resolve, reject) => {
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

        blenderProcess.on('close', (code) => {
            if (code === 0) {
                console.log('3D model generation completed');
                // Return the path relative to the API endpoint
                resolve(`/api/files/${outputFileName}`);
            } else {
                reject(new Error(`Blender failed with code ${code}: ${blenderError}`));
            }
        });
    });
} 