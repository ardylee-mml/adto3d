import { useEffect, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, useGLTF, Stage } from "@react-three/drei";

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  useEffect(() => {
    // Cleanup
    return () => {
      useGLTF.preload(url);
    };
  }, [url]);

  return (
    <Stage environment="city" intensity={0.6}>
      <primitive object={scene} scale={[0.5, 0.5, 0.5]} />
    </Stage>
  );
}

export default function ModelViewer({ modelUrl }: { modelUrl: string }) {
  return (
    <div style={{ width: "100%", height: "400px", background: "#f0f0f0" }}>
      <Canvas
        camera={{
          position: [0, 0, 5],
          fov: 50,
        }}
        shadows
      >
        <ambientLight intensity={0.5} />
        <spotLight
          position={[10, 10, 10]}
          angle={0.15}
          penumbra={1}
          castShadow
        />
        <Model url={modelUrl} />
        <OrbitControls
          makeDefault
          minPolarAngle={0}
          maxPolarAngle={Math.PI / 1.75}
        />
      </Canvas>
    </div>
  );
}
