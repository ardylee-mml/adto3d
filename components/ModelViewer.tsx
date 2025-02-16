import { Suspense, useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF } from '@react-three/drei';
import { config } from '../config/environment';

function Model({ url }: { url: string }) {
  const { scene, nodes, materials } = useGLTF(url, undefined, undefined, (error) => {
    console.error('Error loading model:', error);
  });

  useEffect(() => {
    console.log('Model loaded:', { scene, nodes, materials });
  }, [scene, nodes, materials]);

  return <primitive object={scene} scale={[1, 1, 1]} />;
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
    : modelPath;

  useEffect(() => {
    console.log('Original model path:', modelPath);
    console.log('Processed model path:', fullPath);
  }, [modelPath, fullPath]);

  return (
    <div ref={viewerRef} style={{ width: '100%', height: '500px' }}>
      <Canvas camera={{ position: [0, 0, 5] }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <Suspense fallback={<LoadingFallback />}>
          <Model url={fullPath} />
        </Suspense>
        <OrbitControls />
      </Canvas>
    </div>
  );
}
