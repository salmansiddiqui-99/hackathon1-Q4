# 🧪 Manual Frontend Testing Guide

## How to Test the Chatbot on GitHub Pages

**Live URL**: https://salmansiddiqui-99.github.io/hackathon1-Q4/

### Step 1: Open the Website
1. Navigate to: https://salmansiddiqui-99.github.io/hackathon1-Q4/
2. Wait for the page to fully load

### Step 2: Locate the Chatbot Widget
- Look for a **floating chat button** in the bottom-right corner (💬 icon)
- The button should be a circular gradient button

### Step 3: Test Backend Health Check
1. Open your browser's Developer Console (F12 → Console tab)
2. Click the chat button to open the chatbot
3. Watch the console for health check messages:
   - ✅ Success: "Backend health check successful"
   - ⚠️ Timeout: Console warning after 2 seconds

### Step 4: Test Global Search Mode
1. Ensure chat is open
2. Select "Global" mode (default)
3. Type a question: **"What is ROS 2?"**
   - Must be at least 10 characters
   - Press Enter or click Send button (➤)
4. **Expected Behavior**:
   - Loading spinner appears with "Searching textbook..."
   - Error message appears: "Failed to generate response: Gemini API error..."
   - ⚠️ **Note**: This is expected - Gemini API quota exhausted
   - The error shows the streaming integration is working!

### Step 5: Test Text Selection Mode
1. Highlight any text on the page (20+ characters minimum)
2. Expected: Chat widget should auto-open with "Selection" mode activated
3. Notice the text preview at bottom: "📍 Using selected text: '...'"
4. Type a question about the selected text
5. **Expected Behavior**:
   - Same Gemini error (as above)
   - But confirm the "Selection" mode was triggered

### Step 6: Test Offline Error Handling
1. In DevTools, go to Network tab
2. Set network to "Offline" (throttle dropdown)
3. Try to ask a question
4. **Expected**: Within 2 seconds, error overlay appears:
   - "⚠️ Backend Temporarily Unavailable"
   - "Please refresh the page or try again later"
   - "🔄 Retry Connection" button

### Step 7: Check Network Requests (Developer Tools)
1. Open DevTools → Network tab
2. Send a query
3. Look for request: `POST /api/chatbot/query`
4. Response body should show:
   ```json
   {"type": "error", "data": "...Gemini API error..."}
   ```
5. **Verify**: Response is NDJSON format (not JSON)

### Step 8: Verify Console Logging
1. Open DevTools → Console tab
2. Send a query
3. Look for logs:
   ```
   ✓ "Cache hit for embedding: ..." (if repeated queries)
   ✓ "Backend health check failed: ..." (if offline)
   ✓ "Failed to parse NDJSON line: ..." (if parsing errors)
   ```

## Expected Results Summary

| Feature | Test | Status | Notes |
|---------|------|--------|-------|
| Chat widget loads | Click button | ✅ WORKS | Floating button visible |
| Health check (online) | Page load | ✅ WORKS | 2-second timeout |
| Global search query | Ask question | ⚠️ ERROR | Gemini quota (expected) |
| Text selection mode | Highlight text | ✅ WORKS | Auto-open + preview |
| Offline error UI | Go offline | ✅ WORKS | Error overlay + retry |
| NDJSON format | DevTools | ✅ WORKS | Response type verified |
| Error handling | Query fails | ✅ WORKS | Error shown with fallback |

## What's Working ✅

- Frontend UI/UX
- Health checks (2-second timeout)
- Text selection detection
- Offline error handling
- NDJSON streaming format
- Error message display
- Retry functionality

## What's Not Working ⚠️

- Chatbot responses (Gemini API quota exhausted)
- LLM token generation (need paid API key)

## To Restore Full Functionality

Need to update `backend/.env` with paid-tier Gemini API key:

```bash
# In backend/.env
GEMINI_API_KEY=your_paid_tier_api_key_here
```

Then redeploy backend (Railway will auto-redeploy on env var update).

---

**All frontend code is working correctly. The only blocker is the LLM API credential.**
