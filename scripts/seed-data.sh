#!/bin/bash
# ══════════════════════════════════════════════════════════
# Q-School AI — Seed Demo Data
# Chạy sau khi database đã sẵn sàng và migration đã apply.
# Usage: ./scripts/seed-data.sh
#    Or: docker compose exec -T backend alembic upgrade head
# ══════════════════════════════════════════════════════════

set -e

echo "=== Q-School: Applying Alembic migrations ==="
docker compose exec -T backend alembic upgrade head

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
