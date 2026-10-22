#!/bin/bash
# Chay MOT lan khi tao volume du lieu Postgres lan dau.
# - CSDL fastfat (tap van hanh thu, cap nhat hang ngay), fastfat_calibration, fastfat_holdout (dua 1 lan):
#   kho phuc vu, nhan cac bang Gold, ops tu DuckDB (pipeline/publish.py)
# - vai tro bi_reader: chi doc, cho Metabase va tro ly AI
# - CSDL metabase: CSDL ung dung cua Metabase (cau hinh, cau hoi, dashboard)
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE bi_reader LOGIN PASSWORD '${BI_READER_PASSWORD}';
    GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO bi_reader;
    CREATE DATABASE fastfat_calibration;
    CREATE DATABASE fastfat_holdout;
    GRANT CONNECT ON DATABASE fastfat_calibration TO bi_reader;
    GRANT CONNECT ON DATABASE fastfat_holdout TO bi_reader;
    CREATE ROLE metabase LOGIN PASSWORD '${MB_DB_PASSWORD}';
    CREATE DATABASE metabase OWNER metabase;
EOSQL
