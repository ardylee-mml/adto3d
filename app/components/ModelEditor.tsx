'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { Canvas, useThree, useLoader } from '@react-three/fiber';
import { OrbitControls, TransformControls, useGLTF, Stage, PivotControls } from '@react-three/drei';
import { Object3D } from 'three';
import { 
  Box, 
  Button, 
  Slider, 
  Typography, 
  Paper, 
  Grid, 
  IconButton,
  Select,
  MenuItem,
  TextField,
  Tabs,
  Tab,
} from '@mui/material';
import { 
  Mesh, 
  Group as ThreeGroup, 
  TextureLoader, 
  MeshStandardMaterial, 
  Vector2,
  Vector3,
  NormalBlending,
  MultiplyBlending,
  AdditiveBlending,
  SubtractiveBlending,
} from 'three';
import AddPhotoAlternateIcon from '@mui/icons-material/AddPhotoAlternate';
import DeleteIcon from '@mui/icons-material/Delete';
import { LogoTexture, UVSettings } from './interfaces/TextureTypes';
import { v4 as uuidv4 } from 'uuid';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter';
import SaveIcon from '@mui/icons-material/Save';
import React from 'react';

const blendModes = {
  'normal': NormalBlending,
  'multiply': MultiplyBlending,
  'add': AdditiveBlending,
  'subtract': SubtractiveBlending,
};

function TextureControls({ 
  logo, 
  onUpdate, 
  onDelete 
}: { 
  logo: LogoTexture; 
  onUpdate: (updated: LogoTexture) => void;
  onDelete: () => void;
}) {
  return React.createElement(
    Box,
    { sx: { mb: 3 } },
    [
      React.createElement(
        Box,
        { 
          sx: { 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            mb: 1 
          },
          key: "header"
        },
        [
          React.createElement(Typography, { variant: "subtitle2", key: "title" }, "Logo Settings"),
          React.createElement(IconButton, { onClick: onDelete, size: "small", key: "delete" }, 
            React.createElement(DeleteIcon)
          )
        ]
      ),
      React.createElement(
        Typography,
        { variant: "caption", key: "scale-label" },
        "Scale"
      ),
      React.createElement(
        Grid,
        { container: true, spacing: 1, key: "scale-controls" },
        [
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "x-slider" },
            React.createElement(Slider, {
              value: logo.scale.x,
              onChange: (_, value) => onUpdate({ ...logo, scale: { ...logo.scale, x: value as number } }),
              min: 0.1,
              max: 2,
              step: 0.1,
              key: "x-slider"
            })
          ),
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "y-slider" },
            React.createElement(Slider, {
              value: logo.scale.y,
              onChange: (_, value) => onUpdate({ ...logo, scale: { ...logo.scale, y: value as number } }),
              min: 0.1,
              max: 2,
              step: 0.1,
              key: "y-slider"
            })
          )
        ]
      ),
      React.createElement(
        Typography,
        { variant: "caption", key: "position-label" },
        "Position"
      ),
      React.createElement(
        Grid,
        { container: true, spacing: 1, key: "position-controls" },
        [
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "x-position" },
            React.createElement(Slider, {
              value: logo.position.x,
              onChange: (_, value) => onUpdate({ ...logo, position: { ...logo.position, x: value as number } }),
              min: -1,
              max: 1,
              step: 0.1,
              key: "x-position-slider"
            })
          ),
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "y-position" },
            React.createElement(Slider, {
              value: logo.position.y,
              onChange: (_, value) => onUpdate({ ...logo, position: { ...logo.position, y: value as number } }),
              min: -1,
              max: 1,
              step: 0.1,
              key: "y-position-slider"
            })
          )
        ]
      ),
      React.createElement(
        Typography,
        { variant: "caption", key: "rotation-label" },
        "Rotation"
      ),
      React.createElement(
        Slider,
        {
          value: logo.rotation,
          onChange: (_, value) => onUpdate({ ...logo, rotation: value as number }),
          min: -Math.PI,
          max: Math.PI,
          step: 0.1,
          key: "rotation-slider"
        }
      ),
      React.createElement(
        Typography,
        { variant: "caption", key: "opacity-label" },
        "Opacity"
      ),
      React.createElement(
        Slider,
        {
          value: logo.opacity,
          onChange: (_, value) => onUpdate({ ...logo, opacity: value as number }),
          min: 0,
          max: 1,
          step: 0.1,
          key: "opacity-slider"
        }
      ),
      React.createElement(
        Typography,
        { variant: "caption", key: "blend-mode-label" },
        "Blend Mode"
      ),
      React.createElement(
        Select,
        {
          value: logo.blendMode,
          onChange: (e) => onUpdate({ ...logo, blendMode: e.target.value as LogoTexture['blendMode'] }),
          fullWidth: true,
          size: "small",
          key: "blend-mode-select"
        },
        React.createElement(MenuItem, { value: "normal" }, "Normal"),
        React.createElement(MenuItem, { value: "multiply" }, "Multiply"),
        React.createElement(MenuItem, { value: "add" }, "Add"),
        React.createElement(MenuItem, { value: "subtract" }, "Subtract")
      )
    ]
  );
}

function UVMappingControls({ 
  settings, 
  onUpdate 
}: { 
  settings: UVSettings; 
  onUpdate: (settings: UVSettings) => void; 
}) {
  return React.createElement(
    Box,
    { sx: { mb: 3 } },
    [
      React.createElement(Typography, { variant: "subtitle2", gutterBottom: true, key: "uv-mapping-title" }, "UV Mapping"),
      React.createElement(
        Typography,
        { variant: "caption", key: "tiling-label" },
        "Tiling"
      ),
      React.createElement(
        Grid,
        { container: true, spacing: 1, key: "tiling-controls" },
        [
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "tiling-x" },
            React.createElement(Slider, {
              value: settings.tiling.x,
              onChange: (_, value) => onUpdate({ 
                ...settings, 
                tiling: { ...settings.tiling, x: value as number } 
              }),
              min: 0.1,
              max: 10,
              step: 0.1,
              key: "tiling-x-slider"
            })
          ),
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "tiling-y" },
            React.createElement(Slider, {
              value: settings.tiling.y,
              onChange: (_, value) => onUpdate({ 
                ...settings, 
                tiling: { ...settings.tiling, y: value as number } 
              }),
              min: 0.1,
              max: 10,
              step: 0.1,
              key: "tiling-y-slider"
            })
          )
        ]
      ),
      React.createElement(
        Typography,
        { variant: "caption", key: "offset-label" },
        "Offset"
      ),
      React.createElement(
        Grid,
        { container: true, spacing: 1, key: "offset-controls" },
        [
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "offset-x" },
            React.createElement(Slider, {
              value: settings.offset.x,
              onChange: (_, value) => onUpdate({ 
                ...settings, 
                offset: { ...settings.offset, x: value as number } 
              }),
              min: -1,
              max: 1,
              step: 0.1,
              key: "offset-x-slider"
            })
          ),
          React.createElement(
            Grid,
            { item: true, xs: 6, key: "offset-y" },
            React.createElement(Slider, {
              value: settings.offset.y,
              onChange: (_, value) => onUpdate({ 
                ...settings, 
                offset: { ...settings.offset, y: value as number } 
              }),
              min: -1,
              max: 1,
              step: 0.1,
              key: "offset-y-slider"
            })
          )
        ]
      )
    ]
  );
}

function Model({ 
  url, 
  onEdit, 
  selectedMesh,
  logos,
  uvSettings,
  onSceneReady,
}: { 
  url: string; 
  onEdit?: (mesh: Mesh) => void;
  selectedMesh: Mesh | null;
  logos: LogoTexture[];
  uvSettings: UVSettings;
  onSceneReady?: (scene: ThreeGroup) => void;
}) {
  const { scene } = useGLTF(url);
  const modelRef = useRef<Object3D>(null);
  const clonedSceneRef = useRef(scene.clone());

  // Notify parent when scene is ready
  useEffect(() => {
    if (clonedSceneRef.current && onSceneReady) {
      onSceneReady(clonedSceneRef.current);
    }
  }, [onSceneReady]);

  // Center the logo on the mesh
  const centerLogoOnMesh = useCallback((mesh: Mesh, texture: THREE.Texture) => {
    if (mesh.geometry.boundingBox === null) {
      mesh.geometry.computeBoundingBox();
    }

    const boundingBox = mesh.geometry.boundingBox;
    if (boundingBox) {
      // Get the center of the bounding box
      const center = boundingBox.getCenter(new Vector3());
      
      // Convert to UV coordinates (0-1 range)
      const uvCenter = {
        x: (center.x - boundingBox.min.x) / (boundingBox.max.x - boundingBox.min.x),
        y: (center.y - boundingBox.min.y) / (boundingBox.max.y - boundingBox.min.y)
      };

      // Center the texture
      texture.offset.set(
        0.5 - uvCenter.x,
        0.5 - uvCenter.y
      );
      texture.center.set(0.5, 0.5);
      texture.needsUpdate = true;
    }
  }, []);

  useEffect(() => {
    if (selectedMesh && selectedMesh.material instanceof MeshStandardMaterial) {
      // Create a new material for the selected mesh to avoid affecting other meshes
      const material = selectedMesh.material.clone();
      selectedMesh.material = material;

      // Apply UV settings
      if (material.map) {
        material.map.repeat.set(uvSettings.tiling.x, uvSettings.tiling.y);
        material.map.offset.set(uvSettings.offset.x, uvSettings.offset.y);
        material.map.needsUpdate = true;
      }
      
      // Apply logos
      if (logos.length > 0) {
        const lastLogo = logos[logos.length - 1];
        material.map = lastLogo.texture;
        material.transparent = true;
        material.opacity = lastLogo.opacity;
        material.blending = blendModes[lastLogo.blendMode];
        
        // Center the logo when first applied
        centerLogoOnMesh(selectedMesh, lastLogo.texture);
        
        lastLogo.texture.repeat.set(lastLogo.scale.x, lastLogo.scale.y);
        lastLogo.texture.offset.set(lastLogo.position.x, lastLogo.position.y);
        lastLogo.texture.rotation = lastLogo.rotation;
        lastLogo.texture.needsUpdate = true;
      }

      material.needsUpdate = true;
    }
  }, [selectedMesh, logos, uvSettings, centerLogoOnMesh]);

  // Handle mesh selection
  const handleMeshSelect = useCallback((event: any) => {
    event.stopPropagation();
    if (event.object instanceof Mesh) {
      if (onEdit) onEdit(event.object);
    }
  }, [onEdit]);

  return (
    <object3D ref={modelRef}>
      <primitive object={clonedSceneRef.current} onClick={handleMeshSelect} />
    </object3D>
  );
}

interface ModelEditorProps {
  glbUrl: string;
  onSave?: (modifiedUrl: string) => void;
}

export default function ModelEditor({ glbUrl, onSave }: ModelEditorProps): JSX.Element {
  const boxStyles = {
    mb: 3,
    '& .MuiBox-root': {
      marginBottom: 2
    }
  } as const;

  return React.createElement(
    Box,
    { sx: boxStyles },
    [
      React.createElement(Typography, { variant: "h6", key: "title" }, "Model Editor"),
      React.createElement(
        Box,
        { key: "preview" },
        React.createElement(Typography, { variant: "subtitle1" }, "Preview")
      ),
      React.createElement(
        Box,
        { key: "controls" },
        React.createElement(Typography, { variant: "subtitle1" }, "Controls")
      )
    ]
  );
} 