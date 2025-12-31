#!/bin/bash

echo "🔧 Fixing 404 Errors on Frontend Routes..."
echo ""

cd frontend

# Check Node.js version
NODE_VERSION=$(node --version 2>/dev/null | cut -d'v' -f2 | cut -d'.' -f1)
if [ -z "$NODE_VERSION" ] || [ "$NODE_VERSION" -lt 20 ]; then
    echo "⚠️  Using Node.js 20..."
    if [ -d "/opt/homebrew/opt/node@20" ]; then
        export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
    elif [ -d "/usr/local/opt/node@20" ]; then
        export PATH="/usr/local/opt/node@20/bin:$PATH"
    fi
fi

echo "1. Stopping frontend server..."
pkill -f "next dev" 2>/dev/null
sleep 2

echo "2. Clearing Next.js cache..."
rm -rf .next
echo "   ✅ Cache cleared"

echo "3. Verifying route files exist..."
if [ -f "app/dashboard/listings/page.tsx" ] && [ -f "app/dashboard/leads/page.tsx" ] && [ -f "app/dashboard/settings/page.tsx" ]; then
    echo "   ✅ All route files found"
else
    echo "   ❌ Some route files missing!"
    exit 1
fi

echo ""
echo "4. Restarting frontend server..."
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✅ Frontend restarted (PID: $FRONTEND_PID)"
echo ""
echo "⏳ Wait 15-20 seconds for Next.js to compile all routes..."
echo "Then test: ./test_routes.sh"
echo ""
echo "If still getting 404s:"
echo "1. Check frontend.log for errors: tail -f frontend.log"
echo "2. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)"
echo "3. Check browser console (F12) for errors"

cd ..

