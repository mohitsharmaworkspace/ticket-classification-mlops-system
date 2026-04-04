/**
 * Advanced Mode Component
 * Mode 3: Upload tickets + custom categories
 */

import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Alert,
  Grid
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { uploadWithCategories } from '../services/api';
import PredictionResults from './PredictionResults';

function AdvancedMode({ setLoading, setError, setSuccess }) {
  const [ticketsFile, setTicketsFile] = useState(null);
  const [categoriesFile, setCategoriesFile] = useState(null);
  const [predictions, setPredictions] = useState(null);

  const handleTicketsFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.csv')) {
      setTicketsFile(file);
      setPredictions(null);
    } else {
      setError('Please select a CSV file');
    }
  };

  const handleCategoriesFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.csv')) {
      setCategoriesFile(file);
      setPredictions(null);
    } else {
      setError('Please select a CSV file');
    }
  };

  const handleUpload = async () => {
    if (!ticketsFile || !categoriesFile) {
      setError('Please select both files');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await uploadWithCategories(ticketsFile, categoriesFile);
      setPredictions(result);
      setSuccess(`Successfully processed ${result.total_processed} tickets with ${result.num_categories} custom categories!`);
    } catch (err) {
      setError(err.detail || 'Failed to process files');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setTicketsFile(null);
    setCategoriesFile(null);
    setPredictions(null);
    setError(null);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Advanced Mode - Custom Categories
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Upload tickets and define your own custom categories
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2" gutterBottom>
          <strong>Tickets CSV:</strong> Must contain 'ticket_text' or 'Ticket Description' column
        </Typography>
        <Typography variant="body2">
          <strong>Categories CSV:</strong> Must contain 'category_name' and 'category_description' columns
        </Typography>
      </Alert>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Tickets File Upload */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              border: '2px dashed',
              borderColor: ticketsFile ? 'primary.main' : 'grey.300',
              backgroundColor: ticketsFile ? 'action.hover' : 'background.paper',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
            onClick={() => document.getElementById('tickets-upload').click()}
          >
            <input
              id="tickets-upload"
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={handleTicketsFileChange}
            />
            <CloudUploadIcon sx={{ fontSize: 50, color: 'primary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Tickets CSV
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {ticketsFile ? ticketsFile.name : 'Click to select'}
            </Typography>
          </Paper>
        </Grid>

        {/* Categories File Upload */}
        <Grid item xs={12} md={6}>
          <Paper
            sx={{
              p: 3,
              border: '2px dashed',
              borderColor: categoriesFile ? 'secondary.main' : 'grey.300',
              backgroundColor: categoriesFile ? 'action.hover' : 'background.paper',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.3s'
            }}
            onClick={() => document.getElementById('categories-upload').click()}
          >
            <input
              id="categories-upload"
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={handleCategoriesFileChange}
            />
            <CloudUploadIcon sx={{ fontSize: 50, color: 'secondary.main', mb: 1 }} />
            <Typography variant="h6" gutterBottom>
              Categories CSV
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {categoriesFile ? categoriesFile.name : 'Click to select'}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="contained"
          size="large"
          onClick={handleUpload}
          disabled={!ticketsFile || !categoriesFile}
        >
          Process with Custom Categories
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={handleReset}
          disabled={!ticketsFile && !categoriesFile && !predictions}
        >
          Reset
        </Button>
      </Box>

      {predictions && (
        <Box>
          <Alert severity="success" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Custom Categories Used:</strong> {predictions.category_names.join(', ')}
            </Typography>
          </Alert>
          <PredictionResults
            predictions={predictions.predictions}
            mode="advanced"
            stats={{
              total: predictions.total_processed,
              lowConfidence: predictions.low_confidence_count,
              processingTime: predictions.processing_time_ms,
              numCategories: predictions.num_categories
            }}
          />
        </Box>
      )}
    </Box>
  );
}

export default AdvancedMode;

// Made with Bob
