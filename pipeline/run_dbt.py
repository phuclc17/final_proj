"""
Chay dbt tren kho cua mot tap du lieu.
  python -m pipeline.run_dbt --profile calibration build
  python -m pipeline.run_dbt --profile calibration run --select stg_pos__receipts
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    from .dbutil import wait_writable
except ImportError:          # chay truc tiep bang duong dan tep
    from dbutil import wait_writable

ROOT = Path(__file__).resolve().parent.parent
DBT_DIR = ROOT / "dbt"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="calibration", choices=["calibration", "holdout", "live"])
    ap.add_argument("dbt_args", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    env = dict(os.environ, FASTFAT_DB=str(ROOT / "data" / args.profile / "warehouse" / "fastfat.duckdb"),
               PYTHONIOENCODING="utf-8")
    # dbt tu mo ket noi rieng: cho kho ranh (ung dung co the dang doc) roi moi giao cho dbt
    wait_writable(ROOT / "data" / args.profile / "warehouse" / "fastfat.duckdb")
    dbt = Path(sys.executable).parent / ("dbt.exe" if os.name == "nt" else "dbt")
    # moi tap du lieu dung thu muc target/log rieng de chay song song khong tranh chap
    cmd = [str(dbt), *args.dbt_args, "--project-dir", str(DBT_DIR), "--profiles-dir", str(DBT_DIR),
           "--target-path", str(DBT_DIR / f"target_{args.profile}"), "--log-path", str(DBT_DIR / f"logs_{args.profile}")]
    sys.exit(subprocess.run(cmd, env=env).returncode)


if __name__ == "__main__":
    main()
