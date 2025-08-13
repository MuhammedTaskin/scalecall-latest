# 🔄 Migration Guide: MLX Gemma → Supabase + Google Gemini 2.5 Flash

This document outlines the changes made to migrate from the original MLX-based local LLM to a modern Supabase + Google Gemini architecture.

## 📋 Summary of Changes

### 🗄️ **Database Migration**
- **From**: SQLite with SQLAlchemy
- **To**: Supabase PostgreSQL with Row Level Security (RLS)
- **New Tables**: `profiles`, `messages` with proper RLS policies
- **Authentication**: Integrated Supabase Auth

### 🤖 **LLM Provider Migration**
- **From**: MLX Gemma-3 4B (local, on-device)
- **To**: Google Gemini 2.5 Flash (cloud API, server-side only)
- **Benefits**: Better performance, no local model requirements, streaming support

### 🔐 **Security Enhancements**
- **Authentication**: JWT-based auth with Supabase
- **Authorization**: Row Level Security ensures user data isolation
- **API Security**: Rate limiting, input validation, server-side key management
- **Privacy**: All API keys kept server-side, no client exposure

## 🚀 **New Features Added**

### Frontend Enhancements
- **Auth Components**: Login/signup with email/password or magic links
- **Auth Context**: React context for managing user state
- **API Hooks**: Custom hooks for authenticated API calls
- **Streaming Chat**: Real-time LLM responses with Server-Sent Events

### Backend Enhancements
- **LLM Abstraction**: Provider-agnostic LLM interface
- **Secure API Endpoints**: `/api/llm/chat`, `/api/llm/messages` with auth
- **Rate Limiting**: In-memory rate limiting (10 req/min per user)
- **Message Persistence**: Chat history stored in Supabase

### DevOps & Testing
- **Environment Management**: Separate configs for dev/prod
- **Comprehensive Tests**: Auth, RLS, and LLM endpoint testing
- **Migration Scripts**: SQL migrations for database setup

## 📁 **File Changes**

### New Files
```
backend/lib/supabase_client.py     # Supabase client setup
backend/llm/index.py               # LLM provider abstraction
backend/api/llm.py                 # Secure LLM API endpoints
backend/auth.py                    # JWT authentication middleware
backend/tests/test_auth_and_llm.py # Comprehensive test suite

frontend/src/lib/supabaseClient.ts # Frontend Supabase client
frontend/src/lib/database.types.ts # TypeScript database types
frontend/src/contexts/AuthContext.tsx # React auth context
frontend/src/hooks/useApi.ts       # API hooks for authenticated requests
frontend/src/components/Auth.tsx   # Authentication UI component

supabase/migrations/20240112000001_init_profiles_and_messages.sql # Database migration

env.example                        # Environment configuration template
frontend/env.example               # Frontend environment template
MIGRATION_GUIDE.md                 # This file
```

### Modified Files
```
requirements.txt                   # Added Supabase, Gemini, testing deps
frontend/package.json             # Added Supabase client, Zod
backend/app.py                    # Added LLM API routes, env loading
backend/orchestrator.py           # Updated to use new LLM provider
README.md                         # Updated with new setup instructions
```

### Removed Dependencies
```
mlx==0.0.8                        # Local MLX framework
mlx-lm==0.0.8                     # MLX language models
```

## 🔧 **Environment Variables**

### Backend (.env)
```bash
# Supabase
SUPABASE_URL=your_project_url
SUPABASE_ANON_KEY=your_anon_key  
SUPABASE_SERVICE_ROLE_KEY=your_service_key
SUPABASE_JWT_SECRET=your_jwt_secret

# Google Gemini (server-side only)
GEMINI_API_KEY=your_gemini_key

# Optional
LLM_PROVIDER=gemini  # or 'mock' for testing
```

### Frontend (.env.local)
```bash
# Supabase (client-side safe)
VITE_SUPABASE_URL=your_project_url
VITE_SUPABASE_ANON_KEY=your_anon_key

# API
VITE_API_URL=http://localhost:8000
```

## 🧪 **Testing Strategy**

### Authentication Tests
- JWT token validation (valid, expired, malformed)
- User authorization and data isolation
- Rate limiting enforcement

### LLM Endpoint Tests  
- Authenticated API access
- Message persistence in database
- Streaming response handling
- Error handling and fallbacks

### RLS Policy Tests
- Database-level user isolation
- Policy enforcement on all operations
- Migration script validation

## 🔄 **Migration Steps for Production**

1. **Setup Supabase Project**
   ```bash
   # Create new Supabase project
   # Copy connection details to .env
   ```

2. **Run Database Migrations**
   ```bash
   # Option 1: Supabase CLI
   npx supabase db push
   
   # Option 2: Manual SQL execution
   # Run migration SQL in Supabase dashboard
   ```

3. **Configure API Keys**
   ```bash
   # Get Google Gemini API key from AI Studio
   # Update environment variables
   ```

4. **Deploy Backend**
   ```bash
   # Update requirements and restart server
   pip install -r requirements.txt
   ```

5. **Deploy Frontend** 
   ```bash
   # Update dependencies and rebuild
   npm install && npm run build
   ```

6. **Verify Migration**
   ```bash
   # Run test suite
   pytest backend/tests/ -v
   
   # Test authentication flow
   # Verify LLM responses
   # Check database isolation
   ```

## 🔍 **Backwards Compatibility**

### Preserved APIs
- WebSocket interface remains the same
- Voice processing (STT/TTS) unchanged  
- Tool calling and persona handoff logic preserved
- Frontend component interfaces maintained

### Breaking Changes
- **Authentication Required**: All LLM endpoints now require valid JWT
- **Database Schema**: New Supabase tables replace SQLite
- **Environment Setup**: Additional configuration required
- **Dependencies**: MLX dependencies removed

## 🆘 **Rollback Strategy**

If needed, you can rollback by:

1. **Restore MLX Dependencies**
   ```bash
   pip install mlx==0.0.8 mlx-lm==0.0.8
   ```

2. **Revert LLM Provider**
   ```python
   # In backend/orchestrator.py
   from backend.llm_abi import LLMProvider  # Old import
   ```

3. **Use Local Database**
   ```python
   # Comment out Supabase imports
   # Use original SQLite setup
   ```

4. **Remove Auth Requirements**
   ```python
   # Remove auth dependencies from API routes
   # Restore anonymous access
   ```

## 🎯 **Next Steps**

### Recommended Improvements
- [ ] **Streaming WebSocket Integration**: Merge new LLM streaming with existing WS
- [ ] **Advanced Rate Limiting**: Redis-based distributed rate limiting
- [ ] **Observability**: Add metrics and monitoring with Supabase Analytics
- [ ] **Multi-model Support**: Easy switching between Gemini models
- [ ] **Conversation Management**: Thread-based chat organization
- [ ] **Deployment**: Docker containers and production deployment guides

### Performance Optimizations
- [ ] **Connection Pooling**: Optimize Supabase connection management
- [ ] **Caching**: Add response caching for common queries
- [ ] **Batch Operations**: Optimize message storage operations
- [ ] **CDN Integration**: Static asset optimization

---

**Migration completed successfully! 🎉**

The system now provides:
- ✅ Enterprise-grade security with RLS
- ✅ Scalable cloud-based LLM processing  
- ✅ Modern authentication system
- ✅ Comprehensive test coverage
- ✅ Production-ready architecture
