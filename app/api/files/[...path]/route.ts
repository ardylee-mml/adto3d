import { NextRequest, NextResponse } from 'next/server';
import path from 'path';
import fs from 'fs';

export async function GET(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    try {
        // Join the path segments and create the full file path
        const filePath = path.join(process.cwd(), 'temp', 'output', ...params.path);
        console.log('Attempting to serve file:', filePath);  // Debug log

        // Check if file exists
        if (!fs.existsSync(filePath)) {
            console.error('File not found:', filePath);  // Debug log
            return new NextResponse('File not found', { status: 404 });
        }

        // Read file
        const fileBuffer = fs.readFileSync(filePath);
        console.log('File size:', fileBuffer.length);  // Debug log

        // Determine content type based on file extension
        const ext = path.extname(filePath).toLowerCase();
        const contentType = {
            '.glb': 'model/gltf-binary',
            '.fbx': 'application/octet-stream',
            '.usdz': 'model/vnd.usdz+zip',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }[ext] || 'application/octet-stream';

        // Return file with appropriate headers
        const response = new NextResponse(fileBuffer, {
            headers: {
                'Content-Type': contentType,
                'Content-Length': fileBuffer.length.toString(),
                'Cache-Control': 'no-cache',
                'Access-Control-Allow-Origin': '*',
            },
        });

        return response;
    } catch (error) {
        console.error('Error serving file:', error);
        return new NextResponse('Internal Server Error', { status: 500 });
    }
} 