#!/bin/bash

echo "🔍 Checking CL Monetizer Port Status..."
echo ""

# Check port 3000 (Frontend)
if lsof -i :3000 > /dev/null 2>&1; then
    PROCESS=$(lsof -i :3000 | tail -1 | awk '{print $1, $2, $9}')
    echo "✅ Port 3000: IN USE"
    echo "   Process: $PROCESS"
else
    echo "❌ Port 3000: FREE (Frontend not running)"
fi

# Check port 8000 (Backend)
if lsof -i :8000 > /dev/null 2>&1; then
    PROCESS=$(lsof -i :8000 | tail -1 | awk '{print $1, $2, $9}')
    echo "✅ Port 8000: IN USE"
    echo "   Process: $PROCESS"
else
    echo "❌ Port 8000: FREE (Backend not running)"
fi

# Check port 3001 (should be free)
if lsof -i :3001 > /dev/null 2>&1; then
    PROCESS=$(lsof -i :3001 | tail -1 | awk '{print $1, $2, $9}')
    echo "⚠️  Port 3001: IN USE (should be free)"
    echo "   Process: $PROCESS"
    echo "   This might cause Next.js to use a different port!"
else
    echo "✅ Port 3001: FREE"
fi

echo ""
echo "Expected configuration:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "To free ports: ./stop.sh"
echo "To start app:   ./restart.sh"

