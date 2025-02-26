'use client';

import { useState, ChangeEvent, useEffect } from 'react';
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
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  DialogContentText 
} from '@mui/material';
import Image from 'next/image';
import ModelViewer from './ModelViewer';
import ModelEditor from './ModelEditor';

interface ModelUrls {
  glb: string;
  fbx: string;
  usdz: string;
  thumbnail: string;
}

interface ConversionStatus {
  stage: 'idle' | 'uploading' | 'converting' | 'processing' | 'complete' | 'error';
  progress: number;
  message: string;
}

// Add new interface for outfit types
interface OutfitType {
  isOutfit: boolean;
  type: 'clothes' | 'hats' | 'shoes' | null;
}

export default function ImageUploader() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [imageValidation, setImageValidation] = useState<{
    isValid: boolean;
    message: string | null;
  }>({
    isValid: false,
    message: null
  });
  const [isLoading, setIsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelUrls, setModelUrls] = useState<ModelUrls | null>(null);
  const [status, setStatus] = useState<ConversionStatus>({
    stage: 'idle',
    progress: 0,
    message: 'Ready to convert'
  });
  const [isEditing, setIsEditing] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  // Add new state for outfit type
  const [outfitType, setOutfitType] = useState<OutfitType>({
    isOutfit: false,
    type: null
  });
  const [processingStatus, setProcessingStatus] = useState<string>('');
  // Add new state for dialog
  const [showDownloadReminder, setShowDownloadReminder] = useState(false);

  const handleFileSelect = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setImageValidation({ isValid: false, message: null });
    setIsValidating(true);
    setError(null);

    // Create form data for validation
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/validate-image', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      setImageValidation({
        isValid: result.success,
        message: result.message
      });

      if (!result.success) {
        setError(result.message || 'Image validation failed');
      }
    } catch (error) {
      setImageValidation({
        isValid: false,
        message: 'Error validating image'
      });
      setError('Error validating image');
      console.error('Validation error:', error);
    } finally {
      setIsValidating(false);
    }
  };

  const handleFileNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFileName(event.target.value);
    setError(null);
  };

  const isValidModelUrls = (data: any): data is ModelUrls => {
    return data && 
      typeof data.glb === 'string' && 
      typeof data.fbx === 'string' && 
      typeof data.usdz === 'string' && 
      typeof data.thumbnail === 'string';
  };

  const handleConvert = async () => {
    if (!selectedFile || !fileName) return;

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
      formData.append('file', selectedFile);
      formData.append('fileName', fileName);
      formData.append('isOutfit', outfitType.isOutfit.toString());
      if (outfitType.isOutfit && outfitType.type) {
        formData.append('outfitType', outfitType.type);
      }

      const response = await fetch('/api/convert', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log('Conversion response:', data);

      if (!data.success) {
        throw new Error(data.error || data.message || 'Conversion failed');
      }

      // If this is an outfit, show processing status
      if (outfitType.isOutfit) {
        setStatus({
          stage: 'processing',
          progress: 75,
          message: 'Processing for Roblox...'
        });
        setProcessingStatus('Adjusting 3D model for Roblox...');
      }

      // Verify files are accessible
      const fileUrls = data.outputs;
      for (const url of Object.values(fileUrls)) {
        const testResponse = await fetch(url as string);
        if (!testResponse.ok) {
          throw new Error(`Failed to access file: ${url}`);
        }
      }

      setStatus({
        stage: 'complete',
        progress: 100,
        message: data.message || 'Conversion complete!'
      });
      setModelUrls(data.outputs);
      setProcessingStatus('');
    } catch (err) {
      console.error('Conversion error:', err);
      setError(err instanceof Error ? err.message : 'An error occurred');
      setStatus({
        stage: 'error',
        progress: 0,
        message: err instanceof Error ? err.message : 'Conversion failed'
      });
    } finally {
      setLoading(false);
    }
  };

  // Add effect to handle preview when modelUrls changes
  useEffect(() => {
    if (modelUrls?.glb) {
      // Verify the GLB file is accessible
      fetch(modelUrls.glb)
        .then(response => {
          if (response.ok) {
            setPreviewUrl(modelUrls.glb);
          } else {
            console.error('Failed to load GLB file');
            setError('Failed to load 3D preview');
          }
        })
        .catch(err => {
          console.error('Error loading GLB file:', err);
          setError('Failed to load 3D preview');
        });
    }
  }, [modelUrls]);

  // Add validation for enabling Convert button
  const isConvertEnabled = () => {
    if (!selectedFile || !fileName || !imageValidation.isValid) return false;
    if (outfitType.isOutfit && !outfitType.type) return false;
    return true;
  };

  // Add reset function
  const resetConverter = () => {
    setSelectedFile(null);
    setFileName('');
    setImageValidation({ isValid: false, message: null });
    setError(null);
    setModelUrls(null);
    setStatus({
      stage: 'idle',
      progress: 0,
      message: 'Ready to convert'
    });
    setOutfitType({ isOutfit: false, type: null });
    setProcessingStatus('');
  };

  // Add handler for starting new conversion
  const handleNewConversion = () => {
    if (modelUrls) {
      setShowDownloadReminder(true);
    } else {
      resetConverter();
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

              {/* File Selection */}
              <Box sx={{ mb: 3 }}>
                <Button
                  variant="contained"
                  component="label"
                  fullWidth
                  disabled={loading}
                >
                  Select Image
                  <input
                    type="file"
                    hidden
                    accept="image/*"
                    onChange={handleFileSelect}
                  />
                </Button>
                {selectedFile && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">
                      Selected: {selectedFile.name}
                    </Typography>
                    {isValidating ? (
                      <Typography variant="body2" color="primary">
                        Validating image...
                      </Typography>
                    ) : imageValidation.message && (
                      <Typography 
                        variant="body2" 
                        color={imageValidation.isValid ? "success.main" : "error"}
                      >
                        {imageValidation.message}
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>

              {/* Output Filename */}
              <Box sx={{ mb: 3 }}>
                <TextField
                  fullWidth
                  label="Output Filename"
                  value={fileName}
                  onChange={handleFileNameChange}
                  disabled={loading}
                  error={!!error}
                  helperText={error || "Enter name for output files"}
                />
              </Box>

              {/* Image Type Selection */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Image Type
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Button
                    variant={outfitType.isOutfit ? "contained" : "outlined"}
                    onClick={() => setOutfitType({ isOutfit: true, type: null })}
                    sx={{ mr: 1 }}
                    disabled={loading}
                  >
                    Outfit
                  </Button>
                  <Button
                    variant={!outfitType.isOutfit ? "contained" : "outlined"}
                    onClick={() => setOutfitType({ isOutfit: false, type: null })}
                    disabled={loading}
                  >
                    Other
                  </Button>
                </Box>

                {outfitType.isOutfit && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Outfit Type
                    </Typography>
                    <Grid container spacing={1}>
                      {['clothes', 'hats', 'shoes'].map((type) => (
                        <Grid item xs={4} key={type}>
                          <Button
                            fullWidth
                            variant={outfitType.type === type ? "contained" : "outlined"}
                            onClick={() => setOutfitType({ ...outfitType, type: type as OutfitType['type'] })}
                            disabled={loading}
                          >
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                          </Button>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}
              </Box>

              {/* Convert Button */}
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleConvert}
                disabled={!isConvertEnabled() || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Convert to 3D'}
              </Button>

              {/* Status and Progress */}
              {status.stage !== 'idle' && (
                <Box sx={{ mt: 3 }}>
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
                  {processingStatus && (
                    <Typography 
                      variant="body2" 
                      color="primary" 
                      sx={{ mt: 1 }}
                    >
                      {processingStatus}
                    </Typography>
                  )}
                </Box>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            {modelUrls ? (
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Results
                </Typography>

                {/* Add New Conversion Button at the top */}
                <Box sx={{ mb: 3 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNewConversion}
                    fullWidth
                  >
                    Convert New Image
                  </Button>
                </Box>

                <Box sx={{ mb: 4 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    3D Preview
                  </Typography>
                  <ModelViewer 
                    glbUrl={modelUrls.glb}
                    fbxUrl={modelUrls.fbx}
                    isOutfit={outfitType.isOutfit}
                    outfitType={outfitType.type || undefined}
                  />
                </Box>

                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Download Files
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(modelUrls).map(([format, url]) => (
                      <Grid item xs={6} sm={3} key={format}>
                        <Button
                          variant="outlined"
                          fullWidth
                          href={url}
                          download
                        >
                          Download {format.toUpperCase()}
                        </Button>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </Paper>
            ) : (
              <Paper 
                elevation={2} 
                sx={{ 
                  p: 2, 
                  height: '400px', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center' 
                }}
              >
                <Typography variant="body1" color="textSecondary">
                  3D preview will appear here
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Paper>

      {/* Add Download Reminder Dialog */}
      <Dialog
        open={showDownloadReminder}
        onClose={() => setShowDownloadReminder(false)}
      >
        <DialogTitle>
          Download Your Files
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Please make sure to download all your converted files before starting a new conversion.
            The current files will be removed when you start a new conversion.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setShowDownloadReminder(false)}
            color="primary"
          >
            Go Back
          </Button>
          <Button
            onClick={() => {
              setShowDownloadReminder(false);
              resetConverter();
            }}
            color="primary"
            variant="contained"
          >
            Continue Anyway
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
} 