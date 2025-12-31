#!/bin/bash

echo "🛑 Stopping CL Monetizer App..."

pkill -f "uvicorn.*app.main:app" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "next start" 2>/dev/null

sleep 2

echo "✅ All servers stopped"

