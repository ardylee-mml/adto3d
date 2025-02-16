import { NextApiRequest, NextApiResponse } from 'next';
import formidable from 'formidable';
import path from 'path';
import fs from 'fs';
import { spawn } from 'child_process';
import process from 'process';
import { generateAI3DModel } from '../../utils/ai3dGenerator';
import { generate3DModel } from '../../services/3dGeneration';
import { performOpenCVAnalysis } from '../../utils/openCVAnalysis';

// Add type definitions for formidable
type FormidableParseReturn = {
  fields: formidable.Fields;
  files: formidable.Files;
};

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
  object_detection: {
    class: string;
    confidence: number;
    category: string;
    subcategory?: string;
    attributes?: {
      material?: string;
      style?: string;
      features?: string[];
    };
  };
  generated_prompt: string;
  ai_generation?: {
    description: string;
    timestamp: string;
  };
}

const VM_BASE_PATH = '/home/mml_admin/2dto3d';

// Disable the default body parser to handle form data
export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  let analysis: AnalysisResult | null = null;  // Declare analysis at the top

  try {
    const form = formidable({
      uploadDir: path.join(process.cwd(), 'temp', 'uploads'),
      keepExtensions: true,
    });

    // Parse the form using a Promise wrapper
    const [_, files] = await new Promise<[formidable.Fields, formidable.Files]>((resolve, reject) => {
      form.parse(req, (err, fields, files) => {
        if (err) reject(err);
        resolve([fields, files]);
      });
    });

    const imageFile = Array.isArray(files.image) ? files.image[0] : files.image;
    if (!imageFile) {
      console.error('No image file provided');
      return res.status(400).json({ error: 'No image file provided' });
    }

    console.log('Image received:', imageFile.filepath);

    // Step 1: OpenCV Analysis
    const analysis = await performOpenCVAnalysis(imageFile.filepath);

    // Step 2: AI Understanding & 3D Instructions
    const modelInstructions = await generateAI3DModel({
      shape: analysis.shape.type,
      color: analysis.color.average_rgb,
      dimensions: analysis.dimensions,
      style: 'detailed',
      imagePath: imageFile.filepath
    });

    // Step 3: Generate 3D Model using AI
    const modelPath = await generate3DModel({
      imageDescription: modelInstructions,
      shapeAnalysis: {
        type: analysis.shape.type,
        dimensions: analysis.dimensions,
        symmetry: analysis.shape.symmetry
      },
      referenceImagePath: imageFile.filepath
    });

    res.status(200).json({
      success: true,
      analysis: analysis,
      modelUrl: modelPath,
      aiDescription: modelInstructions
    });

  } catch (error) {
    console.error('Conversion error:', error);
    res.status(500).json({ error: 'Internal server error during conversion' });
  }
} 