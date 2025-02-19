import { NextRequest, NextResponse } from 'next/server';
import { writeFile } from 'fs/promises';
import { mkdir } from 'fs/promises';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const file = formData.get('model') as File;

        if (!file) {
            return new NextResponse('No file uploaded', { status: 400 });
        }

        // Create unique filename
        const filename = `modified_${uuidv4()}.glb`;

        // Ensure directory exists
        const saveDir = path.join(process.cwd(), 'temp', 'modified');
        await mkdir(saveDir, { recursive: true });

        // Save file
        const filePath = path.join(saveDir, filename);
        const bytes = await file.arrayBuffer();
        await writeFile(filePath, Buffer.from(bytes));

        // Return the URL to access the file
        return NextResponse.json({
            success: true,
            url: `/api/files/modified/${filename}`
        });
    } catch (error) {
        console.error('Error saving model:', error);
        return new NextResponse('Error saving model', { status: 500 });
    }
} 