# Runtime Configuration

## Overview

This document specifies the runtime configuration for the Production deployment of the Physical AI & Humanoid Robotics application, including backend API endpoints and frontend configuration.

---

## Production Backend API

### Provider
**Railway** (Cloud application platform)

### Configuration
- **Backend Public URL:** `https://hackathon1-q4-production.up.railway.app`
- **API Base Path:** `/api`
- **Full API Base:** `https://hackathon1-q4-production.up.railway.app/api`

### Status
This is a **public configuration** (NOT a secret) and can be safely committed to version control and displayed in code.

---

## Frontend API Configuration Rule

### Core Rule
Frontend applications **MUST** construct API calls using the formula:

```
{BACKEND_PUBLIC_URL}{API_BASE_PATH}{ENDPOINT_PATH}
```

### Example
For a chatbot query endpoint:
```
https://hackathon1-q4-production.up.railway.app/api/chatbot/query
```

### Implementation

#### 1. **Global API Configuration** (`textbook/static/js/api-url-config.js`)
Sets global window variables for all API endpoints:
- `window.API_BASE_URL` - Base URL for API calls
- `window.CHATBOT_QUERY_ENDPOINT` - Chatbot query endpoint
- `window.HEALTH_CHECK_ENDPOINT` - Health check endpoint

#### 2. **Environment Configuration Files**

##### Development (`.env.development`)
```env
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_API_PATH=/api
REACT_APP_CHATBOT_QUERY_ENDPOINT=http://localhost:8000/api/chatbot/query
REACT_APP_HEALTH_CHECK_ENDPOINT=http://localhost:8000/api/ready
```

##### Production (`.env.production`)
```env
REACT_APP_API_BASE_URL=https://hackathon1-q4-production.up.railway.app
REACT_APP_API_PATH=/api
REACT_APP_CHATBOT_QUERY_ENDPOINT=https://hackathon1-q4-production.up.railway.app/api/chatbot/query
REACT_APP_HEALTH_CHECK_ENDPOINT=https://hackathon1-q4-production.up.railway.app/api/ready
```

---

## Environment Detection

The frontend automatically detects the environment and configures the appropriate backend:

### Development
- **Hostname Detection:** `localhost` or `127.0.0.1`
- **Backend URL:** `http://localhost:8000/api`
- **Usage:** Local development with local backend

### Production (GitHub Pages)
- **Hostname Detection:** `salmansiddiqui-99.github.io`
- **Backend URL:** `https://hackathon1-q4-production.up.railway.app/api`
- **Usage:** Deployed on GitHub Pages, connects to Railway backend

### Custom Deployment
- **Configuration Method:** `window.CHATBOT_QUERY_ENDPOINT` and `window.HEALTH_CHECK_ENDPOINT` environment variables
- **Usage:** For non-standard deployments

---

## API Endpoints

All endpoints are prefixed with the base path:

### Chatbot Endpoints
- **Query:** `{API_BASE_URL}/chatbot/query`
- **Example:** `https://hackathon1-q4-production.up.railway.app/api/chatbot/query`

### Health Endpoints
- **Status:** `{API_BASE_URL}/ready`
- **Example:** `https://hackathon1-q4-production.up.railway.app/api/ready`

### General API Pattern
```
{API_BASE_URL}/{RESOURCE}/{ACTION}
```

---

## CORS Configuration

### Production CORS Origins
The backend accepts requests from:
- `https://salmansiddiqui-99.github.io` (GitHub Pages)
- `http://localhost:3000` (Development frontend)

### Configuration
```env
CORS_ORIGINS=https://salmansiddiqui-99.github.io,http://localhost:3000
```

---

## Deployment Checklist

- [ ] Backend deployed on Railway at `https://hackathon1-q4-production.up.railway.app`
- [ ] Frontend `.env.production` contains correct API base URL
- [ ] CORS origins configured on backend
- [ ] API endpoints accessible and responding
- [ ] Health check endpoint returning status
- [ ] Frontend successfully connecting to backend API
- [ ] GitHub Pages deployment updated with latest configuration

---

## Troubleshooting

### API Calls Failing
1. Check `window.API_BASE_URL` in browser console
2. Verify CORS origin is allowed on backend
3. Confirm network connectivity to `https://hackathon1-q4-production.up.railway.app`
4. Check API response in Network tab (browser DevTools)

### Wrong Backend in Production
1. Verify `salmansiddiqui-99.github.io` hostname detection
2. Check `REACT_APP_API_BASE_URL` in environment
3. Clear browser cache and reload

### Development Backend Not Responding
1. Ensure local backend started: `npm run start-backend` (backend directory)
2. Verify backend running on `http://localhost:8000`
3. Check API documentation: `http://localhost:8000/docs`

---

## References

- [Frontend Configuration](./textbook/.env.production)
- [API Configuration Script](./textbook/static/js/api-url-config.js)
- [Backend Deployment Guide](./.github/DEPLOYMENT.md)
- [Implementation Roadmap](./IMPLEMENTATION_ROADMAP.md)
