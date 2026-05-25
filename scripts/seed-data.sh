#!/bin/bash
# ══════════════════════════════════════════════════════════
# Q-School AI — Seed Demo Data
# Chạy sau khi database đã sẵn sàng và migration đã apply.
# Usage: docker compose exec backend python -c "exec(open('scripts/seed_data.py').read())"
#    Or: ./scripts/seed-data.sh
# ══════════════════════════════════════════════════════════

set -e

echo "=== Q-School: Applying Alembic migrations ==="
docker compose exec backend alembic upgrade head

echo "=== Q-School: Seed data applied via migration 0001 ==="
echo "  - 3 Plans seeded: Free, Pro, Enterprise"
echo "  - 3 AI Personas seeded: Raina, Tutor, StudyBot"

echo ""
echo "=== Q-School Stack Ready ==="
echo "  Frontend:  http://localhost:5173"
echo "  Backend:   http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "  Adminer:   http://localhost:8080"
echo "  MinIO:     http://localhost:9001 (admin: minioadmin/minioadmin)"
echo ""
