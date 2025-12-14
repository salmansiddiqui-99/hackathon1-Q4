// API URL configuration script
// This script runs before the React app loads and sets the API URL for ChatbotWidget

(function() {
  'use strict';

  // Determine the backend API URL
  let apiUrl = null;

  // 1. Check if API URL is set as a window variable (can be injected by deployment)
  if (window.API_BACKEND_URL) {
    apiUrl = window.API_BACKEND_URL;
    console.log('[API Config] Using API URL from window.API_BACKEND_URL:', apiUrl);
  }
  // 2. Check if we're in development (localhost)
  else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    apiUrl = 'http://localhost:8000/api';
    console.log('[API Config] Development mode - using localhost API');
  }
  // 3. For production on GitHub Pages, we need a deployed backend
  // This should be set during the build process or as a Railway environment variable
  else if (window.location.hostname === 'salmansiddiqui-99.github.io') {
    // Try to get from environment (injected during deployment)
    apiUrl = window.RAILWAY_BACKEND_URL || 'https://your-railway-backend.up.railway.app/api';
    console.log('[API Config] Production mode - using Railway API:', apiUrl);
  }
  // 4. Default fallback
  else {
    apiUrl = '/api';
    console.log('[API Config] Using relative API path');
  }

  // Set the global API URL for ChatbotWidget to use
  window.__DOCUSAURUS_API_URL__ = apiUrl;
  console.log('[API Config] Final API URL:', apiUrl);
})();
