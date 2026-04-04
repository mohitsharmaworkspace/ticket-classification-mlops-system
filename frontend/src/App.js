/**
 * Main App Component
 * Ticket Classification MLOps System
 */

import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Alert,
  CircularProgress
} from '@mui/material';
import SingleTextInput from './components/SingleTextInput';
import BulkCSVUpload from './components/BulkCSVUpload';
import AdvancedMode from './components/AdvancedMode';
import './App.css';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setError(null);
    setSuccess(null);
  };

  return (
    <div className="App">
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          {/* Header */}
          <Paper elevation={3} sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <Typography variant="h3" component="h1" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
              🎫 Ticket Classification System
            </Typography>
            <Typography variant="h6" sx={{ color: 'white', opacity: 0.9 }}>
              MLOps-powered intelligent ticket categorization
            </Typography>
          </Paper>

          {/* Global Alerts */}
          {error && (
            <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}

          {/* Main Content */}
          <Paper elevation={3}>
            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange}
                variant="fullWidth"
                sx={{
                  '& .MuiTab-root': {
                    fontSize: '1rem',
                    fontWeight: 'bold',
                    py: 2
                  }
                }}
              >
                <Tab label="📝 Single Text" />
                <Tab label="📊 Bulk CSV" />
                <Tab label="⚙️ Advanced Mode" />
              </Tabs>
            </Box>

            {/* Tab Panels */}
            <TabPanel value={tabValue} index={0}>
              <SingleTextInput 
                setLoading={setLoading}
                setError={setError}
                setSuccess={setSuccess}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={1}>
              <BulkCSVUpload 
                setLoading={setLoading}
                setError={setError}
                setSuccess={setSuccess}
              />
            </TabPanel>

            <TabPanel value={tabValue} index={2}>
              <AdvancedMode 
                setLoading={setLoading}
                setError={setError}
                setSuccess={setSuccess}
              />
            </TabPanel>
          </Paper>

          {/* Loading Overlay */}
          {loading && (
            <Box
              sx={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                zIndex: 9999
              }}
            >
              <Paper sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ mt: 2 }}>
                  Processing...
                </Typography>
              </Paper>
            </Box>
          )}

          {/* Footer */}
          <Box sx={{ mt: 4, textAlign: 'center', color: 'text.secondary' }}>
            <Typography variant="body2">
              Ticket Classification MLOps System v1.0.0
            </Typography>
            <Typography variant="caption">
              Built with FastAPI, React, and Sentence Transformers
            </Typography>
          </Box>
        </Box>
      </Container>
    </div>
  );
}

export default App;

// Made with Bob
