#!/bin/bash

# CL Monetizer - One-Click Restart Script
echo "🔄 Restarting CL Monetizer App..."
echo ""

# Kill any existing processes
echo "📛 Stopping existing processes..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "next start" 2>/dev/null

# Kill any processes using our ports
echo "🔌 Freeing ports 3000 and 8000..."
lsof -ti :3000 | xargs kill -9 2>/dev/null || true
lsof -ti :3001 | xargs kill -9 2>/dev/null || true
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start backend
echo "🚀 Starting backend server..."
cd backend

# Setup virtual environment
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    VENV_PATH="venv"
elif [ -d "venv" ]; then
    VENV_PATH="venv"
else
    VENV_PATH=".venv"
fi

# Activate virtual environment and install/verify dependencies
source "$VENV_PATH/bin/activate"

# Check if critical dependencies are installed
if ! python -c "import uvicorn, fastapi, sqlalchemy" 2>/dev/null; then
    echo "📦 Installing backend dependencies..."
    pip install -q -r requirements.txt || {
        echo "⚠️  Full requirements.txt failed. Installing core dependencies..."
        pip install -q uvicorn fastapi sqlalchemy pydantic python-dotenv
        echo "⚠️  Installing additional dependencies..."
        pip install -q psycopg2-binary playwright httpx alembic beautifulsoup4 pandas openai || true
        echo "⚠️  Installing langchain packages (may have conflicts)..."
        pip install -q langchain langchain-core langchain-community langchain-openai || echo "⚠️  Langchain packages failed - AI features may not work"
    }
fi

# Install playwright browsers if needed
echo "🌐 Checking Playwright browsers..."
python -c "from playwright.sync_api import sync_playwright; sync_playwright().start()" 2>/dev/null || playwright install chromium 2>/dev/null || echo "⚠️  Playwright browsers may need manual installation"

# Start backend using python -m uvicorn (more reliable than binary)
echo "🚀 Starting backend on port 8000..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs: tail -f backend.log"
echo ""

# Start frontend
echo "🚀 Starting frontend server..."
cd frontend

# Check Node.js version and try to fix
NODE_VERSION=$(node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 20 ]; then
    echo "⚠️  Node.js version issue detected!"
    echo "   Current: $(node --version 2>/dev/null || echo 'unknown')"
    echo "   Required: >=20.9.0"
    echo ""
    echo "   Attempting to use Node.js 20 if available via Homebrew..."
    if command -v brew &> /dev/null; then
        if [ -d "/opt/homebrew/opt/node@20" ]; then
            export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
            echo "   ✅ Using Node.js 20 from Homebrew"
        elif [ -d "/usr/local/opt/node@20" ]; then
            export PATH="/usr/local/opt/node@20/bin:$PATH"
            echo "   ✅ Using Node.js 20 from Homebrew (Intel Mac)"
        else
            echo "   ❌ Node.js 20 not found. Run: ./fix_nodejs.sh"
            echo "   Or install manually: brew install node@20"
            exit 1
        fi
    elif [ -s "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh"
        nvm use 20 2>/dev/null || nvm install 20
    else
        echo "   ❌ Please run: ./fix_nodejs.sh"
        exit 1
    fi
fi

echo "   Using Node.js: $(node --version)"

# Clear Next.js cache to fix 404 issues
if [ -d ".next" ]; then
    echo "🧹 Clearing Next.js cache..."
    rm -rf .next
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend in background (explicitly on port 3000)
PORT=3000 npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ Frontend started on port 3000 (PID: $FRONTEND_PID)"
echo "   Logs: tail -f frontend.log"
echo "   ⏳ Wait 10-15 seconds for Next.js to compile routes..."
echo ""

# Wait a bit for servers to start
echo "⏳ Waiting for servers to start..."
sleep 5

# Check if servers are running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend failed to start. Check backend.log"
fi

if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend failed to start. Check frontend.log"
fi

echo ""
echo "🎉 Done! Access the app at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "To stop servers: ./stop.sh"
echo "To view logs: tail -f backend.log or tail -f frontend.log"

