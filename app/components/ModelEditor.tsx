'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { Canvas, useThree, useLoader } from '@react-three/fiber';
import { OrbitControls, TransformControls, useGLTF, Stage, PivotControls } from '@react-three/drei';
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
  Group, 
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
  return (
    <Box sx={{ mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="subtitle2">Logo Settings</Typography>
        <IconButton onClick={onDelete} size="small">
          <DeleteIcon />
        </IconButton>
      </Box>

      <Typography variant="caption">Scale</Typography>
      <Grid container spacing={1}>
        <Grid item xs={6}>
          <Slider
            value={logo.scale.x}
            onChange={(_, value) => onUpdate({ ...logo, scale: { ...logo.scale, x: value as number } })}
            min={0.1}
            max={2}
            step={0.1}
          />
        </Grid>
        <Grid item xs={6}>
          <Slider
            value={logo.scale.y}
            onChange={(_, value) => onUpdate({ ...logo, scale: { ...logo.scale, y: value as number } })}
            min={0.1}
            max={2}
            step={0.1}
          />
        </Grid>
      </Grid>

      <Typography variant="caption">Position</Typography>
      <Grid container spacing={1}>
        <Grid item xs={6}>
          <Slider
            value={logo.position.x}
            onChange={(_, value) => onUpdate({ ...logo, position: { ...logo.position, x: value as number } })}
            min={-1}
            max={1}
            step={0.1}
          />
        </Grid>
        <Grid item xs={6}>
          <Slider
            value={logo.position.y}
            onChange={(_, value) => onUpdate({ ...logo, position: { ...logo.position, y: value as number } })}
            min={-1}
            max={1}
            step={0.1}
          />
        </Grid>
      </Grid>

      <Typography variant="caption">Rotation</Typography>
      <Slider
        value={logo.rotation}
        onChange={(_, value) => onUpdate({ ...logo, rotation: value as number })}
        min={-Math.PI}
        max={Math.PI}
        step={0.1}
      />

      <Typography variant="caption">Opacity</Typography>
      <Slider
        value={logo.opacity}
        onChange={(_, value) => onUpdate({ ...logo, opacity: value as number })}
        min={0}
        max={1}
        step={0.1}
      />

      <Typography variant="caption">Blend Mode</Typography>
      <Select
        value={logo.blendMode}
        onChange={(e) => onUpdate({ ...logo, blendMode: e.target.value as LogoTexture['blendMode'] })}
        fullWidth
        size="small"
      >
        <MenuItem value="normal">Normal</MenuItem>
        <MenuItem value="multiply">Multiply</MenuItem>
        <MenuItem value="add">Add</MenuItem>
        <MenuItem value="subtract">Subtract</MenuItem>
      </Select>
    </Box>
  );
}

function UVMappingControls({ 
  settings, 
  onUpdate 
}: { 
  settings: UVSettings; 
  onUpdate: (settings: UVSettings) => void; 
}) {
  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="subtitle2" gutterBottom>UV Mapping</Typography>
      
      <Typography variant="caption">Tiling</Typography>
      <Grid container spacing={1}>
        <Grid item xs={6}>
          <Slider
            value={settings.tiling.x}
            onChange={(_, value) => onUpdate({ 
              ...settings, 
              tiling: { ...settings.tiling, x: value as number } 
            })}
            min={0.1}
            max={10}
            step={0.1}
          />
        </Grid>
        <Grid item xs={6}>
          <Slider
            value={settings.tiling.y}
            onChange={(_, value) => onUpdate({ 
              ...settings, 
              tiling: { ...settings.tiling, y: value as number } 
            })}
            min={0.1}
            max={10}
            step={0.1}
          />
        </Grid>
      </Grid>

      <Typography variant="caption">Offset</Typography>
      <Grid container spacing={1}>
        <Grid item xs={6}>
          <Slider
            value={settings.offset.x}
            onChange={(_, value) => onUpdate({ 
              ...settings, 
              offset: { ...settings.offset, x: value as number } 
            })}
            min={-1}
            max={1}
            step={0.1}
          />
        </Grid>
        <Grid item xs={6}>
          <Slider
            value={settings.offset.y}
            onChange={(_, value) => onUpdate({ 
              ...settings, 
              offset: { ...settings.offset, y: value as number } 
            })}
            min={-1}
            max={1}
            step={0.1}
          />
        </Grid>
      </Grid>
    </Box>
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
  onSceneReady?: (scene: Group) => void;
}) {
  const { scene } = useGLTF(url);
  const modelRef = useRef<Group>();
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
    <group ref={modelRef}>
      <primitive 
        object={clonedSceneRef.current}
        onClick={handleMeshSelect}
      />
    </group>
  );
}

interface ModelEditorProps {
  glbUrl: string;
  onSave?: (modifiedUrl: string) => void;
}

export default function ModelEditor({ glbUrl, onSave }: ModelEditorProps) {
  const [selectedMesh, setSelectedMesh] = useState<Mesh | null>(null);
  const [transformMode, setTransformMode] = useState<'translate' | 'rotate' | 'scale'>('translate');
  const [logos, setLogos] = useState<LogoTexture[]>([]);
  const [uvSettings, setUVSettings] = useState<UVSettings>({
    tiling: { x: 1, y: 1 },
    offset: { x: 0, y: 0 },
  });
  const [activeTab, setActiveTab] = useState(0);

  // Track if we're in edit mode
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [currentScene, setCurrentScene] = useState<Group | null>(null);

  const handleLogoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files?.[0] || !selectedMesh) return;

    const file = event.target.files[0];
    const imageUrl = URL.createObjectURL(file);
    
    try {
      const texture = await new Promise<THREE.Texture>((resolve, reject) => {
        const loader = new TextureLoader();
        loader.load(
          imageUrl, 
          (texture) => resolve(texture),
          undefined,
          (error) => reject(error)
        );
      });

      texture.needsUpdate = true;

      const newLogo: LogoTexture = {
        id: uuidv4(),
        texture,
        scale: { x: 1, y: 1 },
        position: { x: 0, y: 0 },
        rotation: 0,
        opacity: 1,
        blendMode: 'normal',
      };

      setLogos([...logos, newLogo]);
    } catch (error) {
      console.error('Error loading texture:', error);
    } finally {
      URL.revokeObjectURL(imageUrl);
    }
  };

  const handleMeshSelect = (mesh: Mesh) => {
    setSelectedMesh(mesh);
    setIsEditing(true);
  };

  const handleSave = async () => {
    if (!currentScene) {
      alert('Scene not ready for export');
      return;
    }
    
    setIsSaving(true);
    try {
      const exporter = new GLTFExporter();
      const gltfData = await new Promise((resolve, reject) => {
        exporter.parse(
          currentScene,
          (gltf) => resolve(gltf),
          (error) => reject(error),
          { binary: true }
        );
      });

      // Create blob and form data
      const blob = new Blob([gltfData as ArrayBuffer], { type: 'model/gltf-binary' });
      const formData = new FormData();
      formData.append('model', blob, 'modified_model.glb');

      // Send to server
      const response = await fetch('/api/save-model', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to save model');
      }

      const { url } = await response.json();
      if (onSave) {
        onSave(url);
      }

      // Show success message
      alert('Model saved successfully!');
    } catch (error) {
      console.error('Error saving model:', error);
      alert('Failed to save model: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box sx={{ 
            height: isEditing ? '800px' : '500px',
            bgcolor: '#f5f5f5', 
            borderRadius: '8px',
            transition: 'all 0.3s ease-in-out',
            mb: 2
          }}>
            <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
              <Stage environment="city" intensity={0.5}>
                <Model 
                  url={glbUrl} 
                  onEdit={handleMeshSelect}
                  selectedMesh={selectedMesh}
                  logos={logos}
                  uvSettings={uvSettings}
                  onSceneReady={setCurrentScene}
                />
              </Stage>
              <OrbitControls makeDefault enableDamping={false} />
              {selectedMesh && (
                <TransformControls 
                  object={selectedMesh}
                  mode={transformMode}
                  space="local"
                />
              )}
            </Canvas>
          </Box>

          {selectedMesh && (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: { xs: 'column', sm: 'row' }, 
              gap: 2,
              justifyContent: 'center',
              mb: 2
            }}>
              <Box sx={{ 
                display: 'flex', 
                gap: 1, 
                flexWrap: 'wrap',
                justifyContent: 'center'
              }}>
                <Button
                  variant={transformMode === 'translate' ? 'contained' : 'outlined'}
                  onClick={() => setTransformMode('translate')}
                  sx={{ minWidth: '120px' }}
                >
                  Move
                </Button>
                <Button
                  variant={transformMode === 'rotate' ? 'contained' : 'outlined'}
                  onClick={() => setTransformMode('rotate')}
                  sx={{ minWidth: '120px' }}
                >
                  Rotate
                </Button>
                <Button
                  variant={transformMode === 'scale' ? 'contained' : 'outlined'}
                  onClick={() => setTransformMode('scale')}
                  sx={{ minWidth: '120px' }}
                >
                  Scale
                </Button>
              </Box>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleSave}
                  disabled={isSaving}
                  startIcon={<SaveIcon />}
                  sx={{
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #00BCD4 90%)',
                    }
                  }}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button
                  variant="outlined"
                  color="secondary"
                  onClick={() => {
                    setIsEditing(false);
                    setSelectedMesh(null);
                  }}
                  sx={{
                    borderColor: '#f50057',
                    color: '#f50057',
                    '&:hover': {
                      borderColor: '#c51162',
                      color: '#c51162',
                      backgroundColor: 'rgba(245, 0, 87, 0.04)'
                    }
                  }}
                >
                  Exit Editor
                </Button>
              </Box>
            </Box>
          )}
        </Grid>

        {isEditing && selectedMesh && (
          <Grid item xs={12}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Tabs 
                value={activeTab} 
                onChange={(_, v) => setActiveTab(v)}
                sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
              >
                <Tab label="Logos" />
                <Tab label="UV Mapping" />
              </Tabs>

              {activeTab === 0 && (
                <>
                  <Button
                    variant="outlined"
                    component="label"
                    startIcon={<AddPhotoAlternateIcon />}
                    fullWidth
                    sx={{ my: 2 }}
                  >
                    Add Logo
                    <input
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleLogoUpload}
                    />
                  </Button>

                  {logos.map(logo => (
                    <TextureControls
                      key={logo.id}
                      logo={logo}
                      onUpdate={(updated) => {
                        setLogos(logos.map(l => l.id === updated.id ? updated : l));
                      }}
                      onDelete={() => {
                        setLogos(logos.filter(l => l.id !== logo.id));
                      }}
                    />
                  ))}
                </>
              )}

              {activeTab === 1 && (
                <UVMappingControls
                  settings={uvSettings}
                  onUpdate={setUVSettings}
                />
              )}
            </Paper>
          </Grid>
        )}
      </Grid>
    </Paper>
  );
} 