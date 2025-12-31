#!/bin/bash

echo "🧪 Testing CL Monetizer Routes..."
echo ""

BASE_URL="http://localhost:3000"
API_URL="http://localhost:8000"

# Test API
echo "📡 Testing Backend API..."
if curl -s "$API_URL/health" > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend is NOT running. Start it with: cd backend && uvicorn app.main:app --reload"
    exit 1
fi

# Test Frontend
echo ""
echo "🌐 Testing Frontend Routes..."
routes=(
    "/"
    "/dashboard"
    "/dashboard/listings"
    "/dashboard/leads"
    "/dashboard/scraper"
    "/dashboard/settings"
)

for route in "${routes[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$route")
    if [ "$status" = "200" ]; then
        echo "✅ $route - OK"
    else
        echo "❌ $route - HTTP $status"
    fi
done

echo ""
echo "📊 Testing API Endpoints..."
api_routes=(
    "/health"
    "/api/stats"
    "/api/listings/count"
    "/api/listings?limit=1"
)

for route in "${api_routes[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$route")
    if [ "$status" = "200" ]; then
        echo "✅ $route - OK"
    else
        echo "❌ $route - HTTP $status"
    fi
done

echo ""
echo "✅ Testing complete!"

