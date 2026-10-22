"""Chi co tren ban trinh dien cong khai (FASTFAT_DEMO=1): moi dem 02:00 dua moi truong van hanh ve diem ban dau.

Nguoi xem co the bam "Gui du lieu ngay moi" trong ung dung; dat lai hang dem giup moi nguoi xem sau do thay cung mot
trang thai khop voi bao cao. Cong cu tools/chuan_bi_demo.py cho pipeline ranh, tam dung hai DAG, chep lai anh chup
data/_demo_snapshot/live, dua lai sang PostgreSQL roi bat lai DAG.
"""
import os

import pendulum

if os.environ.get("FASTFAT_DEMO") == "1":
    from airflow import DAG
    from airflow.operators.bash import BashOperator

    HOME = os.environ.get("FASTFAT_HOME", "/opt/fastfat")
    PY = os.environ.get("FASTFAT_PYTHON", "/opt/fastfat-venv/bin/python")
    with DAG(
        dag_id="fastfat_dat_lai_demo",
        description="Ban trinh dien: moi dem dua moi truong van hanh ve diem ban dau",
        schedule="0 2 * * *",
        start_date=pendulum.datetime(2026, 10, 1, tz="Asia/Ho_Chi_Minh"),
        catchup=False,
        max_active_runs=1,
        tags=["fastfat", "trinh_dien"],
    ) as dat_lai:
        BashOperator(task_id="khoi_phuc_anh_chup",
                     bash_command=f"cd {HOME} && {PY} tools/chuan_bi_demo.py --khoi-phuc")
