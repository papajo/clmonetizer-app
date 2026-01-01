# Setting Up Gemini API (Recommended)

Gemini API is **free** and often works better than OpenAI for this use case!

## Quick Setup

### 1. Get Your Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (it's a long string)

### 2. Add to .env File

Add this line to your `.env` file in the project root:

```bash
GEMINI_API_KEY=your-actual-api-key-here
```

**OR** you can use:

```bash
GOOGLE_API_KEY=your-actual-api-key-here
```

### 3. Restart Backend

```bash
./stop.sh
./restart.sh
```

### 4. Re-analyze Existing Listings

After setting up the API key, re-analyze your existing listings:

1. Go to http://localhost:3000/dashboard
2. Click "Re-analyze Existing Listings"
3. Wait a few minutes for analysis to complete
4. Refresh to see opportunities!

Or use the API:
```bash
curl -X POST http://localhost:8000/api/listings/reanalyze
```

## Why Gemini?

- ✅ **Free tier available** - No credit card required
- ✅ **Generous rate limits** - More requests per day
- ✅ **Fast responses** - Lower latency
- ✅ **Good quality** - Excellent for analysis tasks

## Priority Order

The app will use APIs in this order:
1. **Gemini** (if `GEMINI_API_KEY` or `GOOGLE_API_KEY` is set)
2. **OpenAI** (if `OPENAI_API_KEY` is set and Gemini is not available)

## Verify It's Working

Check the backend logs:
```bash
tail -f backend.log
```

You should see:
```
✅ Using Gemini API for AI analysis
```

Or check the API:
```bash
curl http://localhost:8000/api/stats | python3 -m json.tool
```

Look for `"ai_configured": true`

## Troubleshooting

### "Invalid API key"
- Make sure there are no extra spaces in your `.env` file
- Restart the backend after adding the key
- Check that the key starts with the correct format

### "Rate limit exceeded"
- Wait a few minutes and try again
- Gemini free tier has generous limits but they do exist

### Still showing "ai_configured": false
- Make sure `.env` file is in the project root (not in `backend/`)
- Restart the backend: `./stop.sh && ./restart.sh`
- Check backend logs for errors

