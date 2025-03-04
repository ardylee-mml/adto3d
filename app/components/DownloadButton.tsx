import React from 'react';
import { Button } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import axios from 'axios';

interface DownloadButtonProps {
  fileUrl: string;
  fileName: string;
  label: string;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({ fileUrl, fileName, label }) => {
  const handleDownload = async () => {
    try {
      // Use axios to get the file with responseType blob
      const response = await axios.get(fileUrl, {
        responseType: 'blob',
        headers: {
          'Content-Type': 'application/octet-stream',
        }
      });
      
      // Create a blob URL from the response data
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      
      // Create a temporary anchor element
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      
      // Append to the document, click it, and remove it
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(link);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download the file. Please try again.');
    }
  };

  return (
    <Button 
      variant="contained" 
      color="primary" 
      startIcon={<DownloadIcon />}
      onClick={handleDownload}
    >
      {label}
    </Button>
  );
};

export default DownloadButton; 