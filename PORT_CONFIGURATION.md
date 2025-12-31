# Port Configuration Guide

## Standard Ports

The CL Monetizer app is configured to **always** use these ports:

- **Frontend**: Port `3000` (http://localhost:3000)
- **Backend**: Port `8000` (http://localhost:8000)

## How Ports Are Enforced

### Frontend (Next.js)
1. **package.json** script: `"dev": "next dev -p 3000"`
2. **restart.sh** sets: `PORT=3000 npm run dev`
3. **stop.sh** kills any process on port 3000 or 3001

### Backend (FastAPI/Uvicorn)
1. **restart.sh** explicitly sets: `--port 8000`
2. **stop.sh** kills any process on port 8000

## Checking Port Status

Run:
```bash
./check_ports.sh
```

This will show:
- Which ports are in use
- What processes are using them
- Expected configuration

## Freeing Ports

If ports are blocked by other processes:

```bash
./stop.sh
```

This will:
- Kill all CL Monetizer processes
- Force-kill any process on ports 3000, 3001, and 8000

## Starting the App

```bash
./restart.sh
```

This will:
1. Free ports 3000 and 8000
2. Start backend on port 8000
3. Start frontend on port 3000 (never 3001)

## Troubleshooting

### Frontend on Port 3001 Instead of 3000

**Cause**: Another process is using port 3000 (often Docker or another Next.js instance)

**Fix**:
```bash
./stop.sh  # This will free port 3000
./restart.sh  # Restart the app
```

### Backend Not Starting

**Check**:
```bash
tail -f backend.log
```

**Common issues**:
- Port 8000 already in use: Run `./stop.sh`
- Virtual environment not activated: `restart.sh` handles this automatically

### Port Still Blocked After stop.sh

Manually kill the process:
```bash
# Find what's using the port
lsof -i :3000
lsof -i :8000

# Kill it (replace PID with actual process ID)
kill -9 <PID>
```

## Environment Variables

You can override ports using environment variables (not recommended):

```bash
# Frontend
PORT=3000 npm run dev

# Backend
uvicorn app.main:app --port 8000
```

But the scripts handle this automatically, so you shouldn't need to set these manually.

## Verification

After starting, verify ports:
```bash
./check_ports.sh
```

Expected output:
```
✅ Port 3000: IN USE (Frontend)
✅ Port 8000: IN USE (Backend)
✅ Port 3001: FREE
```

