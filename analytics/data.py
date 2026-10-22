"""Doc cac bang Gold can cho phan tich. Mo ket noi chi doc roi dong ngay de khong giu khoa tep DuckDB."""
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
# moi truong van hanh (nhan du lieu moi) la mac dinh; hai tap danh gia la du lieu co dinh de cham diem bo phat hien
PROFILES = {"Vận hành": "live", "Đánh giá · tập phát triển": "calibration", "Đánh giá · tập kiểm tra": "holdout"}
TABLES = ["mart_kpi_vs_peers_weekly", "mart_branch_weekly", "mart_branch_daily", "mart_cashier_weekly",
          "mart_ingredient_avt", "dim_branch", "dim_date", "dim_menu_item", "dim_ingredient", "fact_labor_shift"]
DATE_COLS = {"week_start", "date_day", "period_start_excl", "period_end", "valid_from", "valid_to"}


def db_path(profile):
    return ROOT / "data" / profile / "warehouse" / "fastfat.duckdb"


def load_gold(profile):
    path = db_path(profile)
    if not path.exists():
        return None
    with duckdb.connect(str(path), read_only=True) as con:
        have = set(con.sql("select table_name from duckdb_tables() where schema_name = 'gold'").df().table_name)
        if not set(TABLES) <= have:
            return None
        out = {t: con.sql(f"select * from gold.{t}").df() for t in TABLES}
    for df in out.values():
        for c in DATE_COLS & set(df.columns):
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return out
