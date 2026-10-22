"""Doc cau hinh kich ban va tra loi 'kich ban nao dang tac dong vao (chi nhanh, ngay) nay'."""
import json
from datetime import date

from . import config as C


class ScenarioBook:
    def __init__(self, profile):
        cfg = json.load(open(C.SCENARIO_DIR / f"{profile}.json", encoding="utf-8"))
        self.profile = profile
        self.seed = cfg["seed"]
        self.items = []
        for s in cfg["scenarios"]:
            s = dict(s)
            s["start"] = date.fromisoformat(s["start"])
            s["end"] = date.fromisoformat(s["end"])
            self.items.append(s)

    def active(self, kind, branch_id, d):
        for s in self.items:
            if s["type"] == kind and s["branch_id"] == branch_id and s["start"] <= d <= s["end"]:
                return s
        return None

    def overlapping(self, kind, branch_id, start, end):
        for s in self.items:
            if s["type"] == kind and s["branch_id"] == branch_id and s["start"] <= end and start <= s["end"]:
                return s
        return None

    def active_ids(self, branch_id, d):
        return [s["id"] for s in self.items if s["branch_id"] == branch_id and s["start"] <= d <= s["end"]]
