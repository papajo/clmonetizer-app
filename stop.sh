#!/bin/bash

echo "🛑 Stopping CL Monetizer services..."

echo "Stopping backend (uvicorn on port 8000)..."
pkill -f "uvicorn.*app.main:app" 2>/dev/null
lsof -ti :8000 | xargs kill -9 2>/dev/null || true

echo "Stopping frontend (next dev on port 3000)..."
pkill -f "next dev" 2>/dev/null
pkill -f "next start" 2>/dev/null
lsof -ti :3000 | xargs kill -9 2>/dev/null || true
lsof -ti :3001 | xargs kill -9 2>/dev/null || true

echo "✅ All services stopped."
echo "   Ports 3000 and 8000 are now free."
