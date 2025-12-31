# 🚀 Quick Start Guide

## ⚠️ IMPORTANT: Node.js Version Requirement

**Next.js requires Node.js >=20.9.0**

Your system has Node.js 18, but Node.js 20 is already installed via Homebrew.

**Quick Fix:**
```bash
# Option 1: Use the fix script (recommended)
./fix_nodejs.sh

# Option 2: Manually add to PATH for this session
export PATH="/opt/homebrew/opt/node@20/bin:$PATH"

# Option 3: Make it permanent (add to ~/.zshrc)
echo 'export PATH="/opt/homebrew/opt/node@20/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

The `restart.sh` script will automatically use Node.js 20 if available.

## One-Click Restart

Simply run:
```bash
./restart.sh
```

This will:
- ✅ Stop any running servers
- ✅ Start the backend (port 8000)
- ✅ Start the frontend (port 3000)
- ✅ Check if everything is running

## Manual Start (if script doesn't work)

### Backend:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Access the App

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Pages

- `/dashboard` - Main dashboard
- `/dashboard/listings` - View all scraped listings
- `/dashboard/leads` - View leads
- `/dashboard/scraper` - Start scraping jobs
- `/dashboard/settings` - Settings

## Troubleshooting

### 404 Errors on Pages
1. Make sure frontend is running: `npm run dev` in frontend folder
2. Check browser console for errors
3. Try hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

### Dashboard Not Updating
1. Check backend is running: `curl http://localhost:8000/health`
2. Check browser console for API errors
3. Hard refresh the page

### Stop Everything
```bash
./stop.sh
```

Or manually:
```bash
pkill -f "uvicorn"
pkill -f "next dev"
```

