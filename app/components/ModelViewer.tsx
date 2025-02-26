'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage } from '@react-three/drei';
import { Box, CircularProgress, Typography, ButtonGroup, Button } from '@mui/material';

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
  fbxUrl?: string;
  isOutfit?: boolean;
  outfitType?: string;
  style?: React.CSSProperties;
}

export default function ModelViewer({ 
  glbUrl, 
  fbxUrl,
  isOutfit,
  outfitType,
  style 
}: ModelViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'original' | 'processed'>('processed');

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
    <Box>
      {isOutfit && (
        <Box sx={{ mb: 2 }}>
          <ButtonGroup>
            <Button
              variant={viewMode === 'original' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('original')}
            >
              Original
            </Button>
            <Button
              variant={viewMode === 'processed' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('processed')}
            >
              Processed for Roblox
            </Button>
          </ButtonGroup>
        </Box>
      )}
      
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
      
      {isOutfit && (
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          {viewMode === 'processed' 
            ? `Processed for Roblox (${outfitType})` 
            : 'Original Masterpiece conversion'}
        </Typography>
      )}
    </Box>
  );
} 