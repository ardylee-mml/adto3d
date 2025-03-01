import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

export async function POST(req: NextRequest): Promise<Response> {
    console.log('Received image validation request');
    try {
        const formData = await req.formData();
        const file = formData.get('file') as File;

        console.log('Received file:', {
            fileSize: file?.size,
            fileType: file?.type,
        });

        if (!file) {
            return NextResponse.json({
                success: false,
                error: 'File is required'
            }, { status: 400 });
        }

        // Save uploaded file temporarily
        const uploadsDir = path.join(process.cwd(), 'temp', 'uploads');
        fs.mkdirSync(uploadsDir, { recursive: true });
        const filePath = path.join(uploadsDir, file.name);

        const bytes = await file.arrayBuffer();
        fs.writeFileSync(filePath, Buffer.from(bytes));

        // Run validation script
        const scriptPath = path.join(process.cwd(), 'scripts', 'validate_image.py');

        return new Promise((resolve, reject) => {
            const pythonProcess = spawn('python3', [
                scriptPath,
                filePath
            ]);

            let outputData = '';

            pythonProcess.stdout.on('data', (data) => {
                outputData += data.toString();
            });

            pythonProcess.on('close', (code) => {
                try {
                    // Clean up temp file
                    fs.unlinkSync(filePath);

                    const result = JSON.parse(outputData);
                    resolve(NextResponse.json(result, {
                        status: result.success ? 200 : 400
                    }));
                } catch (e) {
                    resolve(NextResponse.json({
                        success: false,
                        error: 'Failed to validate image'
                    }, { status: 500 }));
                }
            });
        });
    } catch (error) {
        return NextResponse.json({
            success: false,
            error: error.message
        }, { status: 500 });
    }
} 