/**
 * Single Text Input Component
 * Mode 1: Classify single ticket text
 */

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  Chip,
  Grid
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { predictSingleText, submitFeedback } from '../services/api';
import PredictionResults from './PredictionResults';

function SingleTextInput({ setLoading, setError, setSuccess }) {
  const [text, setText] = useState('');
  const [prediction, setPrediction] = useState(null);

  const handlePredict = async () => {
    if (!text.trim()) {
      setError('Please enter ticket text');
      return;
    }

    if (text.length < 10 || text.length > 1000) {
      setError('Text must be between 10 and 1000 characters');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await predictSingleText(text);
      setPrediction({
        ...result,
        original_text: text
      });
      setSuccess('Prediction completed successfully!');
    } catch (err) {
      setError(err.detail || 'Failed to get prediction');
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (correctedCategory) => {
    setLoading(true);
    try {
      await submitFeedback({
        original_text: prediction.original_text,
        predicted_category: prediction.predicted_category,
        corrected_category: correctedCategory,
        confidence_score: prediction.confidence_score
      });
      setSuccess('Feedback submitted successfully!');
      setPrediction(null);
      setText('');
    } catch (err) {
      setError('Failed to submit feedback');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Single Ticket Classification
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Enter a ticket description to classify it into a category
      </Typography>

      <TextField
        fullWidth
        multiline
        rows={6}
        variant="outlined"
        label="Ticket Description"
        placeholder="Enter your ticket text here (10-1000 characters)..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        sx={{ mb: 2 }}
        helperText={`${text.length}/1000 characters`}
      />

      <Button
        variant="contained"
        size="large"
        endIcon={<SendIcon />}
        onClick={handlePredict}
        disabled={!text.trim()}
        sx={{ mb: 3 }}
      >
        Classify Ticket
      </Button>

      {prediction && (
        <PredictionResults
          predictions={[prediction]}
          mode="single"
          onFeedback={handleFeedback}
        />
      )}
    </Box>
  );
}

export default SingleTextInput;

// Made with Bob
