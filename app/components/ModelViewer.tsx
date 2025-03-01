'use client';

import { useEffect, useRef, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage } from '@react-three/drei';
import { Box, CircularProgress, Typography, ButtonGroup, Button } from '@mui/material';
import React from 'react';

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

  const boxStyles = {
    width: '100%',
    height: '400px',
    position: 'relative',
    bgcolor: '#f5f5f5',
    borderRadius: '8px'
  } as const;

  return React.createElement(Box, { sx: boxStyles }, 
    React.createElement(Canvas, 
      { 
        camera: { position: [0, 0, 5], fov: 50 },
        style: { width: '100%', height: '100%' },
        children: [
          React.createElement(Stage, { environment: "city", intensity: 0.5, key: "stage" }),
          React.createElement(Model, { url: glbUrl, key: "model" }),
          React.createElement(OrbitControls, { makeDefault: true, key: "controls" })
        ]
      }
    )
  );
} 