import { spawn } from 'child_process';
import path from 'path';

interface AnalysisResult {
    dimensions: {
        width: number;
        height: number;
        aspect_ratio: number;
    };
    complexity: {
        edge_count: number;
        contour_count: number;
    };
    color: {
        average_rgb: number[];
    };
    shape: {
        type: string;
        circularity: number;
        symmetry: string;
    };
    generated_prompt: string;
}

export async function performOpenCVAnalysis(imagePath: string): Promise<AnalysisResult> {
    console.log('Starting OpenCV analysis...');
    const analysisProcess = spawn('python3', [
        path.join(process.cwd(), 'scripts', 'analyze_image.py'),
        imagePath
    ]);

    const analysisResult = await new Promise<string>((resolve, reject) => {
        let output = '';
        let error = '';

        analysisProcess.stdout.on('data', (data) => {
            output += data.toString();
            console.log('OpenCV analysis output:', data.toString());
        });

        analysisProcess.stderr.on('data', (data) => {
            error += data.toString();
            console.error('OpenCV analysis error:', data.toString());
        });

        analysisProcess.on('close', (code) => {
            if (code === 0) {
                // Find and extract the JSON object from the output
                const jsonMatch = output.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    resolve(jsonMatch[0]);
                } else {
                    reject(new Error('No valid JSON found in output'));
                }
            } else {
                reject(new Error(`Analysis failed with code ${code}: ${error}`));
            }
        });
    });

    const analysis = JSON.parse(analysisResult) as AnalysisResult;
    console.log('OpenCV analysis completed:', analysis);
    return analysis;
} 