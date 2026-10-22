"""Doc metadata cua dbt (manifest.json, run_results.json) de hien thi trong app: danh muc mo hinh, ket qua kiem thu,
pha he du lieu (lineage) va so do hinh sao tu sinh tu cac kiem thu quan he (relationships)."""
import json
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
LAYER = {"bronze": "Bronze", "silver_work": "Silver trung gian", "silver": "Silver", "gold": "Gold"}
LAYER_ORDER = ["Bronze", "Silver trung gian", "Silver", "Gold"]
LAYER_COLOR = {"Bronze": "#d9a066", "Silver trung gian": "#d9dde3", "Silver": "#b9c2cc", "Gold": "#f2c94c"}


def _target(profile):
    return ROOT / "dbt" / f"target_{profile}"


@st.cache_data
def _load_json(path, mtime):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def manifest(profile):
    p = _target(profile) / "manifest.json"
    return _load_json(str(p), p.stat().st_mtime) if p.exists() else None


def run_results(profile):
    p = _target(profile) / "run_results.json"
    return _load_json(str(p), p.stat().st_mtime) if p.exists() else None


def short(uid):
    return uid.split(".")[-1]


def nodes_table(m):
    """1 dong / mo hinh hoac bang nguon, kem tang, kieu luu tru, mo ta, so cot co mo ta, so kiem thu."""
    tests_per = defaultdict(int)
    for n in m["nodes"].values():
        if n["resource_type"] == "test" and n.get("attached_node"):
            tests_per[n["attached_node"]] += 1
    rows = []
    for uid, s in m["sources"].items():
        rows.append({"uid": uid, "Tên": s["name"], "Tầng": "Bronze", "Loại": "bảng nguồn", "Lưu trữ": "bảng",
                     "Mô tả": s.get("description", ""), "Số kiểm thử": tests_per[uid], "Phụ thuộc": []})
    for uid, n in m["nodes"].items():
        if n["resource_type"] not in ("model", "seed"):
            continue
        rows.append({"uid": uid, "Tên": n["name"], "Tầng": LAYER.get(n["schema"], n["schema"]),
                     "Loại": "bảng tra cứu" if n["resource_type"] == "seed" else
                     ("bảng chiều" if n["name"].startswith("dim_") else "bảng sự kiện" if n["name"].startswith("fact_")
                      else "bảng phân tích" if n["name"].startswith("mart_") else "mô hình"),
                     "Lưu trữ": n["config"].get("materialized", "seed"), "Mô tả": n.get("description", ""),
                     "Số kiểm thử": tests_per[uid], "Phụ thuộc": n.get("depends_on", {}).get("nodes", [])})
    return pd.DataFrame(rows)


def test_results(m, rr):
    """Ket qua tung kiem thu: ten, loai, bang duoc kiem, trang thai, thoi gian."""
    if rr is None:
        return pd.DataFrame()
    rows = []
    for r in rr["results"]:
        uid = r["unique_id"]
        if not uid.startswith("test."):
            continue
        n = m["nodes"].get(uid, {})
        meta = n.get("test_metadata") or {}
        rows.append({"Kiểm thử": n.get("name", short(uid)), "Loại": meta.get("name", "singular"),
                     "Bảng": short(n.get("attached_node") or "") or "nhiều bảng",
                     "Trạng thái": r["status"], "Giây": round(r.get("execution_time", 0), 2),
                     "Số dòng vi phạm": r.get("failures")})
    return pd.DataFrame(rows)


def _related(edges, focus, up=True, down=True):
    keep = {focus}
    parents, children = defaultdict(set), defaultdict(set)
    for a, b in edges:
        parents[b].add(a)
        children[a].add(b)
    for graph, go in ((parents, up), (children, down)):
        if not go:
            continue
        stack = [focus]
        while stack:
            for x in graph[stack.pop()]:
                if x not in keep:
                    keep.add(x)
                    stack.append(x)
    return keep


def lineage_dot(m, focus=None):
    """Do thi pha he: Bronze -> Silver trung gian -> Silver -> Gold; chon 1 mo hinh thi chi hien to tien va hau due."""
    t = nodes_table(m)
    ids = set(t.uid)
    edges = [(d, uid) for uid, deps in zip(t.uid, t["Phụ thuộc"]) for d in deps if d in ids]
    if focus:
        keep = _related(edges, focus)
        t = t[t.uid.isin(keep)]
        edges = [(a, b) for a, b in edges if a in keep and b in keep]
    # mot bang: xep doc theo tang (de doc); toan bo kho: xep ngang
    lines = ['digraph G {', ('rankdir=TB; splines=true; nodesep=0.25; ranksep=0.45;' if focus else
                             'rankdir=LR; splines=true; nodesep=0.15; ranksep=0.9;'),
             'node [shape=box, style="rounded,filled", fontname="Arial", fontsize=13, margin="0.1,0.05"];',
             'edge [color="#9aa5b1", arrowsize=0.5];']
    for k, layer in enumerate(LAYER_ORDER):
        sub = t[t.Tầng == layer]
        if sub.empty:
            continue
        lines.append(f'subgraph cluster_{k} {{ label="{layer}"; fontname="Arial"; fontsize=15; style="rounded"; '
                     f'color="#cccccc";')
        for r in sub.itertuples():
            pen = ', penwidth=2.5, color="#d62728"' if r.uid == focus else ""
            lines.append(f'"{r.uid}" [label="{r.Tên}", fillcolor="{LAYER_COLOR[layer]}"{pen}];')
        lines.append("}")
    lines += [f'"{a}" -> "{b}";' for a, b in edges]
    lines.append("}")
    return "\n".join(lines)


def star_dot(m):
    """So do hinh sao tu cac kiem thu quan he giua bang su kien va bang chieu tang Gold."""
    rel = []
    for n in m["nodes"].values():
        meta = n.get("test_metadata") or {}
        if meta.get("name") != "relationships":
            continue
        kw = meta.get("kwargs", {})
        src = short(n.get("attached_node") or "")
        dst = re.search(r"ref\('([^']+)'\)", kw.get("to", ""))
        if dst and src.startswith("fact_") and dst.group(1).startswith(("dim_", "fact_")):
            rel.append((src, dst.group(1), kw.get("column_name", kw.get("field", ""))))
    cols = {n["name"]: list(n["columns"]) for n in m["nodes"].values()
            if n["resource_type"] == "model" and n["schema"] == "gold" and n["name"].startswith(("dim_", "fact_"))}
    lines = ['graph G {', 'layout=neato; overlap=false; splines=true; sep="+18";',
             'node [shape=box, style="rounded,filled", fontname="Arial", fontsize=13];', 'edge [color="#7a869a"];']
    for name in cols:
        color = "#f2c94c" if name.startswith("fact_") else "#cfe3f7"
        lines.append(f'"{name}" [fillcolor="{color}", label="{name}"];')
    for a, b, c in sorted(set(rel)):
        lines.append(f'"{a}" -- "{b}" [label="{c}", fontsize=8, fontname="Arial"];')
    lines.append("}")
    return "\n".join(lines), sorted(set(rel))
