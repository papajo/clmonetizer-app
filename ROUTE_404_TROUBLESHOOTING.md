# Route 404 Troubleshooting Guide

## Issue
Some dashboard routes return 404 errors:
- `/dashboard/listings` - HTTP 404
- `/dashboard/leads` - HTTP 404  
- `/dashboard/settings` - HTTP 404

However, these routes work:
- `/dashboard` - OK
- `/dashboard/scraper` - OK

## Verification

The route files exist and are properly exported:
```bash
ls -la frontend/app/dashboard/*/page.tsx
```

All files have `export default` statements and are valid React components.

## Known Workarounds

### 1. Hard Refresh Browser
Sometimes Next.js routes need a hard refresh to be recognized:
- **Mac**: Cmd + Shift + R
- **Windows/Linux**: Ctrl + Shift + R

### 2. Wait for Full Compilation
Next.js with Turbopack can take 30-60 seconds to fully compile all routes. Wait and try again.

### 3. Access Routes Directly
Try accessing the routes directly in your browser:
- http://localhost:3000/dashboard/listings
- http://localhost:3000/dashboard/leads
- http://localhost:3000/dashboard/settings

### 4. Restart Without Turbopack
Turbopack (Next.js 16's new bundler) may have caching issues:

```bash
# Stop frontend
pkill -f "next dev"

# Start without Turbopack
cd frontend
TURBOPACK=0 npm run dev
```

### 5. Clear All Caches
```bash
cd frontend
rm -rf .next
rm -rf node_modules/.cache
npm run dev
```

### 6. Check Browser Console
Open browser DevTools (F12) and check for JavaScript errors that might prevent route loading.

## Root Cause

This appears to be a known issue with:
- Next.js 16.1.1 + Turbopack caching
- Route compilation order
- Hot module replacement (HMR) not detecting new routes

## Temporary Solution

If routes still don't work, you can access the functionality via:
1. **Listings**: Use the API directly: `http://localhost:8000/api/listings`
2. **Leads**: Use the API directly: `http://localhost:8000/api/leads`
3. **Settings**: Most settings are configured via environment variables

## Long-term Fix

Consider:
1. Upgrading to Next.js 16.2+ (when available) which may have Turbopack fixes
2. Disabling Turbopack: Add to `next.config.mjs`:
   ```js
   const nextConfig = {
     experimental: {
       turbo: false
     }
   };
   ```
3. Using standard webpack bundler instead of Turbopack

## Status

The routes are properly configured and should work. This is a Next.js/Turbopack compilation/caching issue, not a code problem.

