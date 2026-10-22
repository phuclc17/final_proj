"""Kenh tiep nhan tep do nguoi gui (ke toan tai bao cao san, quan ly cua hang gui so kho, phieu kiem ke...).

Ngoai thuc te, phan lon du lieu van hanh F&B den duoi dang tep do nguoi hoac phan mem xuat ra, gui qua email, Drive,
Zalo. Kenh nay lam dung viec mot nhan vien du lieu se lam bang tay:
  1. nhan dang tep thuoc nguon nao theo NOI DUNG (pipeline/contracts.py), khong tin vao ten tep,
  2. kiem tra hop dong du lieu; sai thi tu choi kem ly do, luu tep vao _rejected/ de nguoi gui sua,
  3. tep trung noi dung voi tep da co duoi ten khac -> tu choi (tranh dem hai lan doanh thu, nhap kho),
  4. CSV doi bang ma (UTF-16, Windows) -> chuyen ve UTF-8,
  5. ghi vao dung vi tri chuan trong vung tiep nhan (ghi tam roi doi ten: pipeline khong bao gio doc tep dang ghi do);
     cung vi tri ma noi dung khac -> ban sua, buoc nap se thay ban cu,
  6. ghi nhat ky tiep nhan (landing/intake_log.jsonl) - doc duoc ca khi kho dang bi pipeline ghi.
Chi dung cho moi truong van hanh (live); hai tap danh gia khong nhan du lieu moi.
"""
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

from .contracts import BY_KEY, identify, read_text

ROOT = Path(__file__).resolve().parent.parent


def paths(profile):
    base = ROOT / "data" / profile
    return base / "source_systems", base / "landing"


def md5(data):
    return hashlib.md5(data).hexdigest()


def intake(profile, name, data, sender="tải lên"):
    """Tiep nhan mot tep. Tra ve dict: trang thai, nguon, vi tri, ly do, luu y."""
    src, landing = paths(profile)
    (landing / "_rejected").mkdir(parents=True, exist_ok=True)
    h = md5(data)
    r = identify(name, data, src)
    rec = {"time": datetime.now().isoformat(timespec="seconds"), "file": name, "bytes": len(data), "md5": h,
           "sender": sender, "source": BY_KEY[r.source]["system"] if r.source else None, "target": r.target,
           "facts": {k: str(v) for k, v in r.facts.items()}, "notes": r.notes, "status": None, "reason": None}

    def reject(reason):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        (landing / "_rejected" / f"{stamp}__{Path(name).name}").write_bytes(data)
        rec.update(status="từ chối", reason=reason)
        return log(landing, rec)

    if not r.ok:
        return reject("; ".join(r.errors) or "Không nhận dạng được nguồn của tệp.")

    out = data
    if r.target.endswith(".csv"):             # chuan hoa bang ma ve UTF-8 (khong BOM) truoc khi vao vung tiep nhan
        text, _ = read_text(data)
        out = text.encode("utf-8")
    target = src / r.target
    if target.exists():
        if md5(target.read_bytes()) == md5(out):
            rec.update(status="trùng, bỏ qua", reason="Tệp giống hệt bản đã có trong vùng tiếp nhận.")
            return log(landing, rec)
        status = "thay bản cũ"
        rec["reason"] = "Cùng nguồn, cùng ngày với tệp đã có nhưng nội dung khác: coi là bản sửa, sẽ nạp lại thay bản cũ."
    else:
        status = "đã nhận"
        h_out = md5(out)
        for other in target.parent.glob(f"*{target.suffix}"):   # trung noi dung voi tep khac (vd gui nham ten, ngay)
            if md5(other.read_bytes()) == h_out:
                return reject(f"Nội dung giống hệt tệp đã có {other.relative_to(src).as_posix()}; nạp thêm sẽ đếm hai lần.")
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(f".{target.name}.part")
    tmp.write_bytes(out)
    os.replace(tmp, target)                   # doi ten nguyen tu
    rec["status"] = status
    return log(landing, rec)


def log(landing, rec):
    landing.mkdir(parents=True, exist_ok=True)
    with open(landing / "intake_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def history(profile, n=50):
    _, landing = paths(profile)
    f = landing / "intake_log.jsonl"
    if not f.exists():
        return []
    lines = f.read_text(encoding="utf-8").splitlines()
    return [json.loads(x) for x in lines[-n:]][::-1]
