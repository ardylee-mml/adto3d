'use client';

import React, { useState, ChangeEvent, useEffect } from 'react';
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

// Define explicit types for all state
interface OutfitType {
  isOutfit: boolean;
  type: 'clothes' | 'hats' | 'shoes' | null;
}

interface ConversionStatus {
  stage: 'idle' | 'uploading' | 'converting' | 'processing' | 'complete' | 'error';
  progress: number;
  message: string;
}

interface ImageValidation {
  isValid: boolean;
  message: string | null;
}

interface ModelUrls {
  glb: string;
  fbx: string;
  usdz: string;
  thumbnail: string;
  [key: string]: string;
}

// Break down into smaller components
const DownloadReminderDialog = ({ 
  open, 
  onClose, 
  onContinue 
}: { 
  open: boolean; 
  onClose: () => void; 
  onContinue: () => void; 
}) => (
  <Dialog open={open} onClose={onClose}>
    <DialogTitle>Download Your Files</DialogTitle>
    <DialogContent>
      <DialogContentText>
        Please make sure to download all your converted files before starting a new conversion.
        The current files will be removed when you start a new conversion.
      </DialogContentText>
    </DialogContent>
    <DialogActions>
      <Button onClick={onClose} color="primary">Go Back</Button>
      <Button onClick={onContinue} color="primary" variant="contained">
        Continue Anyway
      </Button>
    </DialogActions>
  </Dialog>
);

// Smaller components
const FileInput: React.FC<{
  loading: boolean;
  onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void;
}> = ({ loading, onFileSelect }) => {
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  
  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };
  
  return (
    <div>
      <input
        ref={fileInputRef}
        type="file"
        style={{ display: 'none' }}
        accept="image/*"
        onChange={onFileSelect}
        disabled={loading}
      />
      <Button
        variant="contained"
        fullWidth
        disabled={loading}
        onClick={handleButtonClick}
      >
        Select Image
      </Button>
    </div>
  );
};

const FileInfo: React.FC<{
  fileName: string;
  isValidating: boolean;
  validation: ImageValidation;
}> = ({ fileName, isValidating, validation }) => (
  <div style={{ marginTop: '8px', marginBottom: '24px' }}>
    <Typography variant="body2">
      Selected: {fileName}
    </Typography>
    {isValidating ? (
      <Typography variant="body2" color="primary">
        Validating image...
      </Typography>
    ) : validation.message && (
      <Typography 
        variant="body2"
        color={validation.isValid ? "success.main" : "error"}
      >
        {validation.message}
      </Typography>
    )}
  </div>
);

// Break down OutfitTypeSelector into smaller components
const OutfitButton: React.FC<{
  selected: boolean;
  onClick: () => void;
  disabled: boolean;
  label: string;
  sx?: Record<string, unknown>;
}> = ({ selected, onClick, disabled, label, sx }) => (
  <Button
    variant={selected ? "contained" : "outlined"}
    onClick={onClick}
    disabled={disabled}
    sx={sx}
  >
    {label}
  </Button>
);

const OutfitTypeButton: React.FC<{
  type: string;
  selected: boolean;
  onClick: () => void;
  disabled: boolean;
}> = ({ type, selected, onClick, disabled }) => (
  <Grid item xs={4}>
    <Button
      fullWidth
      variant={selected ? "contained" : "outlined"}
      onClick={onClick}
      disabled={disabled}
    >
      {type.charAt(0).toUpperCase() + type.slice(1)}
    </Button>
  </Grid>
);

const OutfitTypeSelector: React.FC<{
  outfitType: OutfitType;
  loading: boolean;
  onChange: (newType: OutfitType) => void;
}> = ({ outfitType, loading, onChange }) => (
  <div style={{ marginBottom: '24px' }}>
    <Typography variant="subtitle1" gutterBottom>
      Image Type
    </Typography>
    <div style={{ marginBottom: '16px' }}>
      <OutfitButton
        selected={outfitType.isOutfit}
        onClick={() => onChange({ isOutfit: true, type: null })}
        disabled={loading}
        label="Outfit"
        sx={{ mr: 1 }}
      />
      <OutfitButton
        selected={!outfitType.isOutfit}
        onClick={() => onChange({ isOutfit: false, type: null })}
        disabled={loading}
        label="Other"
      />
    </div>
    {outfitType.isOutfit && (
      <div style={{ marginBottom: '16px' }}>
        <Typography variant="subtitle2" gutterBottom>
          Outfit Type
        </Typography>
        <Grid container spacing={1}>
          {(['clothes', 'hats', 'shoes'] as const).map((type) => (
            <OutfitTypeButton
              key={type}
              type={type}
              selected={outfitType.type === type}
              onClick={() => onChange({
                ...outfitType,
                type
              })}
              disabled={loading}
            />
          ))}
        </Grid>
      </div>
    )}
  </div>
);

const DownloadButton: React.FC<{
  format: string;
  url: string;
}> = ({ format, url }) => (
  <Grid item xs={6} sm={3}>
    <a
      style={{
        textDecoration: 'none',
        width: '100%',
        display: 'block'
      }}
      href={url}
      download
    >
      <Button variant="outlined" fullWidth>
        Download {format.toUpperCase()}
      </Button>
    </a>
  </Grid>
);

const ConversionProgress: React.FC<{
  status: ConversionStatus;
  processingStatus?: string;
}> = ({ status, processingStatus }) => (
  <>
    <LinearProgress
      variant="determinate"
      value={status.progress}
      sx={{ mb: 1, mt: 3 }}
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
  </>
);

// Main component
export default function ImageUploader(): JSX.Element {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [modelUrls, setModelUrls] = useState<ModelUrls | null>(null);
  const [status, setStatus] = useState<ConversionStatus>({
    stage: 'idle',
    progress: 0,
    message: 'Ready to convert'
  });
  const [outfitType, setOutfitType] = useState<OutfitType>({
    isOutfit: false,
    type: null
  });
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [isValidating, setIsValidating] = useState<boolean>(false);
  const [imageValidation, setImageValidation] = useState<ImageValidation>({
    isValid: false,
    message: null
  });
  const [showDownloadReminder, setShowDownloadReminder] = useState<boolean>(false);

  // Handle file selection
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

  // Check if convert button should be enabled
  const isConvertEnabled = (): boolean => {
    // Check if a valid file is selected
    if (!selectedFile || !imageValidation.isValid) return false;
    
    // Check if outfit type is selected when in outfit mode
    if (outfitType.isOutfit && !outfitType.type) return false;
    
    return true;
  };

  // Handle conversion
  const handleConvert = async () => {
    if (!isConvertEnabled() || !selectedFile) return;

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

  // Reset converter
  const resetConverter = () => {
    setSelectedFile(null);
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

  // Handle new conversion
  const handleNewConversion = () => {
    if (modelUrls) {
      setShowDownloadReminder(true);
    } else {
      resetConverter();
    }
  };

  const renderContent = (): JSX.Element => (
    <Box component="div" sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom align="center">
          2D to 3D Converter
        </Typography>

        <Stepper 
          activeStep={
            status.stage === 'idle' ? 0 :
            status.stage === 'uploading' ? 1 :
            status.stage === 'processing' ? 2 :
            status.stage === 'complete' ? 3 : 0
          } 
          sx={{ mb: 4 }}
        >
          <Step><StepLabel>Select Image</StepLabel></Step>
          <Step><StepLabel>Upload</StepLabel></Step>
          <Step><StepLabel>Convert</StepLabel></Step>
          <Step><StepLabel>Complete</StepLabel></Step>
        </Stepper>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Input
              </Typography>

              <div style={{ marginBottom: '24px' }}>
                <FileInput loading={loading} onFileSelect={handleFileSelect} />
                {selectedFile && (
                  <FileInfo 
                    fileName={selectedFile.name}
                    isValidating={isValidating}
                    validation={imageValidation}
                  />
                )}
              </div>

              <div style={{ marginBottom: '24px' }}>
                <OutfitTypeSelector
                  outfitType={outfitType}
                  loading={loading}
                  onChange={setOutfitType}
                />
              </div>

              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={handleConvert}
                disabled={!isConvertEnabled() || loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Convert to 3D'}
              </Button>

              {status.stage !== 'idle' && (
                <ConversionProgress
                  status={status}
                  processingStatus={processingStatus}
                />
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            {modelUrls ? (
              <Paper component="div" elevation={2} sx={{ p: 2 }}>
                <Typography component="h2" variant="h6" gutterBottom>
                  Results
                </Typography>

                <Box component="div" sx={{ mb: 3 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleNewConversion}
                    fullWidth
                  >
                    Convert New Image
                  </Button>
                </Box>

                <Box component="div" sx={{ mb: 4 }}>
                  <Typography component="h3" variant="subtitle1" gutterBottom>
                    3D Preview
                  </Typography>
                  <ModelViewer 
                    glbUrl={modelUrls.glb}
                    fbxUrl={modelUrls.fbx}
                    isOutfit={outfitType.isOutfit}
                    outfitType={outfitType.type || undefined}
                  />
                </Box>

                <Box component="div">
                  <Typography component="h3" variant="subtitle1" gutterBottom>
                    Download Files
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(modelUrls).map(([format, url]) => (
                      <Grid item xs={6} sm={3} key={format}>
                        <a
                          style={{
                            textDecoration: 'none',
                            width: '100%',
                            display: 'block'
                          }}
                          href={url}
                          download
                        >
                          <Button variant="outlined" fullWidth>
                            Download {format.toUpperCase()}
                          </Button>
                        </a>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              </Paper>
            ) : (
              <Paper 
                component="div"
                elevation={2} 
                sx={{ 
                  p: 2, 
                  height: '400px', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center' 
                }}
              >
                <Typography component="p" variant="body1" color="textSecondary">
                  3D preview will appear here
                </Typography>
              </Paper>
            )}
          </Grid>
        </Grid>
      </Paper>

      <DownloadReminderDialog
        open={showDownloadReminder}
        onClose={() => setShowDownloadReminder(false)}
        onContinue={() => {
          setShowDownloadReminder(false);
          resetConverter();
        }}
      />
    </Box>
  );

  return renderContent();
} 