#!/bin/bash

echo "🔧 Fixing 404 errors on dashboard routes..."

# Stop frontend
echo "📛 Stopping frontend..."
pkill -f "next dev" || true
sleep 2

# Clear Next.js cache
echo "🧹 Clearing Next.js cache..."
cd frontend
rm -rf .next
echo "✅ Cache cleared"

# Check Node.js version
echo "🔍 Checking Node.js version..."
if command -v brew &> /dev/null && brew list --versions node@20 &> /dev/null; then
    echo "✅ Using Node.js 20 from Homebrew..."
    export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
else
    echo "⚠️  Node.js 20 not found via Homebrew. Ensure Node.js >=20.9.0 is in your PATH."
fi

# Restart frontend
echo "🚀 Restarting frontend..."
cd ..
npm --prefix frontend run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started with PID: $FRONTEND_PID"

echo ""
echo "⏳ Waiting 20 seconds for Next.js to compile all routes..."
sleep 20

echo ""
echo "🧪 Testing routes..."
BASE_URL="http://localhost:3000"

ROUTES=(
    "/dashboard/listings"
    "/dashboard/leads"
    "/dashboard/settings"
)

for route in "${ROUTES[@]}"; do
    STATUS_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" "$BASE_URL$route" 2>/dev/null || echo "000")
    if [ "$STATUS_CODE" == "200" ]; then
        echo "✅ $route - OK"
    else
        echo "❌ $route - HTTP $STATUS_CODE"
    fi
done

echo ""
echo "✅ Fix complete! If routes still show 404, wait another 10-20 seconds for compilation."
echo "   Check frontend.log for any errors: tail -f frontend.log"
