# Google Gemini API Setup - Quick Guide

**Status**: Ready to Configure
**API**: Google Gemini Pro
**Purpose**: LLM response generation for RAG chatbot

---

## Quick Steps to Get Gemini API Key

### Step 1: Go to Google Cloud Console
1. Visit https://console.cloud.google.com/
2. Login with your Google account (create one if needed)

### Step 2: Create or Select Project
1. At the top, click **Select a Project**
2. Click **NEW PROJECT**
3. Enter project name: `hackathon1-Q4-chatbot`
4. Click **CREATE**
5. Wait 1-2 minutes for project to be created

### Step 3: Enable Generative Language API
1. In the search bar at the top, type: `generative language api`
2. Click on **Generative Language API**
3. Click **ENABLE**
4. Wait for API to be enabled (takes ~30 seconds)

### Step 4: Create API Key
1. Click **CREATE CREDENTIALS** button
2. Select **API Key**
3. Copy the API key that appears
4. Save it somewhere safe (you'll need it for Railway)

### Step 5: (Optional) Set Usage Quotas
To avoid unexpected charges:
1. Go to **APIs & Services** → **Credentials**
2. Click on the API key you just created
3. Scroll to **API restrictions**
4. Select **Restrict key** and choose **Generative Language API**
5. Scroll to **Application restrictions**
6. Set quota limits if needed

---

## API Key Format

Your Gemini API key will look like:
```
AIza_SomeLongStringOfCharactersHere
```

**Note**: Keep this key private! Don't share it publicly.

---

## Railway Configuration

Once you have your Gemini API key:

1. Go to Railway Dashboard
2. Click Backend Service → **Variables**
3. Add this environment variable:
   ```
   GEMINI_API_KEY=AIza_[your-key-here]
   ```
4. Click **Deploy** to apply changes

---

## Testing Your API Key

To verify the API key works:

```bash
# Replace with your actual API key
GEMINI_API_KEY=AIza_...

# Test with a simple API call
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${GEMINI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "What is ROS 2?"
      }]
    }]
  }'

# Expected response: JSON with generated text
```

---

## Free Tier Limits

Google Gemini API free tier includes:
- **60 requests per minute** (RPM)
- **1 million tokens per month** (approximately)
- Access to Gemini Pro model
- No credit card required initially

**Upgrade to Paid when**:
- You exceed 1 million tokens/month
- You need higher RPM limits
- You want access to latest models

---

## Cost Estimate

| Metric | Free Tier | Paid Tier |
|--------|-----------|-----------|
| Tokens/month | 1M free | ~$0.0001 per token |
| Requests/min | 60 RPM | Higher with upgrade |
| Cost | $0 | ~$10-50/month (typical usage) |

---

## Troubleshooting

### Issue: "API key not valid"
**Fix**:
1. Verify key starts with `AIza_`
2. Check Generative Language API is enabled
3. Copy key again from Google Cloud Console

### Issue: "API not enabled"
**Fix**:
1. Go to Google Cloud Console
2. Search for "Generative Language API"
3. Click **ENABLE**

### Issue: "Quota exceeded"
**Fix**:
1. Upgrade to paid tier in Google Cloud Console
2. Or wait for quota to reset (monthly)

### Issue: "Invalid API response"
**Fix**:
1. Check Gemini API status: https://status.cloud.google.com/
2. Try test curl command above
3. Check Railway logs for detailed error

---

## API Models Available

You can use different Gemini models:

| Model | Purpose | Speed | Cost |
|-------|---------|-------|------|
| `gemini-pro` | Text generation | Fast | Free/Low |
| `gemini-pro-vision` | Images + text | Medium | Higher |
| `gemini-1.5-pro` | Advanced reasoning | Slower | Higher |

**Recommendation**: Use `gemini-pro` for chatbot responses

---

## Next Steps

1. **Create Google account** (if needed)
2. **Create Google Cloud project**
3. **Enable Generative Language API**
4. **Create API key**
5. **Add to Railway** as `GEMINI_API_KEY`
6. **Test** the health endpoint
7. **Deploy** chatbot

---

## Useful Links

- Google Cloud Console: https://console.cloud.google.com/
- Gemini API Docs: https://ai.google.dev/
- Google Cloud Status: https://status.cloud.google.com/
- Price Calculator: https://cloud.google.com/pricing/details/generative-ai

---

## Support

If you encounter issues:

1. Check Google Cloud Console for API status
2. Verify API key in Railway environment variables
3. Check Railway logs for error details
4. Review Gemini API documentation: https://ai.google.dev/

---

**Status**: Ready to configure ✅
**Next**: Follow the 5 steps above to get your Gemini API key
**Then**: Add to Railway as GEMINI_API_KEY environment variable
