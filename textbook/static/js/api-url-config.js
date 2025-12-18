// API Endpoint configuration script
// This script runs before the React app loads and sets the specific API endpoints for ChatbotWidget

(function() {
  'use strict';

  let chatbotQueryEndpoint = null;
  let healthCheckEndpoint = null;

  // 1. Check if endpoints are set as window variables (can be injected by deployment)
  if (window.CHATBOT_QUERY_ENDPOINT && window.HEALTH_CHECK_ENDPOINT) {
    chatbotQueryEndpoint = window.CHATBOT_QUERY_ENDPOINT;
    healthCheckEndpoint = window.HEALTH_CHECK_ENDPOINT;
    console.log('[API Config] Using endpoints from window variables');
  }
  // 2. Check if we're in development (localhost)
  else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    chatbotQueryEndpoint = 'http://localhost:8000/api/chatbot/query';
    healthCheckEndpoint = 'http://localhost:8000/api/ready';
    console.log('[API Config] Development mode - using localhost backend');
  }
  // 3. For production on GitHub Pages, use Railway backend with EXACT endpoint URLs
  else if (window.location.hostname === 'salmansiddiqui-99.github.io') {
    chatbotQueryEndpoint = 'https://hackathon1-q4-production.up.railway.app/api/chatbot/query';
    healthCheckEndpoint = 'https://hackathon1-q4-production.up.railway.app/api/ready';
    console.log('[API Config] Production mode - using Railway backend');
  }
  // 4. Default fallback - NO FALLBACK TO /api paths
  else {
    console.warn('[API Config] Unknown environment, using relative paths');
    chatbotQueryEndpoint = '/api/chatbot/query';
    healthCheckEndpoint = '/api/ready';
  }

  // Validate endpoints - CRITICAL: endpoints must not be just base /api
  if (chatbotQueryEndpoint && chatbotQueryEndpoint.endsWith('/api')) {
    console.error('[API Config] ERROR: Chatbot endpoint is just "/api" base path, not a specific endpoint!', chatbotQueryEndpoint);
  }
  if (healthCheckEndpoint && healthCheckEndpoint.endsWith('/api')) {
    console.error('[API Config] ERROR: Health endpoint is just "/api" base path, not a specific endpoint!', healthCheckEndpoint);
  }

  // Set the global endpoints
  window.CHATBOT_QUERY_ENDPOINT = chatbotQueryEndpoint;
  window.HEALTH_CHECK_ENDPOINT = healthCheckEndpoint;

  console.log('[API Config] Final Chatbot Query Endpoint:', window.CHATBOT_QUERY_ENDPOINT);
  console.log('[API Config] Final Health Check Endpoint:', window.HEALTH_CHECK_ENDPOINT);
})();
