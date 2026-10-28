"""Tai du lieu cho ban xem truc tuyen tu dataset tren Hugging Face va giai nen vao thu muc du an.
Moi moi truong (calibration, holdout, live) la mot tep tar.gz gom data/<tap>/... va dbt/target_<tap>/.
python deploy/huggingface/fetch_data.py <ten dataset>"""
import sys
import tarfile
from pathlib import Path

from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[2]
folder = Path(snapshot_download(repo_id=sys.argv[1], repo_type="dataset", allow_patterns=["*.tar.gz"]))
for archive in sorted(folder.glob("*.tar.gz")):
    with tarfile.open(archive) as tar:
        tar.extractall(ROOT, filter="data")
    print("giai nen", archive.name)
