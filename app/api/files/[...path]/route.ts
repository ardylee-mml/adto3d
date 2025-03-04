import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { headers } from 'next/headers';

export async function GET(
    request: NextRequest,
    { params }: { params: { path: string[] } }
) {
    try {
        const filePath = path.join(process.cwd(), ...params.path);

        // Check if file exists
        if (!fs.existsSync(filePath)) {
            return new NextResponse('File not found', { status: 404 });
        }

        // Get file stats
        const stat = fs.statSync(filePath);

        // Read file
        const fileBuffer = fs.readFileSync(filePath);

        // Determine content type based on file extension
        const ext = path.extname(filePath).toLowerCase();
        let contentType = 'application/octet-stream';

        switch (ext) {
            case '.png':
            case '.jpg':
            case '.jpeg':
                contentType = `image/${ext.substring(1)}`;
                break;
            case '.glb':
                contentType = 'model/gltf-binary';
                break;
            case '.fbx':
                contentType = 'application/octet-stream';
                break;
            case '.usdz':
                contentType = 'model/vnd.usdz+zip';
                break;
            case '.json':
                contentType = 'application/json';
                break;
        }

        // Get filename for Content-Disposition header
        const filename = path.basename(filePath);

        // Check if this is a download request
        const headersList = headers();
        const isDownload = headersList.get('x-download') === 'true';

        // Set appropriate headers
        const responseHeaders: Record<string, string> = {
            'Content-Type': contentType,
            'Content-Length': stat.size.toString(),
            'Accept-Ranges': 'bytes',
        };

        // Add Content-Disposition header for downloads
        if (isDownload) {
            responseHeaders['Content-Disposition'] = `attachment; filename="${filename}"`;
        } else {
            responseHeaders['Content-Disposition'] = `inline; filename="${filename}"`;
        }

        return new NextResponse(fileBuffer, {
            status: 200,
            headers: responseHeaders,
        });
    } catch (error) {
        console.error('Error serving file:', error);
        return new NextResponse('Internal Server Error', { status: 500 });
    }
} 