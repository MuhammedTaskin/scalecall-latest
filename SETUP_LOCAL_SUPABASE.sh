#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🐳 TEKNOFEST 2025 - LOCAL SUPABASE SETUP 🐳              ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  100% Local, Open Source, NO CLOUD API!                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo -e "${YELLOW}📦 Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found! Please install Docker first.${NC}"
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed${NC}"

# Check Docker Compose
echo -e "${YELLOW}📦 Checking Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose installed${NC}"

# Option 1: Use our Docker Compose
echo ""
echo -e "${GREEN}🚀 OPTION 1: Quick Start with Our Docker Compose${NC}"
echo "============================================"
echo ""
echo "1. Start PostgreSQL and services:"
echo -e "${YELLOW}   docker-compose up -d postgres${NC}"
echo ""
echo "2. Wait for PostgreSQL to be ready:"
echo -e "${YELLOW}   docker-compose exec postgres pg_isready${NC}"
echo ""
echo "3. Initialize database schema:"
echo -e "${YELLOW}   docker-compose exec postgres psql -U postgres -d teknofest_telco -f /docker-entrypoint-initdb.d/01-schema.sql${NC}"
echo ""
echo "4. Test the system:"
echo -e "${YELLOW}   python3 LOCAL_TELCO_TOOLS.py${NC}"
echo ""

# Option 2: Official Supabase
echo -e "${GREEN}🚀 OPTION 2: Official Supabase Self-Hosted${NC}"
echo "============================================"
echo ""
echo "1. Clone Supabase repository:"
echo -e "${YELLOW}   git clone --depth 1 https://github.com/supabase/supabase${NC}"
echo -e "${YELLOW}   cd supabase/docker${NC}"
echo ""
echo "2. Copy and configure environment:"
echo -e "${YELLOW}   cp .env.example .env${NC}"
echo "   Edit .env and set:"
echo "   - POSTGRES_PASSWORD=teknofest2025"
echo "   - Generate JWT_SECRET with: openssl rand -hex 32"
echo ""
echo "3. Start Supabase:"
echo -e "${YELLOW}   docker compose up -d${NC}"
echo ""
echo "4. Access services:"
echo "   - Studio: http://localhost:3000"
echo "   - API: http://localhost:8000"
echo "   - PostgreSQL: localhost:5432"
echo ""

# Quick start script
echo -e "${GREEN}🎯 QUICK START SCRIPT${NC}"
echo "===================="
echo ""
echo "Run this to start everything:"
echo ""
cat << 'SCRIPT'
#!/bin/bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
sleep 5
docker-compose exec postgres pg_isready

# Create database and schema
docker-compose exec postgres psql -U postgres << SQL
CREATE DATABASE IF NOT EXISTS teknofest_telco;
\c teknofest_telco
\i /docker-entrypoint-initdb.d/01-schema.sql
SQL

# Test connection
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='teknofest_telco',
        user='postgres',
        password='teknofest2025secret'
    )
    print('✅ Database connected successfully!')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"

echo "✅ Setup complete! Run: python3 LOCAL_TELCO_TOOLS.py"
SCRIPT

echo ""
echo -e "${GREEN}📝 ENVIRONMENT VARIABLES${NC}"
echo "======================="
echo ""
echo "Add to your .env or export:"
echo ""
echo "export DB_HOST=localhost"
echo "export DB_PORT=5432"
echo "export DB_NAME=teknofest_telco"
echo "export DB_USER=postgres"
echo "export DB_PASSWORD=teknofest2025secret"
echo ""

echo -e "${GREEN}🔍 VERIFY INSTALLATION${NC}"
echo "===================="
echo ""
echo "1. Check Docker containers:"
echo -e "${YELLOW}   docker ps${NC}"
echo ""
echo "2. Test PostgreSQL connection:"
echo -e "${YELLOW}   docker exec teknofest-postgres pg_isready${NC}"
echo ""
echo "3. Access database:"
echo -e "${YELLOW}   docker exec -it teknofest-postgres psql -U postgres${NC}"
echo ""
echo "4. Run system test:"
echo -e "${YELLOW}   python3 LOCAL_TELCO_TOOLS.py${NC}"
echo ""

echo -e "${GREEN}📚 WHAT YOU GET${NC}"
echo "=============="
echo "✅ PostgreSQL 15 (Supabase optimized)"
echo "✅ 21 Telco Tools (fully implemented)"
echo "✅ Direct database access (no API limits)"
echo "✅ Complete schema with indexes"
echo "✅ RLS policies for security"
echo "✅ Mock mode fallback"
echo "✅ Docker health checks"
echo "✅ pgAdmin for visual management"
echo ""

echo -e "${GREEN}🏆 TEKNOFEST READY!${NC}"
echo "=================="
echo "Your system is 100% local, open source, and production ready!"
echo "NO cloud dependencies, NO API limits, FULL control!"
echo ""
echo "Good luck at TEKNOFEST 2025! 🚀"