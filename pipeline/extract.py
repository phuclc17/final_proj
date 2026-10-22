"""
Bo ket noi API (tang thu thap, truoc Bronze): keo du lieu tu API cua cac phan mem nguon ve vung tiep nhan, tang dan.
Ap dung cho nguon co API: POS dam may (chi nhanh dung POS ban moi) va App dat hang rieng. POS cai tai may, cham cong,
bao cao san, so kho... van den bang tep (xem pipeline/contracts.py).

Moi he thong, moi lan chay:
  1. hoi API cac ngay kinh doanh dang co (business-dates)
  2. lay cac ngay sau moc lan truoc, va lay lai chinh ngay moc (REFETCH_DAYS): hoa don cua may POS mat mang dong bo tre,
     hay mot ngay dang ghi do luc lay lan truoc, duoc bo sung o lan sau
  3. moi ngay lay het cac trang; doi chieu so ban ghi nhan duoc voi tong API bao, lech -> khong ghi, bao loi
  4. ghi tep vao vung tiep nhan dung ten, dung dinh dang nhu tep xuat cua nguon (ghi tep tam roi doi ten: buoc nap
     khong bao gio doc tep ghi do); noi dung khong doi so voi tep dang co -> khong ghi lai
  5. dich moc len sau MOI ngay ghi xong: loi giua chung thi lan sau lam tiep tu ngay do, khong mat, khong trung
Loi tam thoi (503, mat ket noi, qua thoi gian) va gioi han tan suat (429 + Retry-After) -> thu lai, cho tang dan.
Sai ma xac thuc (401) -> dung ngay, khong thu lai. API khong lay duoc sau nhieu lan thu -> ghi nhan, KHONG chan cac
nguon khac: cua chan chat luong bao chi nhanh thieu POS, bo phat hien khong ket luan su co tren du lieu thieu.
Trang thai (moc, lan chay gan nhat, so trang, so ban ghi, so lan thu lai, ket qua) o data/<tap>/landing/api_connector.json.

  python -m pipeline.extract --profile live
  python -m pipeline.extract --profile live --since 2024-09-23   # lay lai tu ngay (bu du lieu thieu da qua moc)
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = os.environ.get("FASTFAT_SOURCE_API", "http://localhost:8600")
TOKEN = os.environ.get("SOURCE_API_TOKEN", "fastfat-demo-token")
PAGE_SIZE = 200
MAX_ATTEMPTS = 6
REFETCH_DAYS = 1
SYSTEMS = {
    "pos": dict(label="POS đám mây", dates="/pos/v1/business-dates", records="/pos/v1/receipts"),
    "app": dict(label="App đặt hàng", dates="/app/v1/business-dates", records="/app/v1/orders"),
}


class ApiError(Exception):
    pass


class Http:
    """Goi HTTP bang thu vien chuan -> (ma trang thai, tieu de, JSON). Loi mang -> OSError."""

    def __init__(self, base=BASE_URL, timeout=30):
        self.base, self.timeout = base.rstrip("/"), timeout

    def get(self, path, params, headers):
        url = f"{self.base}{path}?{urllib.parse.urlencode(params)}" if params else f"{self.base}{path}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=self.timeout) as r:
                head, raw = {k.lower(): v for k, v in r.headers.items()}, r.read()
            try:
                return r.status, head, json.loads(raw)
            except ValueError:            # phan hoi cut giua chung -> coi nhu loi tam thoi, thu lai
                return 502, head, {"detail": "phản hồi không phải JSON hợp lệ"}
        except urllib.error.HTTPError as e:
            try:
                body = json.loads(e.read() or b"{}")
            except ValueError:
                body = {}
            return e.code, {k.lower(): v for k, v in e.headers.items()}, body


class Client:
    """Goi API co xac thuc, thu lai khi loi tam thoi; dem so lan goi, so lan thu lai."""

    def __init__(self, http=None, token=TOKEN, sleep=time.sleep):
        self.http, self.token, self.sleep = http or Http(), token, sleep
        self.calls = self.retries = 0

    def get(self, path, **params):
        wait = 0.5
        for attempt in range(1, MAX_ATTEMPTS + 1):
            self.calls += 1
            try:
                code, headers, body = self.http.get(path, params, {"Authorization": f"Bearer {self.token}"})
            except OSError as e:          # mat ket noi, tu choi ket noi, qua thoi gian
                code, headers, body = None, {}, {"detail": f"không kết nối được ({e.__class__.__name__})"}
            if code == 200:
                return body
            reason = f"{code or 'mạng'}: {(body or {}).get('detail', '')}".strip()
            if code in (401, 403):
                raise ApiError(f"API từ chối mã xác thực ({reason}), kiểm tra SOURCE_API_TOKEN")
            if code is not None and code < 500 and code != 429:
                raise ApiError(f"API trả lỗi {reason}")
            if attempt == MAX_ATTEMPTS:
                raise ApiError(f"API không phản hồi được sau {MAX_ATTEMPTS} lần thử (lần cuối {reason})")
            self.retries += 1
            delay = float(headers.get("retry-after", wait)) if code == 429 else wait
            self.sleep(min(delay, 10))
            wait *= 2


def fetch_day(client, system, day):
    """Moi ban ghi cua mot ngay, het cac trang. Lech so ban ghi so voi tong API bao -> ApiError."""
    out, page, pages, total = [], 1, 1, 0
    while page <= pages:
        body = client.get(SYSTEMS[system]["records"], date=day, page=page, page_size=PAGE_SIZE)
        pages, total = body["total_pages"], body["total"]
        out += body["data"]
        page += 1
    if len(out) != total:
        raise ApiError(f"Ngày {day}: nhận {len(out)} bản ghi, API báo {total} (dữ liệu đổi giữa chừng), lấy lại sau")
    return out, pages


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def write_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def land(src, system, day, records):
    """Ghi vao vung tiep nhan theo dung dinh dang tep cua nguon. Tra ve (so tep ghi moi/ghi lai, so tep khong doi)."""
    files = {}
    if system == "pos":       # moi may POS mot thu muc, nhu tep xuat cua phan mem POS
        for r in records:
            m = re.match(r"POS-\d+", str(r.get("terminal_id") or ""))
            prefix = m.group(0) if m else "POS-khong-ro-may"     # buoc nap se tu choi kem ly do, khong mat im lang
            files.setdefault(src / "pos" / prefix / f"pos_export_{day}.json", []).append(r)
        files = {p: dump(v) for p, v in files.items()}
    else:
        p = src / "owned_app" / f"orders_{day.replace('-', '')}.json"
        if p.exists():
            try:
                if json.loads(p.read_text(encoding="utf-8")).get("data") == records:
                    return 0, 1
            except ValueError:
                pass
        files = {p: dump({"extracted_at": f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}",
                          "source": f"GET {SYSTEMS['app']['records']}?date={day}", "business_date": day,
                          "page": 1, "page_size": len(records), "total": len(records), "data": records})}
    written = same = 0
    for p, data in files.items():
        if p.exists() and p.read_bytes() == data:
            same += 1
            continue
        write_atomic(p, data)
        written += 1
    return written, same


def initial_watermark(src, system):
    """Lan dau ket noi: moc = ngay cuoi cung MOI may POS (hoac App) deu da co trong vung tiep nhan (du lieu cu da den
    bang duong khac). Lay ngay nho nhat trong cac 'ngay moi nhat cua tung may', khong lay ngay lon nhat: may POS cai tai
    may xuat tep rieng co the da toi truoc. May im lang qua 14 ngay (chi nhanh dong cua) khong tinh. Lay thua vai ngay
    khong sao: noi dung khong doi thi khong ghi lai."""
    pat = "pos/*/pos_export_*.json" if system == "pos" else "owned_app/orders_*.json"
    latest = {}
    for p in src.glob(pat):
        m = re.search(r"(\d{4})-?(\d{2})-?(\d{2})", p.name)
        if m:
            d = "-".join(m.groups())
            latest[p.parent.name] = max(latest.get(p.parent.name, d), d)
    if not latest:
        return None
    newest = date.fromisoformat(max(latest.values()))
    active = [d for d in latest.values() if date.fromisoformat(d) >= newest - timedelta(days=14)]
    return min(active)


def state_file(profile):
    return ROOT / "data" / profile / "landing" / "api_connector.json"


def save_state(profile, state):
    write_atomic(state_file(profile), json.dumps(state, ensure_ascii=False, indent=1).encode("utf-8"))


def run(profile, client=None, since=None):
    """Keo moi he thong co API. Tra ve {he thong: tom tat}; khong nem loi API ra ngoai.
    since: lay lai tu ngay nay (dat moc ve ngay truoc do)."""
    src = ROOT / "data" / profile / "source_systems"
    sf = state_file(profile)
    state = json.loads(sf.read_text(encoding="utf-8")) if sf.exists() else {}
    for system, cfg in SYSTEMS.items():
        st = state.setdefault(system, {"watermark": initial_watermark(src, system)})
        if since:
            st["watermark"] = (date.fromisoformat(since) - timedelta(days=1)).isoformat()
        c = client or Client()
        c.calls = c.retries = 0
        t0, days_done, pages, records, written, same = time.time(), [], 0, 0, 0, 0
        try:
            available = c.get(cfg["dates"])["dates"]
            wm = st.get("watermark")
            start = (date.fromisoformat(wm) - timedelta(days=REFETCH_DAYS - 1)).isoformat() if wm else ""
            for day in sorted(d for d in available if d >= start):
                recs, n_pages = fetch_day(c, system, day)
                w, s = land(src, system, day, recs)
                days_done.append(day)
                pages, records, written, same = pages + n_pages, records + len(recs), written + w, same + s
                st["watermark"] = max(st.get("watermark") or day, day)
                save_state(profile, state)        # dich moc sau tung ngay
            new = [d for d in days_done if not wm or d > wm]
            status = (f"{len(new)} ngày mới" if new else "không có ngày mới") + (f", {written} tệp ghi" if written else "")
            st["ok"] = True
        except ApiError as e:
            status, st["ok"] = f"lỗi: {e}", False
        except (KeyError, TypeError, ValueError) as e:
            status, st["ok"] = f"lỗi: phản hồi API sai định dạng ({e.__class__.__name__}: {e})", False
        st.update(last_run=f"{datetime.now():%d/%m/%Y %H:%M:%S}", pages=pages, records=records, calls=c.calls,
                  retries=c.retries, files_written=written, files_unchanged=same, days=days_done, status=status,
                  seconds=round(time.time() - t0, 1), label=cfg["label"])
        save_state(profile, state)
    return state


def summary(state):
    return "; ".join(f"{v['label']}: {v['status']}, {v['records']} bản ghi, {v['pages']} trang, {v['retries']} lần thử lại"
                     for v in state.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="live", choices=["live"])
    ap.add_argument("--since", help="lay lai tu ngay YYYY-MM-DD")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    state = run(args.profile, since=args.since)
    print(summary(state))
    sys.exit(0 if all(v.get("ok") for v in state.values()) else 1)


if __name__ == "__main__":
    main()
