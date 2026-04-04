/**
 * Bulk CSV Upload Component
 * Mode 2: Upload CSV file for bulk classification
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadCSV } from '../services/api';
import PredictionResults from './PredictionResults';

function BulkCSVUpload({ setLoading, setError, setSuccess }) {
  const [file, setFile] = useState(null);
  const [predictions, setPredictions] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.csv')) {
        setError('Please select a CSV file');
        return;
      }
      setFile(selectedFile);
      setPredictions(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await uploadCSV(file);
      setPredictions(result);
      setSuccess(`Successfully processed ${result.total_processed} tickets!`);
    } catch (err) {
      setError(err.detail || 'Failed to process CSV file');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPredictions(null);
    setError(null);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Bulk CSV Upload
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Upload a CSV file with tickets for bulk classification
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>CSV Format:</strong> Your file should contain a column named 
          'ticket_text' or 'Ticket Description' with the ticket descriptions.
        </Typography>
      </Alert>

      <Paper
        sx={{
          p: 4,
          mb: 3,
          border: '2px dashed',
          borderColor: file ? 'primary.main' : 'grey.300',
          backgroundColor: file ? 'action.hover' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.3s'
        }}
        onClick={() => document.getElementById('csv-upload').click()}
      >
        <input
          id="csv-upload"
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <CloudUploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {file ? file.name : 'Click to select CSV file'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {file ? `Size: ${(file.size / 1024).toFixed(2)} KB` : 'Maximum file size: 10MB'}
        </Typography>
      </Paper>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleUpload}
          disabled={!file}
        >
          Process CSV
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={handleReset}
          disabled={!file && !predictions}
        >
          Reset
        </Button>
      </Box>

      {predictions && (
        <PredictionResults
          predictions={predictions.predictions}
          mode="bulk"
          stats={{
            total: predictions.total_processed,
            lowConfidence: predictions.low_confidence_count,
            processingTime: predictions.processing_time_ms
          }}
        />
      )}
    </Box>
  );
}

export default BulkCSVUpload;

// Made with Bob
