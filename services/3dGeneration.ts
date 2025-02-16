import path from 'path';
import { spawn } from 'child_process';
import fs from 'fs/promises';

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

async function verifyBlenderInstallation(): Promise<boolean> {
    return new Promise((resolve, reject) => {
        const blenderProcess = spawn('blender', ['--version']);

        let output = '';

        blenderProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        blenderProcess.on('error', (err) => {
            console.error('Blender verification failed:', err);
            reject(new Error('Blender is not installed or not accessible'));
        });

        blenderProcess.on('close', (code) => {
            if (code === 0) {
                const version = output.match(/Blender\s+(\d+\.\d+\.\d+)/);
                if (version && version[1] === '3.0.1') {
                    console.log('Verified Blender version:', version[1]);
                    resolve(true);
                } else {
                    reject(new Error(`Incorrect Blender version. Found: ${output.trim()}, Required: 3.0.1`));
                }
            } else {
                reject(new Error(`Blender verification failed with code ${code}`));
            }
        });
    });
}

function getBlenderInfo(): Promise<{ path: string, version: string }> {
    return new Promise((resolve, reject) => {
        const blenderPath = spawn('which', ['blender']);
        let path = '';
        let version = '';

        blenderPath.stdout.on('data', (data) => {
            path = data.toString().trim();
        });

        blenderPath.on('close', async (code) => {
            if (code === 0) {
                const versionProcess = spawn('blender', ['--version']);
                versionProcess.stdout.on('data', (data) => {
                    version = data.toString().trim();
                });

                versionProcess.on('close', (code) => {
                    if (code === 0) {
                        resolve({ path, version });
                    } else {
                        reject(new Error('Could not get Blender version'));
                    }
                });
            } else {
                reject(new Error('Could not find Blender installation'));
            }
        });
    });
}

export async function generate3DModel(params: Generation3DParams): Promise<string> {
    // Verify Blender first
    try {
        await verifyBlenderInstallation();
    } catch (error) {
        console.error('Blender verification failed:', error);
        throw error;
    }

    console.log('Starting 3D model generation...');
    console.log('Image Description:', params.imageDescription);
    console.log('Shape Analysis:', params.shapeAnalysis);

    // Create output filename
    const outputFileName = `${path.basename(params.referenceImagePath)}.glb`;
    const outputPath = path.join(process.cwd(), 'temp', 'output', outputFileName);
    const analysisPath = path.join(process.cwd(), 'temp', 'output', `${path.basename(params.referenceImagePath)}.json`);

    // Ensure output directory exists
    await fs.mkdir(path.dirname(outputPath), { recursive: true });

    // Save analysis for Blender
    const analysis = {
        shape: params.shapeAnalysis,
        description: params.imageDescription,
        referenceImage: params.referenceImagePath
    };

    // Write the analysis JSON file
    try {
        await fs.writeFile(analysisPath, JSON.stringify(analysis, null, 2));
    } catch (error) {
        console.error('Failed to write analysis file:', error);
        throw new Error('Failed to create analysis file for Blender');
    }

    // Return a proper promise for the Blender process
    return new Promise((resolve, reject) => {
        const blenderProcess = spawn('blender', [
            '--background',
            '--python',
            path.join(process.cwd(), 'scripts', 'convert_to_3d.py'),
            '--',
            analysisPath,
            outputPath
        ]);

        blenderProcess.on('error', (err) => {
            console.error('Failed to start Blender process:', err);
            reject(new Error('Blender process failed to start'));
        });

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
                resolve(outputFileName);
            } else {
                reject(new Error(`Blender failed with code ${code}: ${blenderError}`));
            }
        });
    });
} 