"""
Dua tang Gold va bang van hanh (ops) tu kho DuckDB sang PostgreSQL - kho phuc vu cho BI (Metabase) va tro ly AI.
DuckDB van la may tinh toan cua pipeline (dbt-duckdb); Postgres la noi nhieu nguoi dung, nhieu cong cu doc dong thoi.

  python -m pipeline.publish --profile live

Cach lam (khong de nguoi doc thay du lieu do dang):
  1. nap moi bang vao schema tam <schema>__new qua extension postgres cua DuckDB (COPY nhi phan),
  2. doi soat so dong DuckDB = Postgres tung bang,
  3. trong MOT giao dich: xoa schema cu, doi ten schema tam, cap quyen chi doc cho bi_reader,
  4. tao chi muc cho cac cot hay loc, ghi nhat ky vao public.publish_log.
Moi tap mot CSDL (pg_database): tap van hanh thu dua hang ngay, tap phat trien va tap kiem tra dua 1 lan.
Ket noi lay tu bien moi truong FASTFAT_PG_* (mac dinh: localhost:5433, tai khoan quan tri cua docker compose).
"""
import argparse
import os
import time
from datetime import datetime
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = {"gold": None, "ops": ["alerts", "alert_scores", "pipeline_runs", "dq_checks"]}
INDEXES = {"gold.fact_order": ["date_day", "branch_id"], "gold.fact_order_line": ["date_day", "branch_id"],
           "gold.mart_branch_daily": ["date_day", "branch_id"], "gold.mart_branch_weekly": ["week_start", "branch_id"],
           "gold.mart_kpi_vs_peers_weekly": ["week_start", "branch_id", "kpi"], "ops.alerts": ["week_start", "branch_id"]}
CAST = {"HUGEINT": "BIGINT", "UBIGINT": "BIGINT", "UHUGEINT": "BIGINT"}   # Postgres khong co kieu so nguyen 128 bit


def pg_database(profile):
    """Moi tap mot CSDL: fastfat (tap van hanh thu, cap nhat hang ngay), fastfat_calibration, fastfat_holdout."""
    return "fastfat" if profile == "live" else f"fastfat_{profile}"


def pg_dsn(profile="live"):
    e = os.environ.get
    return (f"host={e('FASTFAT_PG_HOST', 'localhost')} port={e('FASTFAT_PG_PORT', '5433')} "
            f"dbname={pg_database(profile)} user={e('FASTFAT_PG_USER', 'fastfat')} "
            f"password={e('FASTFAT_PG_PASSWORD', 'fastfat_local')}")


def pg_exec(con, sql):
    """Chay lenh thang tren Postgres. Nhieu lenh trong mot lan goi duoc Postgres thuc hien trong mot giao dich."""
    con.execute("call postgres_execute('pg', '" + sql.replace("'", "''") + "')")


def publish(profile):
    t0 = time.time()
    path = ROOT / "data" / profile / "warehouse" / "fastfat.duckdb"
    con = duckdb.connect()
    con.execute("install postgres; load postgres")
    con.execute(f"attach '{path.as_posix()}' as wh (read_only)")
    con.execute(f"attach '{pg_dsn(profile)}' as pg (type postgres)")

    plan = []
    for schema, only in SCHEMAS.items():
        tables = [r[0] for r in con.execute(
            "select table_name from duckdb_tables() where database_name = 'wh' and schema_name = ? order by 1",
            [schema]).fetchall()]
        plan += [(schema, t) for t in tables if only is None or t in only]

    for schema in SCHEMAS:
        pg_exec(con, f"drop schema if exists {schema}__new cascade; create schema {schema}__new")
    con.execute("call pg_clear_cache()")   # DuckDB luu dem danh muc Postgres; lam moi de thay schema vua tao
    counts = {}
    for schema, t in plan:
        cols = con.execute("select column_name, data_type from duckdb_columns() where database_name = 'wh' "
                           "and schema_name = ? and table_name = ? order by column_index", [schema, t]).fetchall()
        select = ", ".join(f'cast("{c}" as {CAST[d]}) as "{c}"' if d in CAST else f'"{c}"' for c, d in cols)
        con.execute(f'create table pg.{schema}__new."{t}" as select {select} from wh.{schema}."{t}"')
        n_src = con.execute(f'select count(*) from wh.{schema}."{t}"').fetchone()[0]
        n_dst = con.execute(f'select count(*) from pg.{schema}__new."{t}"').fetchone()[0]
        counts[f"{schema}.{t}"] = (n_src, n_dst)
    bad = {k: v for k, v in counts.items() if v[0] != v[1]}
    if bad:
        raise RuntimeError(f"so dong lech giua DuckDB va Postgres: {bad}")

    # doi schema trong mot giao dich: nguoi doc thay ban cu hoac ban moi, khong bao gio thay ban do dang
    swap = []
    for schema in SCHEMAS:
        swap += [f"drop schema if exists {schema} cascade", f"alter schema {schema}__new rename to {schema}",
                 f"grant usage on schema {schema} to bi_reader", f"grant select on all tables in schema {schema} to bi_reader"]
    pg_exec(con, "; ".join(swap))
    for table, cols in INDEXES.items():
        if table.split(".", 1)[1] in {t for _, t in plan}:
            for c in cols:
                pg_exec(con, f"create index if not exists {table.replace('.', '_')}_{c} on {table} ({c})")
    pg_exec(con, "analyze")

    rows = sum(v[0] for v in counts.values())
    secs = time.time() - t0
    pg_exec(con, "create table if not exists public.publish_log (published_at timestamptz, profile text, "
                 "n_tables int, n_rows bigint, seconds double precision); "
                 "grant select on public.publish_log to bi_reader")
    pg_exec(con, f"insert into public.publish_log values ('{datetime.now().astimezone().isoformat()}', '{profile}', "
                 f"{len(plan)}, {rows}, {secs:.1f})")
    con.close()
    return len(plan), rows, secs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="live", choices=["calibration", "holdout", "live"])
    args = ap.parse_args()
    n, rows, secs = publish(args.profile)
    print(f"Da dua {n} bang, " + f"{rows:,}".replace(",", ".") + f" dong sang Postgres, doi soat so dong khop, {secs:.0f} giay")


if __name__ == "__main__":
    main()
