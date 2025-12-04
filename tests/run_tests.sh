#!/bin/bash
set -e

PGHOST=localhost
PGPORT=5432
PGUSER=nutrition_app
PGPASSWORD=nutrition_secure_password
PGDATABASE=nutrition

export PGPASSWORD

for test in tests/test_*.sql; do
  echo "Running $test..."
  cat $test | docker exec -i nutrition-postgres psql -h $PGHOST -U $PGUSER -d $PGDATABASE
  echo "✓ $test passed"
done
