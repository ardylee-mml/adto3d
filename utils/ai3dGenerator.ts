import fs from 'fs';

interface GenerationParams {
    shape: string;
    color: number[];
    dimensions: {
        width: number;
        height: number;
    };
    style: string;
    imagePath: string;
}

async function analyzeImageContent(imagePath: string): Promise<string> {
    // First, get detailed description of the image using Deepseek
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');

    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer sk-f5c55a5ce8a3493fbc5e806fa9395ea9'
        },
        body: JSON.stringify({
            model: "deepseek-chat",
            messages: [
                {
                    role: "system",
                    content: "You are a detailed image analyzer. Describe the image in detail, focusing on physical characteristics, design elements, and branding."
                },
                {
                    role: "user",
                    content: "Analyze this image and provide a detailed description of what you see, focusing on physical characteristics and design elements."
                }
            ],
            max_tokens: 1000
        })
    });

    const data = await response.json();
    return data.choices[0].message.content;
}

async function generate3DModel(imageDescription: string, shape: string, dimensions: any): Promise<string> {
    // Use Deepseek to generate 3D model instructions based on the analysis
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer sk-f5c55a5ce8a3493fbc5e806fa9395ea9'
        },
        body: JSON.stringify({
            model: "deepseek-chat",
            messages: [
                {
                    role: "system",
                    content: "You are a 3D modeling expert. Generate detailed instructions for creating a 3D model based on the provided description and specifications."
                },
                {
                    role: "user",
                    content: `Create detailed 3D modeling instructions for the following object:
                    
                    Image Description: ${imageDescription}
                    Shape Type: ${shape}
                    Dimensions: Width ${dimensions.width}px, Height ${dimensions.height}px
                    
                    Provide specific details about:
                    1. Overall 3D structure
                    2. Surface details and texturing
                    3. Important design elements to preserve
                    4. Material properties
                    5. Specific measurements and proportions`
                }
            ],
            max_tokens: 1500
        })
    });

    const data = await response.json();
    return data.choices[0].message.content;
}

export async function generateAI3DModel(params: GenerationParams): Promise<string> {
    try {
        // Step 1: Get detailed image description
        console.log('Analyzing image content...');
        const imageDescription = await analyzeImageContent(params.imagePath);

        // Step 2: Generate 3D model instructions
        console.log('Generating 3D model instructions...');
        const modelInstructions = await generate3DModel(
            imageDescription,
            params.shape,
            params.dimensions
        );

        return modelInstructions;
    } catch (error) {
        console.error('AI generation error:', error);
        return `A ${params.shape} 3D model with RGB(${params.color.join(', ')}) color scheme.`;
    }
} 