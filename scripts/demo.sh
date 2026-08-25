#!/usr/bin/env sh
set -eu
API="${FLOWREBASE_API:-http://localhost:8000}"
echo "Seeding demo..."
seed=$(curl -sS -X POST "$API/api/v1/demo/seed")
printf '%s\n' "$seed"
echo "Portfolio summary:"
curl -sS "$API/api/v1/portfolio/summary"
printf '\n'
