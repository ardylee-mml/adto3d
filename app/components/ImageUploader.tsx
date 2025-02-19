'use client';

import { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  CircularProgress, 
  Typography, 
  Grid, 
  Paper, 
  Stepper,
  Step,
  StepLabel,
  Alert,
  LinearProgress
} from '@mui/material';
import Image from 'next/image';
import ModelViewer from './ModelViewer';
import ModelEditor from './ModelEditor';

interface ModelUrls {
  glb?: string;
  fbx?: string;
  usdz?: string;
  thumbnail?: string;
}

interface ConversionStatus {
  stage: 'idle' | 'uploading' | 'processing' | 'complete' | 'error';
  progress: number;
  message: string;
}

export default function ImageUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelUrls, setModelUrls] = useState<ModelUrls | null>(null);
  const [status, setStatus] = useState<ConversionStatus>({
    stage: 'idle',
    progress: 0,
    message: 'Ready to convert'
  });
  const [isEditing, setIsEditing] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
    }
  };

  const handleFileNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFileName(event.target.value);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }
    if (!fileName) {
      setError('Please enter a file name');
      return;
    }

    setLoading(true);
    setError(null);
    setModelUrls(null);
    setStatus({
      stage: 'uploading',
      progress: 0,
      message: 'Uploading image...'
    });

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('fileName', fileName);

      const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log('Response data:', data);

      if (!response.ok) {
        throw new Error(data.error || 'Conversion failed');
      }

      if (data.success && data.outputs) {
        setStatus({
          stage: 'complete',
          progress: 100,
          message: 'Conversion complete!'
        });
        setModelUrls(data.outputs);
      } else {
        console.log('Invalid data format:', data);
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setStatus({
        stage: 'error',
        progress: 0,
        message: 'Conversion failed'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom align="center">
          2D to 3D Converter
        </Typography>

        <Stepper activeStep={
          status.stage === 'idle' ? 0 :
          status.stage === 'uploading' ? 1 :
          status.stage === 'processing' ? 2 :
          status.stage === 'complete' ? 3 : 0
        } sx={{ mb: 4 }}>
          <Step>
            <StepLabel>Select Image</StepLabel>
          </Step>
          <Step>
            <StepLabel>Upload</StepLabel>
          </Step>
          <Step>
            <StepLabel>Convert</StepLabel>
          </Step>
          <Step>
            <StepLabel>Complete</StepLabel>
          </Step>
        </Stepper>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Input
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Button
                  variant="contained"
                  component="label"
                  fullWidth
                  sx={{ mb: 2 }}
                >
                  Select Image
                  <input
                    type="file"
                    hidden
                    accept="image/*"
                    onChange={handleFileChange}
                  />
                </Button>
                {file && (
                  <Alert severity="success" sx={{ mb: 2 }}>
                    Selected: {file.name}
                  </Alert>
                )}
              </Box>

              <TextField
                fullWidth
                label="Output File Name"
                value={fileName}
                onChange={handleFileNameChange}
                sx={{ mb: 3 }}
                helperText="This name will be used for the converted files"
              />

              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={loading || !file || !fileName}
                fullWidth
                sx={{ mb: 3 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Convert to 3D'}
              </Button>

              {status.stage !== 'idle' && (
                <Box sx={{ mb: 3 }}>
                  <LinearProgress 
                    variant="determinate" 
                    value={status.progress} 
                    sx={{ mb: 1 }}
                  />
                  <Typography 
                    variant="body2" 
                    color={status.stage === 'error' ? 'error' : 'textSecondary'}
                  >
                    {status.message}
                  </Typography>
                </Box>
              )}

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            {modelUrls ? (
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Results
                </Typography>

                <Box sx={{ mb: 4 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="subtitle1">
                      3D Preview
                    </Typography>
                    <Button 
                      variant="outlined"
                      onClick={() => setIsEditing(!isEditing)}
                    >
                      {isEditing ? 'Exit Editor' : 'Edit Model'}
                    </Button>
                  </Box>
                  {isEditing ? (
                    <ModelEditor glbUrl={modelUrls.glb} />
                  ) : (
                    <ModelViewer glbUrl={modelUrls.glb} />
                  )}
                </Box>

                <Box sx={{ mb: 4 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Thumbnail
                  </Typography>
                  <Image
                    src={modelUrls.thumbnail}
                    alt="3D Model Preview"
                    width={400}
                    height={400}
                    style={{ objectFit: 'contain' }}
                  />
                </Box>

                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Download Files
                  </Typography>
                  <Grid container spacing={2}>
                    {modelUrls.glb && (
                      <Grid item xs={12} sm={4}>
                        <Button 
                          href={modelUrls.glb} 
                          target="_blank" 
                          variant="contained"
                          fullWidth
                          sx={{
                            background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                            color: 'white',
                            boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                            '&:hover': {
                              background: 'linear-gradient(45deg, #1976D2 30%, #00BCD4 90%)',
                            }
                          }}
                          download={`${fileName}.glb`}
                        >
                          Download GLB
                        </Button>
                      </Grid>
                    )}
                    {modelUrls.fbx && (
                      <Grid item xs={12} sm={4}>
                        <Button 
                          href={modelUrls.fbx} 
                          target="_blank" 
                          variant="contained"
                          fullWidth
                          sx={{
                            background: 'linear-gradient(45deg, #4CAF50 30%, #8BC34A 90%)',
                            color: 'white',
                            boxShadow: '0 3px 5px 2px rgba(139, 195, 74, .3)',
                            '&:hover': {
                              background: 'linear-gradient(45deg, #388E3C 30%, #689F38 90%)',
                            }
                          }}
                          download={`${fileName}.fbx`}
                        >
                          Download FBX
                        </Button>
                      </Grid>
                    )}
                    {modelUrls.usdz && (
                      <Grid item xs={12} sm={4}>
                        <Button 
                          href={modelUrls.usdz} 
                          target="_blank" 
                          variant="contained"
                          fullWidth
                          sx={{
                            background: 'linear-gradient(45deg, #FF9800 30%, #FFC107 90%)',
                            color: 'white',
                            boxShadow: '0 3px 5px 2px rgba(255, 193, 7, .3)',
                            '&:hover': {
                              background: 'linear-gradient(45deg, #F57C00 30%, #FFB300 90%)',
                            }
                          }}
                          download={`${fileName}.usdz`}
                        >
                          Download USDZ
                        </Button>
                      </Grid>
                    )}
                  </Grid>
                </Box>
              </Paper>
            ) : (
              <Paper 
                elevation={2} 
                sx={{ 
                  p: 2, 
                  height: '100%', 
                  display: 'flex', 
                  alignItems: 'center',
                  justifyContent: 'center',
                  bgcolor: 'grey.100'
                }}
              >
                <Typography variant="h6" color="text.secondary">
                  Convert an image to see the 3D preview here
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
} 