/**
 * Prediction Results Component
 * Display predictions and allow feedback
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';

function PredictionResults({ predictions, mode, stats, onFeedback }) {
  const [feedbackDialog, setFeedbackDialog] = useState(false);
  const [selectedPrediction, setSelectedPrediction] = useState(null);
  const [correctedCategory, setCorrectedCategory] = useState('');

  const handleOpenFeedback = (prediction) => {
    setSelectedPrediction(prediction);
    setCorrectedCategory('');
    setFeedbackDialog(true);
  };

  const handleSubmitFeedback = () => {
    if (onFeedback && correctedCategory.trim()) {
      onFeedback(correctedCategory.trim());
      setFeedbackDialog(false);
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box>
      {/* Stats Summary */}
      {stats && (
        <Paper sx={{ p: 2, mb: 2, backgroundColor: 'primary.light' }}>
          <Typography variant="h6" gutterBottom>
            Processing Summary
          </Typography>
          <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
            <Typography variant="body1">
              <strong>Total Processed:</strong> {stats.total}
            </Typography>
            <Typography variant="body1">
              <strong>Low Confidence:</strong> {stats.lowConfidence}
            </Typography>
            <Typography variant="body1">
              <strong>Processing Time:</strong> {stats.processingTime.toFixed(2)}ms
            </Typography>
            {stats.numCategories && (
              <Typography variant="body1">
                <strong>Categories:</strong> {stats.numCategories}
              </Typography>
            )}
          </Box>
        </Paper>
      )}

      {/* Results Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'grey.100' }}>
              {mode !== 'single' && <TableCell><strong>#</strong></TableCell>}
              <TableCell><strong>Ticket Text</strong></TableCell>
              <TableCell><strong>Predicted Category</strong></TableCell>
              <TableCell><strong>Confidence</strong></TableCell>
              {mode === 'single' && <TableCell><strong>Actions</strong></TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {predictions.map((pred, index) => (
              <TableRow key={index} hover>
                {mode !== 'single' && (
                  <TableCell>{pred.row_index !== undefined ? pred.row_index : index + 1}</TableCell>
                )}
                <TableCell sx={{ maxWidth: 300 }}>
                  <Typography variant="body2" noWrap>
                    {pred.ticket_text || pred.original_text || 'N/A'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={pred.predicted_category}
                    color="primary"
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={`${(pred.confidence_score * 100).toFixed(1)}%`}
                      color={getConfidenceColor(pred.confidence_score)}
                      size="small"
                      icon={
                        pred.confidence_score >= 0.7 ? 
                        <CheckCircleIcon /> : 
                        <WarningIcon />
                      }
                    />
                  </Box>
                </TableCell>
                {mode === 'single' && (
                  <TableCell>
                    <Button
                      size="small"
                      variant="outlined"
                      onClick={() => handleOpenFeedback(pred)}
                    >
                      Provide Feedback
                    </Button>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Feedback Dialog */}
      <Dialog open={feedbackDialog} onClose={() => setFeedbackDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Provide Feedback</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" paragraph>
            If the prediction is incorrect, please provide the correct category:
          </Typography>
          <Typography variant="body2" paragraph>
            <strong>Predicted:</strong> {selectedPrediction?.predicted_category}
          </Typography>
          <TextField
            fullWidth
            label="Correct Category"
            value={correctedCategory}
            onChange={(e) => setCorrectedCategory(e.target.value)}
            placeholder="Enter the correct category"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setFeedbackDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSubmitFeedback}
            variant="contained"
            disabled={!correctedCategory.trim()}
          >
            Submit Feedback
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

export default PredictionResults;

// Made with Bob
