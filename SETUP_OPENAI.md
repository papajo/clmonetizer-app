# Setting Up OpenAI API Key

The AI analysis feature requires a valid OpenAI API key to identify arbitrage opportunities.

## Why You're Seeing "0 Opportunities"

If you see "0 listings found" or "No arbitrage opportunities found yet" even after scraping, it's likely because:

1. **OpenAI API key is not configured** - The AI service can't analyze listings
2. **Invalid API key** - The key might be expired or incorrect
3. **API key not loaded** - The environment variable isn't set when the backend starts

## Quick Setup

### 1. Get Your API Key

1. Go to https://platform.openai.com/account/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)

### 2. Set the Environment Variable

**Option A: Export in Terminal (Temporary)**
```bash
export OPENAI_API_KEY=sk-your-actual-key-here
```

**Option B: Create `.env` File (Permanent)**
```bash
# In the project root directory
echo "OPENAI_API_KEY=sk-your-actual-key-here" >> .env
```

### 3. Restart Backend

After setting the API key, restart the backend:

```bash
./stop.sh
./restart.sh
```

Or manually:
```bash
# Stop backend
pkill -f uvicorn

# Start backend (make sure you're in the project root)
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Re-analyze Existing Listings

After setting up the API key, you can re-analyze your existing 357 listings:

1. Go to the dashboard: http://localhost:3000/dashboard
2. Click "Re-analyze Existing Listings" button
3. Wait a few minutes for the analysis to complete
4. Refresh the dashboard to see opportunities

Or use the API directly:
```bash
curl -X POST http://localhost:8000/api/listings/reanalyze
```

## Verify It's Working

1. Check the dashboard - you should see a green status if AI is configured
2. Check backend logs - you should see "Opportunity found" messages
3. After re-analysis, check the dashboard stats - opportunities count should increase

## Troubleshooting

### "Invalid API key" Error
- Make sure the key starts with `sk-`
- Check for typos or extra spaces
- Verify the key is active on OpenAI's platform

### "Rate limit exceeded" Error
- You've hit OpenAI's rate limit
- Wait a few minutes and try again
- Consider upgrading your OpenAI plan

### API Key Not Detected
- Make sure you restarted the backend after setting the variable
- Check that the environment variable is set: `echo $OPENAI_API_KEY`
- If using `.env`, make sure it's in the project root directory

## Cost Considerations

OpenAI API usage is charged per request. For 357 listings:
- Each analysis costs approximately $0.01-0.03 (depending on listing length)
- Total cost for re-analysis: ~$3.50-10.50
- Ongoing scraping: ~$0.01-0.03 per new listing

Monitor usage on OpenAI's platform dashboard.

