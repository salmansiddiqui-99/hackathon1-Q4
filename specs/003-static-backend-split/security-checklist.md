# Security Checklist: Static Hosting & Split-Backend Compatibility

**Feature**: 003-static-backend-split
**Date**: 2025-12-19
**Purpose**: Pre-deployment security validation checklist

---

## Frontend Security

### T037: API Configuration Audit

- [ ] `textbook/static/js/api-url-config.js` does NOT contain hardcoded API keys
- [ ] API endpoints are URLs only (no credentials embedded)
- [ ] Environment detection logic is safe (checks hostname, not user input)
- [ ] No credentials passed in endpoint URLs (e.g., `https://key:password@api.com` format)
- [ ] Configuration uses only environment variables, not hardcoded strings

**Verification**:
```bash
grep -E "(API_KEY|secret|Bearer|Authorization)" textbook/static/js/api-url-config.js
# Should return: (no matches or only comments)
```

### T038: ChatbotWidget Audit

- [ ] `textbook/src/components/ChatbotWidget.jsx` does NOT hardcode API keys
- [ ] No `Authorization` headers added by frontend
- [ ] No `X-API-Key` headers added by frontend
- [ ] Fetch requests only include `Content-Type` and `Accept` headers
- [ ] No Bearer tokens in request bodies or headers
- [ ] Selected text is NOT sent as anything other than `selected_text` field
- [ ] User queries are sanitized before sending

**Verification**:
```bash
grep -E "(Authorization|X-API-Key|Bearer|secret)" textbook/src/components/ChatbotWidget.jsx
# Should return: (no matches or only comments)
```

### T039: Environment Files Audit

- [ ] `.env` files are in `.gitignore`
- [ ] `.env.local` files are in `.gitignore`
- [ ] `*.env` pattern is in `.gitignore`
- [ ] Backend `.env` does NOT appear in Git history
- [ ] Frontend `.env` does NOT appear in Git history
- [ ] `.env.example` files are version-controlled (safe templates only)
- [ ] Real credentials NEVER committed to repository

**Verification**:
```bash
# Check .gitignore
cat .gitignore | grep -E "\.env"
# Output should show: *.env, .env*, or similar patterns

# Check Git history for .env files
git log --all --full-history -p -- "*.env" | head
# Should return: (no results)
```

### T040: Build Security Validation

- [ ] Built JavaScript bundles (`build/assets/js/`) do NOT contain API keys
- [ ] Built CSS files (`build/assets/css/`) do NOT contain credentials
- [ ] Built HTML files (`build/index.html`) do NOT contain credentials
- [ ] No `process.env` patterns in built output
- [ ] No `window.ENV` patterns in built output
- [ ] No inline scripts contain sensitive data

**Verification**:
```bash
# Check built bundles for credentials
grep -r "API_KEY\|secret\|Bearer\|sk-" build/
# Should return: (no matches)

# Verify no env vars leaked
grep -r "process\.env\|window\.ENV" build/
# Should return: (no matches)
```

---

## Backend Security

### API Endpoint Security

- [ ] Health check endpoint (`GET /api/ready`) does NOT expose sensitive info
- [ ] Chatbot endpoint (`POST /api/chatbot/query`) validates input
- [ ] Error responses do NOT include stack traces
- [ ] Error responses do NOT reveal internal paths or database schema
- [ ] No API credentials in response bodies
- [ ] No credentials in error messages

**Verification**:
```bash
curl http://localhost:8000/api/ready
# Should return: {"status": "ok", "uptime_seconds": X, "version": "...", "timestamp": "..."}
# No credentials or stack traces
```

### Environment Variable Security

- [ ] All sensitive config in environment variables, NOT in code
- [ ] `GEMINI_API_KEY` NOT in source files
- [ ] `COHERE_API_KEY` NOT in source files
- [ ] `QDRANT_API_KEY` NOT in source files
- [ ] `DATABASE_URL` with password NOT in source files
- [ ] Railway environment variables configured (NOT in .env file)

**Verification**:
```bash
grep -r "GEMINI_API_KEY\|COHERE_API_KEY\|QDRANT_API_KEY" backend/src/
# Should return: (no matches - only references like os.getenv())

grep -r "sk-" backend/src/
# Should return: (no matches for hardcoded keys)
```

### CORS Security

- [ ] CORS configured with explicit origin allowlist (NOT `*`)
- [ ] Only `https://salmansiddiqui-99.github.io` in production CORS_ORIGINS
- [ ] `http://localhost:3000` in development CORS_ORIGINS only
- [ ] No wildcard origins (`*`) used
- [ ] Credentials NOT included in CORS response headers unnecessarily

**Verification**:
```bash
# Check config.py
grep -A 5 "CORS_ORIGINS" backend/src/config.py
# Should show explicit origins, not wildcards
```

---

## Data Security

### User Input

- [ ] Query input validated for length (1-1000 characters)
- [ ] Selected text validated for length (max 5000 characters)
- [ ] No SQL injection possible (using Pydantic + ORM)
- [ ] No XSS possible (user input sanitized before display)
- [ ] Chapter IDs validated against known list

### Data in Transit

- [ ] HTTPS enforced in production
- [ ] No sensitive data in query strings
- [ ] No sensitive data in response bodies
- [ ] Streaming responses properly handle sensitive data

### Data at Rest

- [ ] User queries NOT stored in logs with sensitive context
- [ ] Error logs do NOT contain full request bodies
- [ ] Database passwords NOT in configuration files
- [ ] API keys NOT in database

---

## Infrastructure Security

### GitHub Repository

- [ ] No `.env` files committed
- [ ] No API keys in commit history
- [ ] `.gitignore` properly configured
- [ ] GitHub Secrets used for deployment credentials
- [ ] Branch protection enabled on main branches

### Railway Deployment

- [ ] Environment variables configured in Railway dashboard
- [ ] No secrets in Docker files
- [ ] CORS_ORIGINS environment variable set correctly
- [ ] All required API keys set as Railway Secrets
- [ ] Production URLs use HTTPS only

### GitHub Pages Deployment

- [ ] No API keys in built assets
- [ ] No credentials in JavaScript bundles
- [ ] HTTPS enforced (GitHub Pages default)
- [ ] Only public content deployed

---

## Pre-Deployment Checklist

Before deploying to production:

- [ ] Run security tests: `npm test security.test.js`
- [ ] Verify no credentials in Git history: `git log --all --full-history -p -- "*.env"`
- [ ] Scan built bundles: `grep -r "API_KEY\|Bearer\|sk-" build/`
- [ ] Review CORS configuration
- [ ] Verify Railway environment variables
- [ ] Test CORS headers in production
- [ ] Review error responses (no sensitive info)
- [ ] Check .gitignore excludes all .env files
- [ ] Verify API responses don't leak credentials

---

## Post-Deployment Validation

After deploying to production:

- [ ] Test health check endpoint returns correct response
- [ ] Test chatbot endpoint works end-to-end
- [ ] Verify CORS headers present for allowed origins
- [ ] Check browser console for errors (no stack traces)
- [ ] Verify no credentials in Network tab (DevTools)
- [ ] Test from GitHub Pages domain
- [ ] Test error scenarios (backend down, invalid input)

---

## Remediation Actions

If security issues found:

1. **Credentials in code**:
   - Remove immediately
   - Rotate compromised keys
   - Force push to remove from history (if on feature branch)
   - Never use compromised key again

2. **Credentials in build**:
   - Clean build directory
   - Rebuild from clean source
   - Verify no credentials in new build
   - Redeploy

3. **Credentials in Git history**:
   - Use `git filter-branch` or `BFG Repo-Cleaner` to remove
   - Rotate compromised keys
   - Force push after cleanup (if team agrees)

4. **CORS misconfiguration**:
   - Update CORS_ORIGINS immediately
   - Restart backend
   - Verify CORS headers in test requests

---

## Security Training

All developers should understand:

- ✅ Never hardcode API keys
- ✅ Never commit .env files
- ✅ Always use environment variables for secrets
- ✅ Always sanitize user input
- ✅ Always use HTTPS in production
- ✅ Always validate CORS settings
- ✅ Always check error messages for info leakage
- ✅ Always review security checklists before deployment

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE-798: Use of Hard-Coded Credentials](https://cwe.mitre.org/data/definitions/798.html)
- [CWE-79: Improper Neutralization of Input During Web Page Generation](https://cwe.mitre.org/data/definitions/79.html)
- [CORS Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [API Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/REST_API_Security_Cheat_Sheet.html)

---

**Last Updated**: 2025-12-19
**Status**: ✅ Ready for security validation
