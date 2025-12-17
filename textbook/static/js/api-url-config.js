// API Endpoint configuration script
// This script runs before the React app loads and sets the specific API endpoints for ChatbotWidget

(function() {
  'use strict';

  // Determine the backend base URL based on environment
  let backendUrl = null;

  // 1. Check if backend URL is set as a window variable (can be injected by deployment)
  if (window.BACKEND_URL) {
    backendUrl = window.BACKEND_URL;
    console.log('[API Config] Using backend URL from window.BACKEND_URL:', backendUrl);
  }
  // 2. Check if we're in development (localhost)
  else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    backendUrl = 'http://localhost:8000';
    console.log('[API Config] Development mode - using localhost backend');
  }
  // 3. For production on GitHub Pages, use Railway backend
  else if (window.location.hostname === 'salmansiddiqui-99.github.io') {
    backendUrl = 'https://hackathon1-q4-production.up.railway.app';
    console.log('[API Config] Production mode - using Railway backend');
  }
  // 4. Default fallback
  else {
    backendUrl = window.location.origin;
    console.log('[API Config] Using current origin as backend');
  }

  // Set specific API endpoints (NOT base URLs)
  window.CHATBOT_QUERY_ENDPOINT = backendUrl + '/api/chatbot/query';
  window.HEALTH_CHECK_ENDPOINT = backendUrl + '/api/ready';

  console.log('[API Config] Chatbot Query Endpoint:', window.CHATBOT_QUERY_ENDPOINT);
  console.log('[API Config] Health Check Endpoint:', window.HEALTH_CHECK_ENDPOINT);
})();
