#!/bin/bash
# ══════════════════════════════════════════════════════════
# Q-School AI — Database Initialization Script
# Tự động chạy khi PostgreSQL container khởi tạo lần đầu.
# Script này được mount vào /docker-entrypoint-initdb.d/
# ══════════════════════════════════════════════════════════

set -e

echo "=== Q-School DB Init: Enabling required extensions ==="
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Enable pgvector extension cho vector search (RAG)
    CREATE EXTENSION IF NOT EXISTS vector;
    
    -- Enable uuid-ossp (backup cho gen_random_uuid)
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Enable pgcrypto (provides gen_random_uuid() used by Alembic migrations)
    CREATE EXTENSION IF NOT EXISTS "pgcrypto";
    
    -- Verify extensions
    SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'uuid-ossp', 'pgcrypto');
EOSQL

echo "=== Q-School DB Init: Extensions installed successfully ==="
