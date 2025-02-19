import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

export async function POST(req: NextRequest) {
    console.log('Received conversion request');
    try {
        const formData = await req.formData();
        console.log('Parsed form data');
        const file = formData.get('file') as File;
        const fileName = formData.get('fileName') as string;

        console.log('Received file:', {
            fileName,
            fileSize: file?.size,
            fileType: file?.type,
            fileKeys: Object.keys(file || {})
        });

        if (!file || !fileName) {
            console.log('Missing required fields');
            return NextResponse.json({
                success: false,
                error: 'File and fileName are required'
            }, { status: 400 });
        }

        // Save uploaded file temporarily
        const outputDir = path.join(process.cwd(), 'temp', 'output');
        console.log('Creating output directory:', outputDir);
        fs.mkdirSync(outputDir, { recursive: true });

        const filePath = path.join(outputDir, file.name || 'uploaded_file.png');
        console.log('Saving file to:', filePath);

        // Convert file to buffer and save
        try {
            if (!file.arrayBuffer) {
                throw new Error('File object does not have arrayBuffer method');
            }
            const bytes = await file.arrayBuffer();
            fs.writeFileSync(filePath, Buffer.from(bytes));
            console.log('File saved successfully');
        } catch (error) {
            console.error('Error saving file:', error);
            return NextResponse.json({
                success: false,
                error: `Error saving file: ${error.message}`
            }, { status: 500 });
        }

        // Verify Python script exists
        const scriptPath = path.join(process.cwd(), 'scripts', 'convert_image.py');
        if (!fs.existsSync(scriptPath)) {
            console.error('Python script not found:', scriptPath);
            return NextResponse.json({
                success: false,
                error: 'Conversion script not found'
            }, { status: 500 });
        }

        console.log('Starting Python conversion...', {
            scriptPath,
            filePath,
            fileName
        });

        // Run the working Python conversion script
        return new Promise((resolve, reject) => {
            const pythonProcess = spawn('python3', [
                scriptPath,
                filePath,
                fileName
            ]);

            let outputData = '';
            let errorData = '';

            pythonProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log('Python stdout:', output);
                outputData += output;

                // Try to parse progress updates
                try {
                    const lines = output.split('\n');
                    for (const line of lines) {
                        if (line.trim()) {
                            const data = JSON.parse(line);
                            if (data.type === 'progress') {
                                // Send progress to client (if using WebSocket/SSE)
                                console.log('Progress:', {
                                    stage: data.stage,
                                    progress: data.progress,
                                    message: data.message
                                });
                            }
                        }
                    }
                } catch (e) {
                    // Not a JSON line, ignore
                }
            });

            pythonProcess.stderr.on('data', (data) => {
                const error = data.toString();
                console.error('Python stderr:', error);
                errorData += error;
            });

            pythonProcess.on('close', (code) => {
                console.log('Python process closed with code:', code);
                if (code === 0) {
                    try {
                        // Find the last complete JSON object that starts with {"success":
                        const jsonMatch = outputData.match(/\{"success":.*\}/s);
                        if (!jsonMatch) {
                            console.error('No valid JSON found in output:', outputData);
                            throw new Error('No valid JSON output found');
                        }

                        const result = JSON.parse(jsonMatch[0]);
                        console.log('Parsed result:', result);

                        // Verify the format
                        if (!result.success || !result.outputs) {
                            console.error('Invalid result format:', result);
                            throw new Error('Invalid result format from conversion script');
                        }

                        // Clean up the temporary file
                        try {
                            fs.unlinkSync(filePath);
                        } catch (e) {
                            console.error('Error cleaning up file:', e);
                        }

                        resolve(NextResponse.json(result));
                    } catch (e) {
                        console.error('Failed to parse Python output:', e, '\nOutput:', outputData);
                        reject(new Error('Invalid output from conversion script'));
                    }
                } else {
                    reject(new Error(`Conversion failed: ${errorData}`));
                }
            });

            pythonProcess.on('error', (err) => {
                console.error('Failed to start Python process:', err);
                reject(new Error('Failed to start conversion process'));
            });
        });
    } catch (error) {
        console.error('Conversion error:', error);
        return NextResponse.json({
            success: false,
            error: error.message
        }, { status: 500 });
    }
} 