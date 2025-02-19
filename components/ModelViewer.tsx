import { Suspense, useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import { config } from '../config/environment';

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url, undefined, undefined, (error) => {
    console.error('Error loading model:', error);
  });

  useEffect(() => {
    console.log('Model loaded:', { scene });
  }, [scene]);

  return (
    <primitive 
      object={scene} 
      scale={[1, 1, 1]}
      rotation={[0, 0, 0]}
      position={[0, 0, 0]}
    />
  );
}

function LoadingFallback() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="gray" />
    </mesh>
  );
}

interface ModelViewerProps {
  modelPath: string;
}

export default function ModelViewer({ modelPath }: ModelViewerProps) {
  const viewerRef = useRef<HTMLDivElement>(null);
  
  if (!modelPath) {
    return <div>No model path provided</div>;
  }

  const fullPath = modelPath.startsWith('http') 
    ? modelPath 
    : `/temp/output/${modelPath.split('/').pop()}`;

  useEffect(() => {
    console.log('Original model path:', modelPath);
    console.log('Processed model path:', fullPath);
  }, [modelPath, fullPath]);

  return (
    <div ref={viewerRef} style={{ width: '100%', height: '500px' }}>
      <Canvas camera={{ position: [2, 2, 2], fov: 50 }}>
        <ambientLight intensity={1} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight
          position={[5, 5, 5]}
          angle={0.15}
          penumbra={1}
          intensity={2}
          castShadow
        />
        <Suspense fallback={<LoadingFallback />}>
          <Model url={fullPath} />
        </Suspense>
        <OrbitControls makeDefault />
      </Canvas>
    </div>
  );
}
