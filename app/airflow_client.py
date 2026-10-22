"""Goi REST API cua Airflow: trang thai hai DAG (he thong nguon, pipeline), kich hoat he thong nguon, tam dung lich."""
import os

import requests

URL = os.environ.get("AIRFLOW_URL", "http://localhost:8080").rstrip("/")
AUTH = (os.environ.get("AIRFLOW_USER", "admin"), os.environ.get("AIRFLOW_PASSWORD", "admin"))
PUBLIC_URL = os.environ.get("AIRFLOW_PUBLIC_URL", "http://localhost:8080")
SOURCE, PIPELINE = "fastfat_nguon", "fastfat_pipeline"
PIPELINE_STEPS = ["extract", "check", "ingest", "quality", "dbt", "detect", "publish"]


def _get(path, **params):
    r = requests.get(f"{URL}/api/v1{path}", params=params, auth=AUTH, timeout=4)
    r.raise_for_status()
    return r.json()


def dag(dag_id):
    return _get(f"/dags/{dag_id}")


def runs(dag_id, limit=10):
    return _get(f"/dags/{dag_id}/dagRuns", order_by="-execution_date", limit=limit)["dag_runs"]


def tasks(dag_id, run_id):
    return {t["task_id"]: t for t in _get(f"/dags/{dag_id}/dagRuns/{run_id}/taskInstances")["task_instances"]}


def status(limit=10):
    """None neu Airflow khong chay; nguoc lai {dag_id: {dag, runs, tasks (cua luot moi nhat)}}."""
    try:
        out = {}
        for d in (SOURCE, PIPELINE):
            rs = runs(d, limit)
            out[d] = {"dag": dag(d), "runs": rs, "tasks": tasks(d, rs[0]["dag_run_id"]) if rs else {}}
        return out
    except (requests.RequestException, ValueError, KeyError):
        return None


def last_processing_run(limit=25):
    """Luot pipeline gan nhat co xu ly du lieu (buoc check khong bi bo qua vi khong co tep moi)."""
    for r in runs(PIPELINE, limit):
        t = tasks(PIPELINE, r["dag_run_id"])
        if t.get("check", {}).get("state") != "skipped":
            return r, t
    return None, {}


def busy():
    try:
        return any(r["state"] in ("running", "queued") for d in (SOURCE, PIPELINE) for r in runs(d, 3))
    except (requests.RequestException, ValueError, KeyError):
        return False


def trigger_source(days=1):
    """He thong nguon xuat tep cho `days` ngay kinh doanh moi; pipeline tu chay khi co tep moi."""
    r = requests.post(f"{URL}/api/v1/dags/{SOURCE}/dagRuns", json={"conf": {"days": int(days)}}, auth=AUTH, timeout=5)
    r.raise_for_status()
    return r.json()["dag_run_id"]


def set_paused(dag_id, paused):
    r = requests.patch(f"{URL}/api/v1/dags/{dag_id}", params={"update_mask": "is_paused"},
                       json={"is_paused": paused}, auth=AUTH, timeout=5)
    r.raise_for_status()


SOURCE_FILES = "file:///opt/fastfat/data/live/source_systems"   # Dataset ma DAG he thong nguon cap nhat


def notify_new_files(note=""):
    """Bao Airflow vung tiep nhan vua co tep moi (vd tep do nguoi tai len): tao su kien Dataset, pipeline tu chay
    dung nhu khi he thong nguon xuat tep. Airflow cu khong co API nay -> kich hoat thang DAG pipeline."""
    r = requests.post(f"{URL}/api/v1/datasets/events", json={"dataset_uri": SOURCE_FILES, "extra": {"from": note}},
                      auth=AUTH, timeout=5)
    if r.ok:
        return "dataset"
    r = requests.post(f"{URL}/api/v1/dags/{PIPELINE}/dagRuns", json={"conf": {}}, auth=AUTH, timeout=5)
    r.raise_for_status()
    return "dag"
