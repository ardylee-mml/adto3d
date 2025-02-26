import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

export async function POST(req: NextRequest) {
    console.log('Received conversion request');
    try {
        const formData = await req.formData();
        const file = formData.get('file') as File;
        const fileName = formData.get('fileName') as string;
        const isOutfit = formData.get('isOutfit') === 'true';
        const outfitType = formData.get('outfitType') as string | null;

        if (!file || !fileName) {
            return NextResponse.json({
                success: false,
                error: 'File and fileName are required'
            }, { status: 400 });
        }

        // Save uploaded file temporarily
        const uploadsDir = path.join(process.cwd(), 'temp', 'uploads');
        fs.mkdirSync(uploadsDir, { recursive: true });
        const filePath = path.join(uploadsDir, file.name);

        const bytes = await file.arrayBuffer();
        fs.writeFileSync(filePath, Buffer.from(bytes));

        // Run Python script with outfit parameters
        return new Promise((resolve) => {
            const pythonProcess = spawn('python3', [
                path.join(process.cwd(), 'scripts', 'convert_image.py'),
                filePath,
                fileName,
                isOutfit ? 'true' : 'false',
                outfitType || ''
            ]);

            let outputData = '';
            let errorData = '';

            pythonProcess.stdout.on('data', (data) => {
                console.log('Python stdout:', data.toString());
                outputData += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                console.error('Python stderr:', data.toString());
                errorData += data.toString();
            });

            pythonProcess.on('close', (code) => {
                // Clean up uploaded file
                try {
                    fs.unlinkSync(filePath);
                } catch (e) {
                    console.error('Error cleaning up file:', e);
                }

                try {
                    // Get the last line of output which should be our JSON
                    const lines = outputData.trim().split('\n');
                    const lastLine = lines[lines.length - 1];
                    const result = JSON.parse(lastLine);

                    console.log('Parsed result:', result);

                    if (result.success) {
                        const basePath = path.join(process.cwd(), 'temp', 'output', fileName);
                        const files = [
                            `${fileName}.glb`,
                            isOutfit ? `${fileName}_processed.fbx` : `${fileName}.fbx`,
                            `${fileName}.usdz`,
                            `${fileName}_preview.png`
                        ];

                        // Check if files exist
                        const missingFiles = files.filter(file =>
                            !fs.existsSync(path.join(basePath, file))
                        );

                        if (missingFiles.length > 0) {
                            console.error('Missing files:', missingFiles);
                            resolve(NextResponse.json({
                                success: false,
                                error: 'Processing failed',
                                details: `Missing files: ${missingFiles.join(', ')}`
                            }, { status: 500 }));
                            return;
                        }

                        // If processing succeeded, return the result
                        resolve(NextResponse.json(result));
                    } else {
                        resolve(NextResponse.json(result, { status: 400 }));
                    }
                } catch (e) {
                    console.error('Error parsing output:', e);
                    console.error('Raw output:', outputData);
                    console.error('Error output:', errorData);
                    resolve(NextResponse.json({
                        success: false,
                        error: 'Failed to process output',
                        details: errorData || outputData
                    }, { status: 500 }));
                }
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