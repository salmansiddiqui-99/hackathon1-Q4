# Feature Specification: Static Hosting & Split-Backend Compatibility

**Feature Branch**: `003-static-backend-split`
**Created**: 2025-12-18
**Status**: Draft
**Input**: User description: "Static Hosting & Split-Backend Constraints Enforcement - Ensure the Docusaurus frontend deployed on GitHub Pages operates reliably with a separately hosted FastAPI backend on Railway, without broken assets, incorrect routing, or invalid API assumptions."

## User Scenarios & Testing

### User Story 1 - Frontend Developer Deploys Static Site to GitHub Pages (Priority: P1)

A frontend developer builds and deploys a Docusaurus site to GitHub Pages at a non-root path (`/hackathon1-Q4/`). All static assets (CSS, JS, images, fonts) must load correctly without 404 errors, and relative paths must be respected under the baseUrl configuration.

**Why this priority**: This is the foundational requirement. Without correct asset resolution, the entire application fails. Every user will encounter this immediately upon page load.

**Independent Test**: Deploy the built Docusaurus site to GitHub Pages and verify all static assets load with HTTP 200 status and no 404 errors in browser DevTools. This alone validates the asset resolution contract.

**Acceptance Scenarios**:

1. **Given** a Docusaurus site configured with `baseUrl: "/hackathon1-Q4/"`, **When** deployed to GitHub Pages, **Then** all CSS, JavaScript, and image assets resolve to correct URLs under `/hackathon1-Q4/assets/` and `/hackathon1-Q4/img/`
2. **Given** a user reloads the page with cache disabled (Ctrl+Shift+R), **When** DevTools Network tab is checked, **Then** no 404 errors appear for any static asset
3. **Given** a user navigates between different pages, **When** each page loads, **Then** all styles and scripts remain applied correctly with no broken element rendering

---

### User Story 2 - Backend API Calls Succeed from GitHub Pages (Priority: P1)

A frontend user opens the deployed Docusaurus site and interacts with the AI chatbot widget. API calls are sent to a separately hosted Railway backend using explicit, hardcoded endpoint URLs. Cross-origin requests succeed due to CORS configuration, and responses are processed correctly.

**Why this priority**: This ensures the split-backend architecture works end-to-end. Without this, the chatbot feature is completely non-functional in production.

**Independent Test**: Open the deployed site, verify CORS headers in DevTools Network tab allow the GitHub Pages origin, send a chatbot query, and confirm the backend at Railway domain receives and responds to the request successfully. This validates the frontend→backend contract.

**Acceptance Scenarios**:

1. **Given** the chatbot widget is displayed on the frontend, **When** a user enters a query and clicks Send, **Then** a POST request is sent to `https://hackathon1-q4-production.up.railway.app/api/chatbot/query` with CORS headers
2. **Given** the backend is running with correct CORS configuration, **When** the browser sends the cross-origin request, **Then** the response includes `Access-Control-Allow-Origin: https://salmansiddiqui-99.github.io` and the request succeeds (HTTP 200)
3. **Given** a successful API response is received, **When** the response body contains NDJSON-formatted tokens, **Then** the frontend parses and displays each token in real-time without errors

---

### User Story 3 - Backend Health Check Prevents UI Errors (Priority: P1)

Before displaying the chatbot UI, the frontend validates backend availability by calling `/api/ready`. If the backend is unreachable or returns an error, the chatbot widget displays a graceful error message and disables user input. Users understand why the chatbot is unavailable and can retry when the backend recovers.

**Why this priority**: This prevents confusing 404 or 500 errors in the browser and ensures users have a clear, safe experience even when the backend fails.

**Independent Test**: With the backend stopped/unreachable, open the frontend and verify the chatbot shows an error message (not a raw HTTP error) and the Send button is disabled. Then restart the backend and verify the chatbot resumes functionality without requiring a page reload. This validates graceful degradation.

**Acceptance Scenarios**:

1. **Given** the frontend loads and the backend at Railway is unreachable (e.g., down for maintenance), **When** the health check fetch to `/api/ready` times out or fails, **Then** the chatbot widget displays a message like "Backend Temporarily Unavailable" instead of crashing
2. **Given** the backend is unavailable, **When** the user clicks the Send button, **Then** nothing happens—the button remains disabled and no 404 error is logged to the console
3. **Given** the backend was previously unavailable, **When** the backend comes back online, **Then** the health check retries automatically and the chatbot resumes accepting user input without requiring a page reload

---

### User Story 4 - No API Key Leaks in Frontend Code (Priority: P1)

A security auditor reviews the frontend code and network traffic. No API keys, bearer tokens, or secrets appear in JavaScript bundles, HTML, or network request headers. All sensitive credentials remain on the backend and are never transmitted to the client.

**Why this priority**: This is a critical security requirement. Leaked credentials enable attackers to bypass access controls and compromise the backend. This must be verified before any production deployment.

**Independent Test**: Inspect the frontend codebase (including built bundles), check all network requests in DevTools, and search for hardcoded API keys, secrets, or sensitive tokens. No credentials should be found. This validates the security contract.

**Acceptance Scenarios**:

1. **Given** the frontend code is deployed to GitHub Pages, **When** an auditor searches the JavaScript bundles for patterns like `API_KEY=`, `secret`, `Bearer `, **Then** no hardcoded credentials are found
2. **Given** a chatbot query is sent to the backend, **When** the DevTools Network tab is inspected, **Then** the request headers contain no `Authorization`, `X-API-Key`, or other credential headers—only standard CORS and Content-Type headers
3. **Given** the backend receives the user query, **When** the backend processes it using internal credentials, **Then** those credentials never appear in the frontend, network traffic, or error messages sent back to the client

---

### User Story 5 - Error Messages Are Deterministic and User-Friendly (Priority: P2)

When an API call fails (network error, backend timeout, invalid response), the frontend displays a clear, non-technical error message. Users understand what went wrong without seeing raw HTTP errors or stack traces. Error messages are consistent across all scenarios.

**Why this priority**: This improves user experience and prevents confusion. Clear messaging increases user confidence and reduces support burden.

**Independent Test**: Trigger various failure scenarios (backend timeout, no internet, backend returns 500) and verify that each produces an appropriate, user-friendly error message without leaking technical details. This validates error handling.

**Acceptance Scenarios**:

1. **Given** the backend times out on a chatbot query, **When** the frontend detects the timeout, **Then** it displays "Request timed out. Please try again." instead of a raw HTTP error
2. **Given** the backend returns a 500 error, **When** the error is caught by the frontend, **Then** it displays "Something went wrong. Please try again later." and logs the error internally for debugging, but does not show the stack trace to the user
3. **Given** the backend returns no results (RAG query returns empty), **When** the frontend processes the response, **Then** it displays "Not found in the book." instead of a blank response or error state

---

### Edge Cases

- What happens when the GitHub Pages domain changes (e.g., custom domain is configured)? The frontend must continue to work with the new domain as long as CORS is reconfigured on the backend.
- What happens when the backend endpoint URL is misconfigured (e.g., wrong port or path)? The health check should fail, and the chatbot should display an unavailable message rather than silently failing.
- What happens if the backend responds with partial data (e.g., incomplete NDJSON stream)? The frontend should display the partial response received so far and indicate that additional data was incomplete.
- What happens if the user's network is intermittently flaky? The frontend should retry health checks periodically (e.g., every 30 seconds) and attempt to resume the connection when the network stabilizes.
- What happens if multiple tabs/windows of the site are open? Each instance should independently check backend health without interfering with others.

## Requirements

### Functional Requirements

**Frontend Asset Resolution**

- **FR-001**: All static assets (CSS, JS, images, SVG, fonts) MUST be referenced using Docusaurus-compatible paths (e.g., `useBaseUrl()` or static directory) that respect the configured `baseUrl`
- **FR-002**: The build process MUST fail with an error if any unresolved asset paths are detected (e.g., absolute root paths like `/logo.svg` instead of relative paths)
- **FR-003**: The frontend MUST NOT use absolute paths starting with `/` for assets. All asset paths MUST be relative or use Docusaurus utilities

**Explicit Backend API Configuration**

- **FR-004**: The frontend MUST define a single point of configuration for the API base URL (e.g., `window.API_BASE_URL` or `process.env.REACT_APP_API_URL`)
- **FR-005**: The frontend MUST support different API endpoints for local development (`http://localhost:8000`) and production (`https://hackathon1-q4-production.up.railway.app`)
- **FR-006**: All API calls (chatbot, health check, embeddings, data retrieval) MUST be prefixed with the configured API base URL. No hardcoded endpoint URLs are allowed in component code
- **FR-007**: The API endpoint configuration MUST be set at application startup (not dynamically changed during runtime)

**Static Frontend ↔ Dynamic Backend Contract**

- **FR-008**: The frontend MUST use HTTPS for all API calls in production environments
- **FR-009**: The backend MUST expose a public health check endpoint at `GET /api/ready` that returns HTTP 200 if operational and appropriate error codes (503, 500) if unavailable
- **FR-010**: The frontend MUST call `/api/ready` on component mount and periodically (e.g., every 30 seconds) to validate backend availability
- **FR-011**: If the health check fails or times out (after 2 seconds), the frontend MUST disable the chatbot UI and display a user-friendly error message
- **FR-012**: The chatbot input field MUST display a placeholder message indicating backend status (e.g., "Backend offline..." when unavailable)

**CORS & Security Constraints**

- **FR-013**: The backend MUST explicitly configure CORS middleware to allow requests from the GitHub Pages domain (e.g., `https://salmansiddiqui-99.github.io`)
- **FR-014**: The backend MUST include CORS headers in all successful responses: `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`
- **FR-015**: The backend MUST reject requests from unknown or untrusted origins by returning HTTP 403 Forbidden or by omitting CORS headers
- **FR-016**: The frontend MUST NOT embed API keys, bearer tokens, or secrets in code, configuration files, or network requests. All authentication MUST be handled server-side

**Failure Handling & User Safety**

- **FR-017**: If an API request fails, the frontend MUST display a deterministic, user-friendly error message (not a raw HTTP error or stack trace)
- **FR-018**: If the backend returns no results (e.g., RAG query returns empty), the chatbot MUST respond with "Not found in the book." instead of an error or blank response
- **FR-019**: The frontend MUST NOT retry failed requests indefinitely. Retries MUST be limited to a maximum of 3 attempts, with exponential backoff
- **FR-020**: Streaming responses (NDJSON format) MUST be parsed incrementally. If the stream breaks midway, the frontend MUST display the partial response received so far and indicate the stream was incomplete

### Key Entities

- **API Configuration**: Represents the centralized endpoint URLs for backend communication (base URL, health check URL, etc.). Attributes: `baseUrl`, `healthCheckUrl`, `timeout`
- **Health Status**: Represents the current availability state of the backend. Attributes: `isAvailable` (boolean), `lastCheckTime` (timestamp), `retryCount` (number)
- **Error Response**: Represents a standardized error message shown to the user. Attributes: `message` (user-friendly text), `code` (internal error identifier), `timestamp` (when error occurred)

## Success Criteria

### Measurable Outcomes

- **SC-001**: The Docusaurus build completes with zero asset warnings and zero unresolved path errors
- **SC-002**: Zero 404 errors appear in browser DevTools Network tab when the site is fully loaded on GitHub Pages (with cache disabled)
- **SC-003**: The `/api/ready` endpoint is reachable from the browser within 2 seconds (before the frontend times out)
- **SC-004**: The chatbot successfully sends queries to the Railway backend and receives responses without CORS errors
- **SC-005**: When the backend is offline, the chatbot gracefully disables its UI and displays an error message (not a raw HTTP error) within 2.5 seconds
- **SC-006**: When the backend comes back online, the chatbot automatically resumes functionality without requiring a page reload
- **SC-007**: Zero API keys, tokens, or credentials appear in the frontend source code, built bundles, or network traffic
- **SC-008**: 95% of API requests complete successfully (200 status) when both frontend and backend are operational
- **SC-009**: Error messages displayed to users are consistent and user-friendly across all failure scenarios
- **SC-010**: The site operates identically in local development (`localhost:3000` + `localhost:8000`) and production (`GitHub Pages` + `Railway`) environments

## Assumptions

1. **Docusaurus Version**: The site uses Docusaurus v2.x with CommonJS config support
2. **Backend Statefulness**: The FastAPI backend is stateless and can handle requests from any origin (with CORS validation)
3. **Network Connectivity**: Users have stable internet connections; temporary network blips may occur but persistent disconnections are out of scope
4. **CORS Pre-flight**: Browsers will send OPTIONS pre-flight requests; the backend must support these
5. **API Response Format**: All backend responses use JSON (or NDJSON for streaming). Other formats are out of scope
6. **Environment Variables**: Frontend cannot access secrets; sensitive config is backend-only
7. **GitHub Pages Behavior**: GitHub Pages serves static files with appropriate caching headers; no server-side rendering or redirects are used

## Constraints

- **No Reverse Proxy**: GitHub Pages does not support reverse proxying to the backend; the frontend must explicitly call the Railway domain
- **No Server-Side Rendering**: The frontend is purely client-side (Docusaurus/React). No Node.js APIs or server-side code generation
- **No Dynamic Environment Variables**: The frontend cannot read environment variables at runtime; configuration must be set at build time or hardcoded for production
- **Static Hosting Only**: The frontend must work entirely within GitHub Pages' static hosting limitations (no API routes, no server-side auth, no databases)
- **HTTPS in Production**: All API calls in production must use HTTPS; HTTP is not supported for security reasons
- **No Third-Party Dependencies for API Config**: The API configuration should not depend on external services or libraries (e.g., config servers, feature flags)
- **Browser Support**: Only modern browsers (Chrome, Firefox, Safari, Edge) with fetch API support are required

## Out of Scope

- Load balancing or multi-region backend failover (single backend endpoint only)
- Custom domain migration strategies beyond CORS reconfiguration
- Real-time bidirectional communication (WebSockets) - polling/REST is sufficient
- Analytics or monitoring dashboards for frontend/backend health
- Client-side caching strategies or service workers
- Authentication/authorization (assumes public API; no user login required)
