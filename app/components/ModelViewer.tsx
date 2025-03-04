'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, useProgress } from '@react-three/drei';
import { Box, CircularProgress, Typography, LinearProgress } from '@mui/material';

interface ModelViewerProps {
  modelUrl: string | null;
  conversionId?: string | null;
}

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  
  useEffect(() => {
    return () => {
      if (url) {
        // Preload the model
        useGLTF.preload(url);
        // Clean up loaded resources when component unmounts
        setTimeout(() => {
          useGLTF.clear(url);
        }, 100);
      }
    };
  }, [url]);
  
  return <primitive object={scene} />;
}

const ModelViewer: React.FC<ModelViewerProps> = ({ 
  modelUrl, 
  conversionId
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [key, setKey] = useState(0);
  const { progress, errors } = useProgress();
  const progressValue: number = Number(progress || 0);
  
  useEffect(() => {
    if (modelUrl) {
      setLoading(true);
      setError(null);
      setKey(prevKey => prevKey + 1);
      
      try {
        // Preload the model
        useGLTF.preload(modelUrl);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        console.error('Error loading model:', errorMessage);
        setError(`Failed to load 3D model: ${errorMessage}`);
        setLoading(false);
      }
    }
  }, [modelUrl, conversionId]);

  // Handle progress and errors
  useEffect(() => {
    if (errors.length > 0) {
      setError(`Failed to load 3D model: ${errors[0]}`);
      setLoading(false);
    } else if (progressValue === 100) {
      setLoading(false);
    }
    console.log(`Loading model: ${progressValue}%`);
  }, [progressValue, errors]);

  const containerStyle = {
    width: '100%',
    height: 400,
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: '4px'
  };

  if (!modelUrl) {
    return (
      <div style={containerStyle}>
        <Typography variant="body1" color="textSecondary">
          No model available. Start a conversion to see the 3D preview.
        </Typography>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={containerStyle}>
        <CircularProgress size={40} />
        <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
          Loading 3D Model: {progressValue}%
        </Typography>
        <Box component="div" sx={{ width: '80%', mt: 2 }}>
          <LinearProgress variant="determinate" value={progressValue as number} />
        </Box>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <Typography variant="body1" color="error" gutterBottom>
          {error}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Try downloading and viewing the file locally instead.
        </Typography>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: 400, borderRadius: '4px', overflow: 'hidden' }}>
      <Canvas key={key} camera={{ position: [0, 0, 5], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} />
        <pointLight position={[-10, -10, -10]} />
        <Model url={modelUrl} />
        <OrbitControls />
      </Canvas>
    </div>
  );
};

export default ModelViewer; 