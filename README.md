# CL Monetizer App

Automatically discover arbitrage opportunities on Craigslist using AI-powered analysis.

## 🚀 Quick Start

### One-Click Restart (Easiest)
```bash
./restart.sh
```

This will automatically:
- ✅ Stop any running servers
- ✅ Check and fix Node.js version if needed
- ✅ Start backend (port 8000)
- ✅ Start frontend (port 3000)

### If Node.js Version Error

If you see "Node.js version >=20.9.0 is required", run:
```bash
./fix_nodejs.sh
```

Then run `./restart.sh` again.

## 📋 Prerequisites

- **Node.js >=20.9.0** (Next.js requirement)
- **Python 3.8+**
- **PostgreSQL** (or SQLite for development)

## 🛠️ Manual Setup

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📄 Pages

- `/` - Landing page
- `/dashboard` - Main dashboard with stats
- `/dashboard/listings` - View all scraped listings
- `/dashboard/leads` - View leads and opportunities
- `/dashboard/scraper` - Start scraping jobs
- `/dashboard/settings` - Settings

## 🛑 Stop Servers

```bash
./stop.sh
```

## 🧪 Test Routes

```bash
./test_routes.sh
```

## 📝 Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost/clmonetizer
OPENAI_API_KEY=your_openai_api_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For development, SQLite is used by default if `DATABASE_URL` is not set.

## 🐛 Troubleshooting

### 404 Errors on Pages
**Quick Fix:**
```bash
./fix_404.sh
```

This automatically clears the Next.js cache and restarts the server.

**Manual Steps:**
1. Stop frontend: `pkill -f "next dev"`
2. Clear cache: `cd frontend && rm -rf .next`
3. Restart: `cd frontend && npm run dev`
4. Wait 15-20 seconds for routes to compile
5. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

### Dashboard Not Updating
1. Check backend is running: `curl http://localhost:8000/health`
2. Check browser console (F12) for errors
3. Click the "Refresh" button on the dashboard

### Node.js Version Issues
- Run `./fix_nodejs.sh` to automatically fix
- Or manually: `brew install node@20` then add to PATH

### Check Database
See `CHECK_DATABASE.md` for detailed instructions on checking if listings are saved.

## 📚 Documentation

- `QUICK_START.md` - Quick reference guide
- `CHECK_DATABASE.md` - How to check database contents
- `tasks.md` - Development tasks and progress

