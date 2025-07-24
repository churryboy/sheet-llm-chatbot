# Cache Clearing Instructions

## 1. Browser Cache Clearing

### Chrome/Edge
1. Open Developer Tools (F12 or Cmd+Option+I on Mac)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

OR

1. Press Cmd+Shift+Delete (Mac) or Ctrl+Shift+Delete (Windows)
2. Select "Cached images and files"
3. Choose time range "All time"
4. Click "Clear data"

### Safari
1. Enable Developer menu: Safari → Preferences → Advanced → Show Develop menu
2. Develop → Empty Caches
3. Cmd+Option+R for hard refresh

### Firefox
1. Cmd+Shift+Delete (Mac) or Ctrl+Shift+Delete (Windows)
2. Select "Cache"
3. Choose time range "Everything"
4. Click "Clear Now"

## 2. Test if Cache is Cleared

Run this command to test the API directly:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Cache-Control: no-cache" \
  -d '{"question": "중학생은 몇명이야"}' | jq .
```

## 3. Frontend Cache Clearing

If using React/Next.js frontend:
1. Stop the development server (Ctrl+C)
2. Delete `.next` folder (for Next.js) or `build` folder
3. Clear node_modules/.cache if exists
4. Restart the development server

```bash
# For Next.js
rm -rf .next
rm -rf node_modules/.cache

# For Create React App
rm -rf build
rm -rf node_modules/.cache
```

## 4. Service Worker Cache

If your app uses service workers:
1. Open Developer Tools
2. Go to Application tab
3. Click "Storage" → "Clear site data"
4. OR in Application → Service Workers → Unregister all

## 5. DNS Cache (if needed)

```bash
# macOS
sudo dscacheutil -flushcache

# Windows (run as admin)
ipconfig /flushdns
```

## 6. Test with Different Methods

### Direct API Test (bypasses all browser cache):
```bash
# Test with timestamp to ensure fresh request
curl -X POST "http://localhost:8000/api/chat?t=$(date +%s)" \
  -H "Content-Type: application/json" \
  -H "Cache-Control: no-cache, no-store, must-revalidate" \
  -H "Pragma: no-cache" \
  -d '{"question": "중학생은 몇명이야"}' | jq .
```

### Test in Incognito/Private Mode
- Chrome: Cmd+Shift+N (Mac) or Ctrl+Shift+N (Windows)
- Safari: Cmd+Shift+N
- Firefox: Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)

## 7. Verify Backend is Updated

Check that the backend is running the latest code:
```bash
# Check if server is running
lsof -i :8000

# Check server logs
tail -f server.log

# Restart server to ensure latest code
pkill -f "python app.py"
python app.py > server.log 2>&1 &
```
