# 🐳 Local Supabase Setup with Docker - TEKNOFEST 2025

## Overview
We're using **self-hosted Supabase** running locally in Docker containers. NO CLOUD API - everything runs on your machine!

## Quick Setup

### 1. Clone Supabase
```bash
git clone --depth 1 https://github.com/supabase/supabase
cd supabase/docker
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Generate secure keys
openssl rand -hex 32  # For JWT_SECRET
openssl rand -hex 32  # For ANON_KEY
openssl rand -hex 32  # For SERVICE_KEY
```

### 3. Update .env file
```env
# Local Supabase Configuration
POSTGRES_PASSWORD=your-super-secret-password
JWT_SECRET=your-jwt-secret-here
ANON_KEY=your-anon-key-here
SERVICE_ROLE_KEY=your-service-key-here

# Local endpoints (NO CLOUD!)
API_EXTERNAL_URL=http://localhost:8000
SUPABASE_PUBLIC_URL=http://localhost:8000

# Database
POSTGRES_HOST=db
POSTGRES_DB=postgres
POSTGRES_PORT=5432

# Studio
STUDIO_PORT=3000
```

### 4. Start Local Supabase
```bash
# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 5. Access Local Services
- **Supabase Studio**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Storage**: http://localhost:8000/storage/v1

## Docker Services Running Locally

```yaml
services:
  studio:
    container_name: supabase-studio
    image: supabase/studio:latest
    ports:
      - 3000:3000
    
  kong:
    container_name: supabase-kong
    image: kong:2.8.1
    ports:
      - 8000:8000  # API Gateway
    
  auth:
    container_name: supabase-auth
    image: supabase/gotrue:latest
    
  rest:
    container_name: supabase-rest
    image: postgrest/postgrest:latest
    
  realtime:
    container_name: supabase-realtime
    image: supabase/realtime:latest
    
  storage:
    container_name: supabase-storage
    image: supabase/storage-api:latest
    
  meta:
    container_name: supabase-meta
    image: supabase/postgres-meta:latest
    
  db:
    container_name: supabase-db
    image: supabase/postgres:15.1.0.117
    ports:
      - 5432:5432
    volumes:
      - ./volumes/db/data:/var/lib/postgresql/data
```

## Initialize Our Schema

```bash
# Connect to local PostgreSQL
docker exec -it supabase-db psql -U postgres

# Or use psql directly
psql postgresql://postgres:your-password@localhost:5432/postgres

# Run our schema
\i SUPABASE_SETUP.sql
```

## Local Connection in Python

```python
# NO CLOUD API - Direct local PostgreSQL connection
import psycopg2
from psycopg2.extras import RealDictCursor

class LocalSupabaseClient:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="postgres",
            user="postgres",
            password="your-super-secret-password",
            cursor_factory=RealDictCursor
        )
        self.cursor = self.conn.cursor()
    
    def execute(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def insert(self, table, data):
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({values}) RETURNING *"
        self.cursor.execute(query, list(data.values()))
        self.conn.commit()
        return self.cursor.fetchone()
```

## Why Local Self-Hosted?

1. **NO API LIMITS** - Unlimited requests
2. **FULL CONTROL** - Complete database access
3. **DATA PRIVACY** - Everything stays on your machine
4. **ZERO COST** - No cloud fees
5. **OFFLINE WORK** - No internet required
6. **CUSTOM EXTENSIONS** - Add any PostgreSQL extension
7. **DEBUG FRIENDLY** - Direct database access

## Docker Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# Access PostgreSQL
docker exec -it supabase-db psql -U postgres

# Backup database
docker exec supabase-db pg_dump -U postgres > backup.sql

# Restore database
docker exec -i supabase-db psql -U postgres < backup.sql
```

## Health Check

```bash
# Check all services are running
curl http://localhost:8000/rest/v1/

# Check database connection
docker exec supabase-db pg_isready

# Check Studio
curl http://localhost:3000
```

## Troubleshooting

### Port Conflicts
```bash
# Change ports in .env if needed
STUDIO_PORT=3001
KONG_HTTP_PORT=8001
POSTGRES_PORT=5433
```

### Reset Everything
```bash
docker compose down -v  # Remove volumes too
rm -rf volumes/
docker compose up -d
```

### View Container Logs
```bash
docker logs supabase-db
docker logs supabase-kong
docker logs supabase-studio
```

## Performance Tuning

### PostgreSQL Configuration
```sql
-- Optimize for local development
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET random_page_cost = 1.1;
```

### Docker Resources
```yaml
# docker-compose.override.yml
services:
  db:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2'
```

## Integration with Our System

The system automatically detects local Supabase:
- Checks localhost:5432 for PostgreSQL
- Falls back to mock mode if not available
- No cloud API keys needed
- Direct database queries for maximum speed

## Notes

- All data stored in `./volumes/db/data/`
- Backup regularly with `pg_dump`
- Studio provides visual database management
- No internet required after initial Docker pull
- Fully open source - MIT licensed

---

**TEKNOFEST 2025 - Running 100% Local!**