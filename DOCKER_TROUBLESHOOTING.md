# 🔧 Docker Build Issues - Quick Fix

If you're seeing Docker build errors, here's how to fix them:

## Quick Fix (Use This!)

```bash
chmod +x fix.sh
./fix.sh
```

This script will:
1. Stop all services
2. Check and create missing files
3. Rebuild everything
4. Download AI model
5. Start BMO

## Manual Fix

If the script doesn't work, do this:

### 1. Stop Everything
```bash
cd bmo-assistant
docker-compose down
```

### 2. Check Files Exist

Make sure these files exist:
```bash
ls frontend/web/Dockerfile
ls frontend/web/public/index.html
ls frontend/web/src/index.js
ls .env
```

If any are missing, the archive may be incomplete.

### 3. Create .env File
```bash
cp .env.example .env
echo "OLLAMA_MODEL=llama3.2:1b" >> .env
```

### 4. Rebuild Services
```bash
docker-compose up -d --build
```

### 5. Wait for Services
```bash
# Wait 30 seconds
sleep 30
```

### 6. Download Model
```bash
docker exec -it bmo-ollama ollama pull llama3.2:1b
```

### 7. Restart AI Service
```bash
docker-compose restart ai-service
```

### 8. Check Status
```bash
docker-compose ps
curl http://localhost:8000/health
```

## Common Errors

### "no such file or directory"
**Problem:** Missing Dockerfile or source files
**Fix:** Re-extract the archive or download fresh copy

### "version is obsolete"
**Not an error!** Just a warning, ignore it.

### "Cannot connect to Docker daemon"
**Problem:** Docker isn't running
**Fix:** Start Docker Desktop or Docker service

### "port is already allocated"
**Problem:** Another service using the port
**Fix:** 
```bash
# Find what's using port 3000
lsof -i :3000
# Or use different port in docker-compose.yml
```

### "permission denied"
**Problem:** Scripts not executable
**Fix:**
```bash
chmod +x start.sh fix.sh
```

## Voice Service Disabled?

This is **normal** if you don't have Google Cloud credentials!

BMO works fine without voice. To enable voice later:

1. Get credentials from Google Cloud
2. Save as `credentials.json`
3. Uncomment voice-service in `docker-compose.yml`
4. Run: `docker-compose up -d --build`

## Still Having Issues?

### Check Docker
```bash
docker --version
docker-compose --version
docker ps
```

### Check Logs
```bash
docker-compose logs
# Or specific service:
docker-compose logs ai-service
docker-compose logs ollama
docker-compose logs gateway
```

### Nuclear Option (Fresh Start)
```bash
docker-compose down -v
docker system prune -f
rm -rf frontend/web/node_modules
./start.sh
```

## Need Fresh Download?

If files are corrupted or missing, download fresh:
1. Delete current folder
2. Extract archive again
3. Run `./fix.sh`

## Services Status

### Essential Services:
- ✅ **ollama** - Must be running
- ✅ **ai-service** - Must be running  
- ✅ **gateway** - Must be running
- ✅ **web** - Must be running
- ✅ **redis** - Must be running
- ✅ **task-service** - Must be running

### Optional Services:
- ⚠️ **voice-service** - Disabled by default (needs Google credentials)

## Success Looks Like

```bash
$ docker-compose ps

NAME           STATUS
bmo-ai         Up
bmo-gateway    Up
bmo-ollama     Up
bmo-redis      Up
bmo-task       Up
bmo-web        Up
```

Then:
- http://localhost:3000 shows BMO
- http://localhost:8000/health shows all services healthy

## Get Help

If none of this works:
1. Check you extracted the full archive
2. Check Docker has enough resources (4GB+ RAM)
3. Check disk space (10GB+ free)
4. Try `./fix.sh` script
5. Check logs with `docker-compose logs`
