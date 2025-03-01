import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(
    request: NextRequest,
    { params }: { params: { filename: string } }
): Promise<Response> {
    try {
        const filename = params.filename;
        const uploadsDir = path.join(process.cwd(), 'uploads');
        const filePath = path.join(uploadsDir, filename);

        // Check if file exists
        if (!fs.existsSync(filePath)) {
            return new NextResponse('File not found', { status: 404 });
        }

        // Read file and get its mime type
        const file = fs.readFileSync(filePath);
        const mimeType = filename.toLowerCase().endsWith('.jpg') || filename.toLowerCase().endsWith('.jpeg')
            ? 'image/jpeg'
            : filename.toLowerCase().endsWith('.png')
                ? 'image/png'
                : 'application/octet-stream';

        // Return file with appropriate headers
        return new NextResponse(file, {
            headers: {
                'Content-Type': mimeType,
                'Content-Length': file.length.toString(),
                'Cache-Control': 'public, max-age=31536000',
                'Access-Control-Allow-Origin': '*'
            }
        });
    } catch (error) {
        console.error('Error serving image:', error);
        return new NextResponse('Internal Server Error', { status: 500 });
    }
} 