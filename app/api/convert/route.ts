import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

export async function POST(req: NextRequest): Promise<Response> {
    console.log('Received conversion request');
    try {
        const formData = await req.formData();

        // Get the uploaded file
        const file = formData.get('file');
        const isOutfit = formData.get('isOutfit') === 'true';
        const outfitType = formData.get('outfitType') as string | null;

        if (!file || !(file instanceof Blob)) {
            console.error('No valid file received');
            return NextResponse.json({
                success: false,
                error: 'No valid file uploaded'
            }, { status: 400 });
        }

        // Get the original filename
        const originalFilename = (file as File).name;
        if (!originalFilename) {
            console.error('No filename in uploaded file');
            return NextResponse.json({
                success: false,
                error: 'No filename in uploaded file'
            }, { status: 400 });
        }

        console.log('Processing file:', originalFilename);

        // Ensure uploads directory exists
        const uploadsDir = '/home/mml_admin/2dto3d/uploads';
        try {
            if (!fs.existsSync(uploadsDir)) {
                console.log('Creating uploads directory');
                await fs.promises.mkdir(uploadsDir, { recursive: true });
            }
        } catch (error) {
            console.error('Failed to create uploads directory:', error);
            return NextResponse.json({
                success: false,
                error: 'Server configuration error'
            }, { status: 500 });
        }

        // Save the uploaded file
        const uploadFilePath = path.join(uploadsDir, originalFilename);
        console.log('Saving file to:', uploadFilePath);

        try {
            const buffer = Buffer.from(await file.arrayBuffer());
            await fs.promises.writeFile(uploadFilePath, buffer);

            // Verify file was saved
            const stats = await fs.promises.stat(uploadFilePath);
            console.log('File saved:', {
                path: uploadFilePath,
                size: stats.size
            });
        } catch (error) {
            console.error('Failed to save file:', error);
            return NextResponse.json({
                success: false,
                error: 'Failed to save uploaded file'
            }, { status: 500 });
        }

        // Run Python script using the original filename for both input and output
        return await new Promise<Response>((resolve) => {
            const outputBaseName = path.parse(originalFilename).name; // Remove extension

            console.log('Starting conversion:', {
                input: uploadFilePath,
                outputBase: outputBaseName
            });

            const pythonProcess = spawn('python3', [
                path.join(process.cwd(), 'scripts', 'convert_to_3d.py'),
                '-i', uploadFilePath,
                '-o', path.join(process.cwd(), 'temp', 'output', `${outputBaseName}.glb`)
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
                try {
                    // Process output and check for files
                    const basePath = path.join(process.cwd(), 'temp', 'output', outputBaseName);
                    const files = [
                        `${outputBaseName}.glb`,
                        isOutfit ? `${outputBaseName}_processed.fbx` : `${outputBaseName}.fbx`,
                        `${outputBaseName}.usdz`,
                        `${outputBaseName}_preview.png`
                    ];

                    // Check if files exist
                    const missingFiles = files.filter(file =>
                        !fs.existsSync(path.join(basePath, file))
                    );

                    if (missingFiles.length > 0) {
                        resolve(NextResponse.json({
                            success: false,
                            error: 'Processing failed',
                            details: `Missing files: ${missingFiles.join(', ')}`
                        }, { status: 500 }));
                        return;
                    }

                    // Return success response
                    resolve(NextResponse.json({
                        success: true,
                        message: 'Conversion complete',
                        outputs: {
                            glb: `/output/${outputBaseName}.glb`,
                            fbx: `/output/${isOutfit ? outputBaseName + '_processed.fbx' : outputBaseName + '.fbx'}`,
                            usdz: `/output/${outputBaseName}.usdz`,
                            preview: `/output/${outputBaseName}_preview.png`
                        }
                    }));
                } catch (error) {
                    console.error('Error processing conversion:', error);
                    resolve(NextResponse.json({
                        success: false,
                        error: 'Conversion processing failed',
                        details: error.message
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