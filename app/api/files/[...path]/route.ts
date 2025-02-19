import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
    try {
        const filePath = path.join(process.cwd(), 'temp', 'output', ...params.path);

        if (!fs.existsSync(filePath)) {
            return new NextResponse('File not found', { status: 404 });
        }

        const fileBuffer = fs.readFileSync(filePath);
        const fileName = path.basename(filePath);
        const ext = path.extname(fileName).toLowerCase();

        let contentType = 'application/octet-stream';
        if (ext === '.glb') contentType = 'model/gltf-binary';
        if (ext === '.fbx') contentType = 'application/octet-stream';
        if (ext === '.usdz') contentType = 'model/vnd.usdz+zip';
        if (ext === '.png') contentType = 'image/png';

        return new NextResponse(fileBuffer, {
            headers: {
                'Content-Type': contentType,
                'Content-Disposition': `inline; filename="${fileName}"`,
            },
        });
    } catch (error) {
        console.error('Error serving file:', error);
        return new NextResponse('Internal Server Error', { status: 500 });
    }
} 