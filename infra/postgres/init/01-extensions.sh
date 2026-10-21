#!/usr/bin/env bash
# Runs once on an empty data volume. Creates the test database and enables
# pgvector in both. Migrations also enable the extension, so this is only a
# convenience for fresh local volumes.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
  CREATE EXTENSION IF NOT EXISTS vector;
  CREATE DATABASE ${POSTGRES_DB}_test OWNER "$POSTGRES_USER";
SQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "${POSTGRES_DB}_test" <<-SQL
  CREATE EXTENSION IF NOT EXISTS vector;
SQL
