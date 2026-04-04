/**
 * API Service for Ticket Classification
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Predict category for single text
 */
export const predictSingleText = async (text) => {
  try {
    const response = await api.post('/predict-text', { text });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

/**
 * Upload CSV for bulk prediction
 */
export const uploadCSV = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

/**
 * Upload tickets and categories for advanced mode
 */
export const uploadWithCategories = async (ticketsFile, categoriesFile) => {
  try {
    const formData = new FormData();
    formData.append('tickets_file', ticketsFile);
    formData.append('categories_file', categoriesFile);
    
    const response = await api.post('/upload-with-categories', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

/**
 * Submit feedback/correction
 */
export const submitFeedback = async (feedbackData) => {
  try {
    const response = await api.post('/feedback', feedbackData);
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

/**
 * Get health status
 */
export const getHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

/**
 * Get metrics summary
 */
export const getMetrics = async () => {
  try {
    const response = await api.get('/metrics/summary');
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export default api;

// Made with Bob
