"""
Dung phan BI tren Metabase bang ma (tai lap duoc, chay lai bao nhieu lan cung duoc):
  - tao tai khoan quan tri lan dau, ket noi 3 CSDL cua kho phuc vu (moi tap du lieu mot CSDL) bang tai khoan CHI DOC,
  - moi tap mot bo suu tap gom cac cau hoi SQL va dashboard "Tình hình kinh doanh" co bo loc Khoang ngay, Chi nhanh,
  - bat lien ket xem cong khai cho dashboard (du lieu mo phong) va ghi duong dan vao bi/metabase_links.json
    de ung dung Streamlit nhung dashboard vao trang "Dashboard BI".

  .venv/Scripts/python bi/metabase_setup.py                 # Metabase o http://localhost:3000
  .venv/Scripts/python bi/metabase_setup.py --url http://<may chu>:3000

Mat khau lay tu bien moi truong (xem .env.example), mac dinh dung gia tri cho may ca nhan.
"""
import argparse
import json
import os
import time
import uuid
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
E = os.environ.get
ADMIN = {"email": E("METABASE_ADMIN_EMAIL", "admin@fastfat.local"), "password": E("METABASE_ADMIN_PASSWORD", "FastFat-Metabase-1")}
DB_DETAILS = {"host": "warehouse-db", "port": 5432, "user": "bi_reader",
              "password": E("BI_READER_PASSWORD", "bi_reader_local"), "ssl": False,
              "schema-filters-type": "inclusion", "schema-filters-patterns": "gold,ops,public"}
# (ma tap, ten hien thi, CSDL tren kho phuc vu) - trung voi pipeline/publish.py pg_database()
PROFILES = [("live", "Vận hành thử", "fastfat"), ("calibration", "Tập phát triển", "fastfat_calibration"),
            ("holdout", "Tập kiểm tra", "fastfat_holdout")]
OLD_NAMES = {"Kho phục vụ Fast&Fat (PostgreSQL)", "Fast&Fat"}   # ban dung truoc (mot tap), go khi dung lai
VND = {"number_style": "decimal", "suffix": " đ", "number_separators": ",."}

# ---------------------------------------------------------------- cau hoi (SQL tren kho phuc vu)
# {{ngay}}, {{chi_nhanh}} la bo loc truong (field filter) cua Metabase, gan vao cot that ben duoi (filters).
# Bang duoc loc KHONG dat bi danh, vi Metabase sinh dieu kien theo ten day du "schema"."bang"."cot".
DAILY = "gold.mart_branch_daily"
# mau theo kenh, cung bang mau voi ung dung (.streamlit/config.toml)
KENH = {"Tại quầy": "#1F3A5F", "App riêng": "#2F7F86", "GrabFood": "#5B8DB8", "ShopeeFood": "#C08A2E"}
CARDS = [
    {"key": "doanh_thu", "name": "Doanh thu", "desc": "Doanh thu thuần: tiền món sau giảm giá của đơn hoàn thành", "display": "scalar",
     "sql": f"select sum(net_sales) as doanh_thu from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}}",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"scalar.compact_primary_number": False,
             "column_settings": {'["name","doanh_thu"]': {**VND, "scale": 1e-9, "suffix": " tỷ đ", "decimals": 2}}}},
    {"key": "so_don", "name": "Số đơn", "desc": "Số đơn hoàn thành, cả 4 kênh", "display": "scalar",
     "sql": f"select sum(orders) as so_don from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}}",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"scalar.compact_primary_number": False}},
    {"key": "aov", "name": "AOV", "desc": "Giá trị đơn bình quân = doanh thu thuần / số đơn", "display": "scalar",
     "sql": f"select round(sum(net_sales)::numeric / nullif(sum(orders), 0)) as aov from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}}",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"scalar.compact_primary_number": False, "column_settings": {'["name","aov"]': VND}}},
    {"key": "cogs", "name": "COGS%", "desc": "Giá vốn theo định mức công thức / doanh thu thuần", "display": "scalar",
     "sql": f"select sum(cogs_standard)::numeric / nullif(sum(net_sales), 0) as cogs_pct from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}}",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"column_settings": {'["name","cogs_pct"]': {"number_style": "percent", "decimals": 1}}}},
    {"key": "labor", "name": "Labor%", "desc": "Chỉ gồm lương giờ trực tiếp theo chấm công, chưa có lương cố định, bảo hiểm", "display": "scalar",
     "sql": f"select sum(labor_cost)::numeric / nullif(sum(net_sales), 0) as labor_pct from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}}",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"column_settings": {'["name","labor_pct"]': {"number_style": "percent", "decimals": 1}}}},
    {"key": "do_moi", "name": "Dữ liệu đến", "desc": "Ngày mới nhất có trong kho phục vụ", "display": "scalar",
     "sql": "select to_char(max(date_day), 'DD/MM/YYYY') as den_ngay from gold.mart_branch_daily", "filters": {}, "viz": {}},
    {"key": "theo_ngay", "name": "Doanh thu theo ngày và trung bình 7 ngày", "display": "line",  # mau: xem KENH
     "sql": f"""select date_day as ngay, sum(net_sales) / 1e6 as doanh_thu,
       avg(sum(net_sales) / 1e6) over (order by date_day rows between 6 preceding and current row) as tb_7_ngay
from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}} group by date_day order by date_day""",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"graph.dimensions": ["ngay"], "graph.metrics": ["doanh_thu", "tb_7_ngay"],
             "graph.y_axis.title_text": "triệu đồng", "graph.x_axis.title_text": "Ngày",
             "series_settings": {"doanh_thu": {"title": "Doanh thu ngày", "color": "#9CA3AF"},
                                 "tb_7_ngay": {"title": "Trung bình 7 ngày", "color": "#1F3A5F"}}}},
    {"key": "co_cau_kenh", "name": "Cơ cấu doanh thu theo kênh", "display": "pie",
     "sql": f"""select k.kenh, sum(k.v) as doanh_thu from {DAILY}
cross join lateral (values ('Tại quầy', net_sales_walkin), ('App riêng', net_sales_app),
                          ('GrabFood', net_sales_grabfood), ('ShopeeFood', net_sales_shopeefood)) as k(kenh, v)
where {{{{ngay}}}} and {{{{chi_nhanh}}}} group by k.kenh order by 2 desc""",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"pie.dimension": "kenh", "pie.metric": "doanh_thu", "pie.show_legend": True, "pie.percent_visibility": "inside",
             "pie.colors": KENH}},
    {"key": "kenh_theo_tuan", "name": "Doanh thu theo kênh và tuần", "display": "bar",
     "sql": f"""select week_start as tuan, k.kenh, sum(k.v) / 1e6 as doanh_thu from {DAILY}
cross join lateral (values ('Tại quầy', net_sales_walkin), ('App riêng', net_sales_app),
                          ('GrabFood', net_sales_grabfood), ('ShopeeFood', net_sales_shopeefood)) as k(kenh, v)
where {{{{ngay}}}} and {{{{chi_nhanh}}}}
  and week_start + 6 <= (select max(date_day) from gold.mart_branch_daily)   -- bo tuan chua du 7 ngay
group by 1, 2 order by 1""",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"graph.dimensions": ["tuan", "kenh"], "graph.metrics": ["doanh_thu"], "stackable.stack_type": "stacked",
             "graph.y_axis.title_text": "triệu đồng", "graph.x_axis.title_text": "Tuần",
             "series_settings": {k: {"color": v} for k, v in KENH.items()}}},
    {"key": "theo_chi_nhanh", "name": "Doanh thu theo chi nhánh", "display": "row",
     "sql": f"""select 'CN' || branch_id || ' · hạng ' || store_class as chi_nhanh_hang,
       sum(net_sales) / 1e6 as doanh_thu from {DAILY}
where {{{{ngay}}}} and {{{{chi_nhanh}}}} group by 1 order by 2 desc""",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"graph.dimensions": ["chi_nhanh_hang"], "graph.metrics": ["doanh_thu"], "graph.x_axis.title_text": "",
             "series_settings": {"doanh_thu": {"color": "#1F3A5F"}},
             "graph.y_axis.title_text": "Doanh thu, triệu đồng"}},
    {"key": "canh_bao", "name": "Cảnh báo của bộ phát hiện", "display": "table",
     "sql": """select to_char(week_start, 'DD/MM/YYYY') as "Tuần", 'CN' || branch_id || ' · ' || branch_name as "Chi nhánh",
       cause || ' · ' || cause_name as "Nghi vấn", round(score::numeric, 1) as "Điểm",
       round(gap_vs_expected::numeric) as "Doanh thu so kỳ vọng", evidence as "Bằng chứng chính"
from ops.alerts where level = 'Cảnh báo' and {{tuan}} and {{chi_nhanh}} order by week_start desc, score desc""",
     "filters": {"tuan": ("ops", "alerts", "week_start"), "chi_nhanh": ("ops", "alerts", "branch_name")},
     "viz": {"column_settings": {'["name","Doanh thu so kỳ vọng"]': VND}}},
    {"key": "thuc_don", "name": "Thực đơn: doanh thu và biên gộp theo món", "display": "table",
     "sql": """select dim_menu_item.item_name as "Món", dim_menu_item.category as "Nhóm",
       sum(fact_order_line.qty) as "Số lượng", sum(fact_order_line.line_amount) as "Doanh thu",
       round(100 * (1 - sum(fact_order_line.cogs_standard)::numeric / nullif(sum(fact_order_line.line_amount), 0)), 1)
         as "Biên gộp %"
from gold.fact_order_line
join gold.dim_menu_item on dim_menu_item.menu_item_sk = fact_order_line.menu_item_sk
join gold.dim_branch on dim_branch.branch_id = fact_order_line.branch_id
where fact_order_line.is_revenue_line and {{ngay}} and {{chi_nhanh}}
group by 1, 2 order by 4 desc""",
     "filters": {"ngay": ("gold", "fact_order_line", "date_day"), "chi_nhanh": ("gold", "dim_branch", "branch_name")},
     "viz": {"column_settings": {'["name","Doanh thu"]': VND, '["name","Số lượng"]': {"number_separators": ",."}}}},
    {"key": "so_sanh_cn", "name": "So sánh chi nhánh", "display": "table",
     "sql": f"""select 'CN' || branch_id || ' · ' || branch_name as "Chi nhánh", store_class as "Hạng",
       sum(net_sales) as "Doanh thu thuần", sum(orders) as "Số đơn",
       round(sum(net_sales)::numeric / nullif(sum(orders), 0)) as "AOV",
       round(100 * sum(cogs_standard)::numeric / nullif(sum(net_sales), 0), 1) as "COGS%",
       round(100 * sum(labor_cost)::numeric / nullif(sum(net_sales), 0), 1) as "Labor%",
       round(100 * sum(app_store_cancels)::numeric / nullif(sum(app_orders_placed), 0), 1) as "Tự hủy đơn App %",
       round((sum(orders) / nullif(sum(labor_hours), 0))::numeric, 2) as "Đơn mỗi giờ công"
from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}} group by branch_id, branch_name, store_class order by branch_id""",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"column_settings": {'["name","Doanh thu thuần"]': VND, '["name","AOV"]': VND,
                                 '["name","Số đơn"]': {"number_separators": ",."}}}},
    {"key": "huy_app", "name": "Hủy App", "desc": "Đơn App bị cửa hàng hoặc khách hủy / đơn App đặt", "display": "scalar",
     "sql": f"""select sum(app_store_cancels + app_customer_cancels)::numeric / nullif(sum(app_orders_placed), 0) as huy
from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}}""",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"column_settings": {'["name","huy"]': {"number_style": "percent", "decimals": 1}}}},
    {"key": "nhan_su", "name": "Nhân sự và vận hành theo tuần", "display": "line",
     "sql": f"""select week_start as tuan,
       sum(orders_evening)::numeric / nullif(sum(shifts_evening), 0) as don_toi_moi_ca_toi,
       sum(app_prep_sum)::numeric / nullif(sum(app_prep_n), 0) as phut_chuan_bi_app
from {DAILY} where {{{{ngay}}}} and {{{{chi_nhanh}}}}
  and week_start + 6 <= (select max(date_day) from gold.mart_branch_daily)
group by 1 order by 1""",
     "filters": {"ngay": ("gold", "mart_branch_daily", "date_day"), "chi_nhanh": ("gold", "mart_branch_daily", "branch_name")},
     "viz": {"graph.dimensions": ["tuan"], "graph.metrics": ["don_toi_moi_ca_toi", "phut_chuan_bi_app"],
             "graph.x_axis.title_text": "Tuần", "graph.y_axis.title_text": "",
             "series_settings": {"don_toi_moi_ca_toi": {"title": "Số đơn tối mỗi ca tối", "color": "#1F3A5F"},
                                 "phut_chuan_bi_app": {"title": "Thời gian chuẩn bị đơn App, phút", "color": "#2F7F86"}}}},
]
# vi tri tren luoi 24 cot: (key, cot, hang, rong, cao)
LAYOUT = [("doanh_thu", 0, 0, 4, 3), ("so_don", 4, 0, 3, 3), ("aov", 7, 0, 3, 3), ("cogs", 10, 0, 3, 3),
          ("labor", 13, 0, 3, 3), ("huy_app", 16, 0, 3, 3), ("do_moi", 19, 0, 5, 3),
          ("theo_ngay", 0, 3, 16, 6), ("co_cau_kenh", 16, 3, 8, 6),
          ("kenh_theo_tuan", 0, 9, 12, 7), ("theo_chi_nhanh", 12, 9, 12, 7),
          ("canh_bao", 0, 16, 24, 6),
          ("so_sanh_cn", 0, 22, 24, 7),
          ("nhan_su", 0, 29, 10, 8), ("thuc_don", 10, 29, 14, 8)]
PARAMS = [{"id": "p_ngay", "name": "Khoảng ngày", "slug": "khoang_ngay", "type": "date/all-options", "sectionId": "date"},
          {"id": "p_chi_nhanh", "name": "Chi nhánh", "slug": "chi_nhanh", "type": "string/=", "sectionId": "string"}]
PARAM_OF_TAG = {"ngay": "p_ngay", "tuan": "p_ngay", "chi_nhanh": "p_chi_nhanh"}


class MB:
    def __init__(self, url):
        self.url, self.s = url.rstrip("/"), requests.Session()

    def call(self, method, path, **kw):
        r = self.s.request(method, f"{self.url}/api{path}", timeout=60, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:500]}")
        return r.json() if r.text else None


def wait_ready(mb, timeout=300):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if mb.s.get(f"{mb.url}/api/health", timeout=5).json().get("status") == "ok":
                return
        except (requests.RequestException, ValueError):
            pass
        time.sleep(3)
    raise RuntimeError("Metabase chưa sẵn sàng")


def login(mb):
    props = mb.call("GET", "/session/properties")
    token = props.get("setup-token")
    if token and not props.get("has-user-setup"):
        mb.call("POST", "/setup", json={
            "token": token,
            "user": {**ADMIN, "first_name": "Quản trị", "last_name": "Fast&Fat", "site_name": "Fast&Fat"},
            "prefs": {"site_name": "Fast&Fat", "site_locale": "vi", "allow_tracking": False}})
        print("Đã tạo tài khoản quản trị Metabase")
    sid = mb.call("POST", "/session", json={"username": ADMIN["email"], "password": ADMIN["password"]})["id"]
    mb.s.headers["X-Metabase-Session"] = sid


def ensure_database(mb, name, dbname):
    """Ket noi Metabase toi CSDL cua mot tap (tim theo ten CSDL de dung lai ket noi cu, doi ten neu can)."""
    dbs = mb.call("GET", "/database")
    dbs = dbs.get("data", dbs) if isinstance(dbs, dict) else dbs
    details = {**DB_DETAILS, "dbname": dbname}
    db = next((d for d in dbs if d["name"] == name or (d.get("engine") == "postgres"
                                                        and (d.get("details") or {}).get("dbname") == dbname)), None)
    if db is None:
        db = mb.call("POST", "/database", json={"engine": "postgres", "name": name, "details": details})
        print(f"Đã kết nối {name}")
    else:
        mb.call("PUT", f"/database/{db['id']}", json={"name": name, "details": details})
    mb.call("POST", f"/database/{db['id']}/sync_schema")
    return db["id"]


def field_ids(mb, db_id, need, timeout=180):
    """Doi Metabase dong bo xong cau truc kho roi tra ve id cua cac cot dung lam bo loc."""
    t0 = time.time()
    while True:
        meta = mb.call("GET", f"/database/{db_id}/metadata", params={"include_hidden": "true"})
        ids = {(t["schema"], t["name"], f["name"]): f["id"] for t in meta["tables"] for f in t.get("fields", [])}
        missing = [k for k in need if k not in ids]
        if not missing:
            return ids
        if time.time() - t0 > timeout:
            raise RuntimeError(f"Metabase chưa đồng bộ các cột: {missing}")
        time.sleep(3)


def reset_collection(mb, name):
    """Bo suu tap cua mot tap; dung lai thi go cac cau hoi, dashboard cu trong do."""
    cols = mb.call("GET", "/collection")
    for c in cols:   # bo suu tap cua ban dung mot tap truoc day
        if c.get("name") in OLD_NAMES and not c.get("archived") and isinstance(c.get("id"), int):
            mb.call("PUT", f"/collection/{c['id']}", json={"archived": True})
    col = next((c for c in cols if c.get("name") == name and not c.get("archived")), None)
    if col is None:
        return mb.call("POST", "/collection", json={"name": name, "description": "Dựng tự động bởi bi/metabase_setup.py"})["id"]
    items = mb.call("GET", f"/collection/{col['id']}/items")
    for it in items.get("data", items):
        kind = {"card": "card", "dataset": "card", "metric": "card", "dashboard": "dashboard"}.get(it["model"])
        if kind:
            mb.call("PUT", f"/{kind}/{it['id']}", json={"archived": True})
    return col["id"]


def build(mb, db_id, coll_id, ids, label):
    card_ids = {}
    for c in CARDS:
        tags = {}
        for tag, (sch, tbl, col) in c["filters"].items():
            is_date = tag in ("ngay", "tuan")
            tags[tag] = {"id": str(uuid.uuid4()), "name": tag, "type": "dimension",
                         "display-name": {"ngay": "Khoảng ngày", "tuan": "Tuần", "chi_nhanh": "Chi nhánh"}[tag],
                         "dimension": ["field", ids[(sch, tbl, col)], None],
                         "widget-type": "date/all-options" if is_date else "string/="}
        card = mb.call("POST", "/card", json={
            "name": c["name"], "display": c["display"], "collection_id": coll_id,
            "visualization_settings": c["viz"],
            "dataset_query": {"database": db_id, "type": "native", "native": {"query": c["sql"], "template-tags": tags}}})
        card_ids[c["key"]] = (card["id"], list(c["filters"]))
    dash = mb.call("POST", "/dashboard", json={
        "name": f"Tình hình kinh doanh · {label}", "collection_id": coll_id, "parameters": PARAMS,
        "description": "Doanh thu, kênh, chi nhánh, chi phí, nhân sự, thực đơn và cảnh báo; đọc kho phục vụ Postgres."})
    dashcards = []
    for i, (key, col, row, w, h) in enumerate(LAYOUT):
        cid, tags = card_ids[key]
        dashcards.append({"id": -(i + 1), "card_id": cid, "col": col, "row": row, "size_x": w, "size_y": h,
                          "parameter_mappings": [{"parameter_id": PARAM_OF_TAG[t], "card_id": cid,
                                                  "target": ["dimension", ["template-tag", t]]} for t in tags],
                          "visualization_settings": {}})
    mb.call("PUT", f"/dashboard/{dash['id']}", json={"dashcards": dashcards, "parameters": PARAMS})
    return dash["id"]


def remove_samples(mb):
    """Metabase tu cai kem CSDL mau va bo vi du; go di de giao dien chi con du lieu cua du an."""
    dbs = mb.call("GET", "/database")
    for d in (dbs.get("data", dbs) if isinstance(dbs, dict) else dbs):
        if d.get("is_sample"):
            mb.call("DELETE", f"/database/{d['id']}")
    for c in mb.call("GET", "/collection"):
        if c.get("is_sample") and not c.get("archived") and isinstance(c.get("id"), int):
            mb.call("PUT", f"/collection/{c['id']}", json={"archived": True})


def vn_formatting(mb):
    """Dinh dang chung: dau cham hang nghin, dau phay thap phan, ngay D/M/YYYY, gio 24h."""
    mb.call("PUT", "/setting/custom-formatting", json={"value": {
        "type/Number": {"number_separators": ",."},
        "type/Temporal": {"date_style": "D/M/YYYY", "date_abbreviate": False, "time_style": "HH:mm"},
        "type/Currency": {"currency": "VND", "currency_style": "code"}}})


def public_link(mb, dash_id):
    mb.call("PUT", "/setting/enable-public-sharing", json={"value": True})
    return mb.call("POST", f"/dashboard/{dash_id}/public_link")["uuid"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:3000")
    ap.add_argument("--public-url", default=None, help="địa chỉ người xem mở được (mặc định = --url)")
    args = ap.parse_args()
    mb = MB(args.url)
    wait_ready(mb)
    login(mb)
    remove_samples(mb)
    vn_formatting(mb)
    base = (args.public_url or args.url).rstrip("/")
    need = {f for c in CARDS for f in c["filters"].values()}
    links = {}
    for profile, label, dbname in PROFILES:
        db_id = ensure_database(mb, f"Kho phục vụ · {label}", dbname)
        ids = field_ids(mb, db_id, need)
        coll_id = reset_collection(mb, f"Fast&Fat · {label}")
        dash_id = build(mb, db_id, coll_id, ids, label)
        uid = public_link(mb, dash_id)
        links[profile] = {"dashboard": f"{base}/dashboard/{dash_id}", "public": f"{base}/public/dashboard/{uid}"}
        print(f"{label}: {len(CARDS)} câu hỏi, dashboard {links[profile]['dashboard']}")
    (HERE / "metabase_links.json").write_text(json.dumps(links, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
