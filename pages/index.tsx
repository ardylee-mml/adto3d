import { useState, useCallback, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useDropzone } from 'react-dropzone';

// Dynamically import the ModelViewer to avoid SSR issues
const ModelViewer = dynamic(() => import('../components/ModelViewer'), {
  ssr: false
});

interface AnalysisResult {
  dimensions: {
    width: number;
    height: number;
    aspect_ratio: number;
  };
  shape: {
    type: string;
    symmetry: string;
    circularity: number;
  };
  complexity: {
    edge_count: number;
    contour_count: number;
  };
  color: {
    average_rgb: [number, number, number];
  };
}

export default function Home() {
  const [modelUrl, setModelUrl] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (modelUrl) {
      console.log('Model URL updated:', modelUrl);
    }
  }, [modelUrl]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setIsLoading(true);
    setError(null);
    setModelUrl(null); // Reset model URL

    try {
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (data.success) {
        console.log('Full response data:', data);
        setModelUrl(data.modelUrl);
        setAnalysis(data.analysis);
      } else {
        setError(data.error || 'Conversion failed');
      }
    } catch (error) {
      console.error('Conversion error:', error);
      setError('Failed to convert image');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    multiple: false
  });

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-8 text-center">2D to 3D Converter</h1>
      
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed p-8 rounded-lg text-center cursor-pointer
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300'}`}
          >
            <input {...getInputProps()} />
            {isLoading ? (
              <p>Converting...</p>
            ) : (
              <p>Drag & drop an image here, or click to select one</p>
            )}
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
              {error}
            </div>
          )}

          {analysis && (
            <div className="mt-8 p-6 bg-white rounded-lg shadow">
              <h2 className="text-2xl font-bold mb-4">Image Analysis Results</h2>
              
              <div className="space-y-4">
                <section>
                  <h3 className="text-lg font-semibold">Dimensions</h3>
                  <p>Width: {analysis.dimensions.width}px</p>
                  <p>Height: {analysis.dimensions.height}px</p>
                  <p>Aspect Ratio: {analysis.dimensions.aspect_ratio.toFixed(2)}</p>
                </section>

                <section>
                  <h3 className="text-lg font-semibold">Shape Analysis</h3>
                  <p>Type: {analysis.shape.type}</p>
                  <p>Symmetry: {analysis.shape.symmetry}</p>
                  <p>Circularity: {analysis.shape.circularity.toFixed(3)}</p>
                </section>

                <section>
                  <h3 className="text-lg font-semibold">Complexity</h3>
                  <p>Edge Count: {analysis.complexity.edge_count}</p>
                  <p>Contour Count: {analysis.complexity.contour_count}</p>
                </section>

                <section>
                  <h3 className="text-lg font-semibold">Color</h3>
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-6 h-6 rounded"
                      style={{
                        backgroundColor: `rgb(${analysis.color.average_rgb.join(',')})`
                      }}
                    />
                    <span>RGB: ({analysis.color.average_rgb.join(', ')})</span>
                  </div>
                </section>
              </div>
            </div>
          )}
        </div>

        <div>
          {modelUrl && (
            <div className="mt-8">
              <h2 className="text-2xl font-bold mb-4">3D Model Preview</h2>
              <div className="model-viewer-container">
                <ModelViewer modelPath={modelUrl} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 