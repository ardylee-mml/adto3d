'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage } from '@react-three/drei';
import { Box, CircularProgress, Typography } from '@mui/material';

function Model({ url }: { url: string }) {
  const [error, setError] = useState<string | null>(null);
  
  try {
    const { scene } = useGLTF(url);
    return <primitive object={scene} />;
  } catch (err) {
    console.error('Error loading model:', err);
    return null;
  }
}

interface ModelViewerProps {
  glbUrl: string;
}

export default function ModelViewer({ glbUrl }: ModelViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Test if the URL is accessible
    fetch(glbUrl)
      .then(response => {
        if (!response.ok) throw new Error('Model not ready yet');
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading model:', err);
        setError('Model is still processing. Please wait...');
        setLoading(false);
      });
  }, [glbUrl]);

  return (
    <Box
      ref={containerRef}
      sx={{
        width: '100%',
        height: '400px',
        position: 'relative',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <Canvas
          camera={{ position: [0, 0, 5], fov: 50 }}
          style={{ width: '100%', height: '100%' }}
        >
          <Stage environment="city" intensity={0.5}>
            <Model url={glbUrl} />
          </Stage>
          <OrbitControls
            autoRotate
            autoRotateSpeed={2}
            enableZoom={true}
            enablePan={true}
            minDistance={2}
            maxDistance={10}
          />
        </Canvas>
      )}
    </Box>
  );
} 