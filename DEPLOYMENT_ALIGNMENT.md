# Deployment Alignment Checklist

## Current Issues Identified:

1. **Data Sources Mismatch**
   - Local: Shows 4 data sources (2 default + 2 custom)
   - Production: Shows only 2 data sources
   - Root cause: Production backend may not have the updated `data_sources.json`

2. **Frontend HTML Hardcoding**
   - Fixed locally: Now loads data sources dynamically
   - Need to deploy: Frontend changes to production

3. **Backend Data Persistence**
   - Local: Uses `backend/data_sources.json`
   - Production (Render): File system is ephemeral, data doesn't persist

## Action Plan:

### 1. Immediate Fixes:

#### Frontend Deployment:
```bash
# Commit and push frontend changes
git add frontend/index.html
git commit -m "Fix: Load data sources dynamically instead of hardcoded values"
git push origin main

# Vercel will auto-deploy from main branch
```

#### Backend Data Persistence:
- **Problem**: Render's filesystem is ephemeral
- **Solution**: Need to implement persistent storage (database or external file storage)
- **Temporary Fix**: Include data_sources.json in git and redeploy

### 2. Architecture Alignment:

#### Local Development:
```
Frontend (localhost:3000) --> Backend (localhost:8000)
                                    |
                                    v
                          Local file: backend/data_sources.json
```

#### Production:
```
Frontend (qanda-user-gpt.com) --> Backend (Render)
                                       |
                                       v
                             Need persistent storage solution
```

### 3. Deployment Commands:

#### Backend (Render):
```bash
# Backend changes are auto-deployed when pushed to main
git add backend/
git commit -m "Update: Include data sources in deployment"
git push origin main
```

#### Frontend (Vercel):
```bash
# Frontend is auto-deployed from main branch
# Ensure vercel.json is configured correctly
```

### 4. Environment Variables Check:

#### Backend (.env):
- ANTHROPIC_API_KEY
- GOOGLE_API_KEY
- GOOGLE_SEARCH_API_KEY
- GOOGLE_SEARCH_ENGINE_ID

#### Production (Render Dashboard):
- Ensure all environment variables are set

### 5. Testing Checklist:

- [ ] Local frontend loads all 4 data sources
- [ ] Local backend API returns all 4 sources
- [ ] Production frontend receives dynamic data
- [ ] Production backend persists custom data sources
- [ ] Chat functionality works with all data sources

## Recommended Long-term Solutions:

1. **Database Integration**: Use PostgreSQL or MongoDB for data persistence
2. **Redis Cache**: For session management and temporary data
3. **CI/CD Pipeline**: Automated testing before deployment
4. **Monitoring**: Add logging and monitoring for production issues
