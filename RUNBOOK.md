# 🚀 Scalecall Runbook: Local Development & Testing

## 📋 Quick Setup Checklist

### 1. Prerequisites
- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed  
- [ ] Supabase account created
- [ ] Google Gemini API key obtained

### 2. Environment Setup
```bash
# Clone and setup
git clone https://github.com/MuhammedTaskin/scalecall-latest.git
cd scalecall-latest

# Copy environment files
cp env.example .env
cp frontend/env.example frontend/.env.local

# Edit .env with your credentials
nano .env  # Add your Supabase and Gemini keys
nano frontend/.env.local  # Add frontend Supabase config
```

### 3. Database Setup
```bash
# Option A: Supabase CLI (recommended)
npx supabase init
npx supabase link --project-ref YOUR_PROJECT_REF
npx supabase db push

# Option B: Manual SQL execution
# Copy/paste SQL from supabase/migrations/20240112000001_init_profiles_and_messages.sql
# into your Supabase SQL editor and run
```

### 4. Install Dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend  
cd frontend && npm install
cd ..
```

### 5. Start Services
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

## 🧪 Testing Commands

### Run All Tests
```bash
cd backend && python -m pytest tests/ -v
```

### Test Specific Components
```bash
# Authentication tests
pytest tests/test_auth_and_llm.py::TestAuthentication -v

# LLM endpoint tests  
pytest tests/test_auth_and_llm.py::TestLLMEndpoints -v

# RLS policy tests
pytest tests/test_auth_and_llm.py::TestRLSPolicies -v
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8000/health

# Test unauthenticated request (should fail)
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# Test with authentication (need to get JWT from frontend first)
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"messages": [{"role": "user", "content": "Merhaba"}], "stream": false}'
```

## 🔍 Debugging Guide

### Common Issues

#### 1. Supabase Connection Failed
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY

# Test connection
python -c "from backend.lib.supabase_client import supabase_client; print(supabase_client)"
```

#### 2. Gemini API Key Invalid
```bash
# Check API key
echo $GEMINI_API_KEY

# Test Gemini connection
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')
print('Gemini connection successful')
"
```

#### 3. Frontend Not Loading
```bash
# Check frontend environment
cd frontend && cat .env.local

# Restart dev server
npm run dev
```

#### 4. Authentication Issues
```bash
# Check JWT secret
echo $SUPABASE_JWT_SECRET

# Verify RLS policies in Supabase dashboard
# Go to: Database > Authentication > Policies
```

### Log Files
```bash
# Backend logs
tail -f backend.log  # if running with log file

# Frontend logs  
# Check browser console for errors

# Supabase logs
# Check Supabase dashboard > Logs
```

## 🎯 Sample API Calls

### 1. Get JWT Token (via Frontend)
1. Open http://localhost:5173
2. Sign up/login with email
3. Open browser dev tools > Application > Local Storage
4. Find `sb-YOUR_PROJECT_REF-auth-token`
5. Copy the `access_token` value

### 2. Test LLM Chat (Non-streaming)
```bash
export JWT_TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "messages": [
      {"role": "user", "content": "Merhaba, eSIM almak istiyorum"}
    ],
    "stream": false
  }'
```

### 3. Test LLM Chat (Streaming)
```bash
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "messages": [
      {"role": "user", "content": "eSIM paketlerinizi gösterebilir misiniz?"}
    ],
    "stream": true
  }'
```

### 4. Get Message History
```bash
curl -H "Authorization: Bearer $JWT_TOKEN" \
  http://localhost:8000/api/llm/messages?limit=10
```

### 5. Clear Message History
```bash
curl -X DELETE \
  -H "Authorization: Bearer $JWT_TOKEN" \
  http://localhost:8000/api/llm/messages
```

## 📊 Performance Testing

### Rate Limiting Test
```bash
# Test rate limiting (should fail after 10 requests)
for i in {1..12}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/api/llm/chat \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -d '{"messages": [{"role": "user", "content": "test"}], "stream": false}' \
    -w "Status: %{http_code}\n" -s -o /dev/null
done
```

### Load Testing
```bash
# Install apache bench
# brew install httpd (macOS)

# Test with multiple concurrent requests
ab -n 100 -c 10 -H "Authorization: Bearer $JWT_TOKEN" \
  -p test_payload.json -T application/json \
  http://localhost:8000/api/llm/chat
```

## 🔄 Development Workflow

### 1. Make Changes
```bash
# Backend changes
# Edit files in backend/
# Server auto-reloads with --reload flag

# Frontend changes  
# Edit files in frontend/src/
# Vite auto-reloads
```

### 2. Test Changes
```bash
# Run specific tests
pytest tests/test_auth_and_llm.py::TestAuthentication::test_valid_jwt_token -v

# Test in browser
# Open http://localhost:5173
# Sign in and test functionality
```

### 3. Commit Changes
```bash
git add .
git commit -m "Your descriptive commit message"
```

## 🚨 Emergency Procedures

### Rollback to Previous Version
```bash
# If new version has issues
git log --oneline  # Find previous commit
git checkout PREVIOUS_COMMIT_HASH
pip install -r requirements.txt
cd frontend && npm install && cd ..
# Restart services
```

### Reset Database
```bash
# In Supabase dashboard
# Go to Settings > Database > Reset database
# Then re-run migrations:
npx supabase db push
```

### Clear Rate Limits
```python
# In Python console
from backend.api.llm import rate_limit_store
rate_limit_store.clear()
print("Rate limits cleared")
```

## 📞 Support & Resources

### Documentation
- **Supabase Docs**: https://supabase.com/docs
- **Google Gemini Docs**: https://ai.google.dev/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

### Troubleshooting
- Check `MIGRATION_GUIDE.md` for detailed changes
- Review `README.md` for setup instructions
- Check Supabase dashboard for database issues
- Monitor backend logs for API errors

### Environment Variables Reference
```bash
# Backend (.env)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret
GEMINI_API_KEY=AI...

# Frontend (.env.local)  
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_API_URL=http://localhost:8000
```

---

**Happy coding! 🎉**

For issues or questions, check the logs, test endpoints manually, and verify environment configuration first.
