"""Hai DAG tach dung vai tro, giong mot doanh nghiep that:

fastfat_nguon    - HE THONG NGUON (o day la bo mo phong): cuoi ngay cac he thong POS, App, kho, cham cong... ghi du
                   lieu. Phan mem co API (POS dam may, App) ghi vao kho cua chinh no (source_api/ phuc vu qua API),
                   phan mem chi xuat tep ghi vao source_systems/. Khong dung vao kho du lieu. Xong thi bao Dataset.
fastfat_pipeline - PIPELINE: chay khi co du lieu moi, khong can ai bam:
                     (1) ngay khi DAG nguon bao Dataset cap nhat, hoac
                     (2) moi gio tu kiem tra - phong khi tep do he thong ben ngoai day vao (khong qua Airflow).
                   'extract' keo du lieu moi qua API ve vung tiep nhan (API loi -> ghi nhan, KHONG chan nguon tep);
                   'check' doi chieu tep nguon voi nhat ky nap; khong co tep moi -> cac buoc sau bi bo qua.
                   extract -> check -> ingest -> quality -> dbt -> detect -> publish.
Tren dam may, mau nay tuong ung: tep moi tren S3 -> su kien (EventBridge) -> kich hoat pipeline.
"""
import os
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.datasets import Dataset
from airflow.models.param import Param
from airflow.operators.bash import BashOperator
from airflow.sensors.python import PythonSensor
from airflow.timetables.datasets import DatasetOrTimeSchedule
from airflow.timetables.trigger import CronTriggerTimetable

HOME = os.environ.get("FASTFAT_HOME", "/opt/fastfat")
PY = os.environ.get("FASTFAT_PYTHON", "/opt/fastfat-venv/bin/python")
TZ = "Asia/Ho_Chi_Minh"
SOURCE_FILES = Dataset(f"file://{HOME}/data/live/source_systems")
START = pendulum.datetime(2026, 10, 1, tz=TZ)


def pipeline_idle():
    """He thong nguon (mo phong) cho pipeline xu ly xong lo truoc roi moi xuat tep moi,
    tranh pipeline nap mot ngay dang ghi do."""
    from airflow.models import DagRun
    from airflow.utils.state import DagRunState
    return not any(DagRun.find(dag_id="fastfat_pipeline", state=s) for s in (DagRunState.RUNNING, DagRunState.QUEUED))


with DAG(
    dag_id="fastfat_nguon",
    description="He thong nguon (mo phong): cuoi ngay xuat tep POS, App, san, kho, cham cong",
    # ban trinh dien cong khai: khong tu sinh ngay moi luc 23:00, nguoi xem bam nut trong ung dung
    schedule=None if os.environ.get("FASTFAT_DEMO") == "1" else "0 23 * * *",
    start_date=START,
    catchup=False,
    max_active_runs=1,
    params={"days": Param(1, type="integer", minimum=1, maximum=14, description="So ngay kinh doanh sinh them")},
    tags=["fastfat"],
) as nguon:
    wait = PythonSensor(task_id="cho_pipeline_ranh", python_callable=pipeline_idle, poke_interval=10,
                        timeout=1800, mode="reschedule", doc_md="Chờ pipeline xử lý xong lô trước.")
    export = BashOperator(
        task_id="xuat_tep",
        doc_md="Bộ mô phỏng sinh các ngày kinh doanh mới, mỗi hệ thống nguồn ghi tệp theo định dạng riêng.",
        bash_command=f"cd {HOME} && {PY} -m pipeline.run_daily --profile live --step simulate --days {{{{ params.days }}}}",
        outlets=[SOURCE_FILES],
    )
    wait >> export


with DAG(
    dag_id="fastfat_pipeline",
    description="Pipeline du lieu: chay khi co tep nguon moi",
    schedule=DatasetOrTimeSchedule(timetable=CronTriggerTimetable("0 * * * *", timezone=TZ), datasets=[SOURCE_FILES]),
    start_date=START,
    catchup=False,
    max_active_runs=1,  # DuckDB chi cho 1 tien trinh ghi tai mot thoi diem
    default_args={"retries": 1, "retry_delay": timedelta(minutes=2)},
    params={"profile": "live"},
    tags=["fastfat"],
) as pipeline:
    steps = [
        ("extract", "Bộ kết nối kéo dữ liệu mới từ API POS đám mây và App về vùng tiếp nhận (tăng dần theo mốc ngày)"),
        ("check", "Có tệp nguồn mới chưa nạp không? Không có thì bỏ qua các bước sau."),
        ("ingest", "Nạp tệp mới vào Bronze, tăng dần theo mã băm tệp"),
        ("quality", "Cửa chặn chất lượng đầu vào: độ mới, khối lượng, tệp lỗi, thay đổi cấu trúc"),
        ("dbt", "dbt build: Silver, Gold và kiểm thử chất lượng dữ liệu"),
        ("detect", "Quét bộ chỉ số giám sát, ghi cảnh báo vào ops.alerts"),
        ("publish", "Đưa Gold, ops sang kho phục vụ PostgreSQL, đối soát số dòng"),
    ]
    tasks = [
        BashOperator(
            task_id=step,
            doc_md=desc,
            bash_command=f"cd {HOME} && {PY} -m pipeline.run_daily --profile {{{{ params.profile }}}} "
                         f"--step {step} --run-id {{{{ run_id }}}}",
            skip_on_exit_code=99 if step == "check" else None,
            retries=0 if step == "check" else 1,
        )
        for step, desc in steps
    ]
    for a, b in zip(tasks, tasks[1:]):
        a >> b
