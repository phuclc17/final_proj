"""Du lieu tham chieu cua the gioi: chi nhanh, mon, nguyen lieu, cong thuc, nhan vien, ten goi o tung he thong."""
import csv
import hashlib
import json
from collections import defaultdict

from . import config as C

INGREDIENT_VN = {
    1: ("Thịt gà tươi", ["Thit ga", "Gà tươi", "thịt gà"]),
    2: ("Thịt bò xay", ["Bo xay", "thịt bò"]),
    3: ("Tôm tươi", ["Thit tom", "Tôm"]),
    4: ("Rau xà lách", ["Xa lach", "Xà lách"]),
    5: ("Cà chua", ["Ca chua"]),
    6: ("Bắp cải", ["Bap cai"]),
    7: ("Trứng gà", ["Trung", "Trứng"]),
    8: ("Sữa tươi", ["Sua tuoi"]),
    9: ("Bột chiên giòn", ["Bot chien", "Bột chiên"]),
    10: ("Bánh burger", ["Banh burger", "Vỏ bánh burger"]),
    11: ("Khoai tây đông lạnh", ["Khoai tay DL", "Khoai tây"]),
    12: ("Cơm trắng", ["Com trang", "Gạo nấu"]),
    13: ("Mỳ Ý", ["My Y", "Mì Ý"]),
    14: ("Sốt cay Hàn Quốc", ["Sot cay HQ"]),
    15: ("Sốt mayonnaise", ["Mayonnaise", "Sot mayo"]),
    16: ("Phô mai lát", ["Pho mai", "Phô mai"]),
    17: ("Trân châu", ["Tran chau"]),
    18: ("Ly + ống hút + hộp đựng", ["Bao bì", "Ly ong hut hop"]),
    19: ("Pepsi lon", ["Pepsi"]),
    20: ("7Up lon", ["7up"]),
    21: ("Nước suối", ["Nuoc suoi", "Aquafina"]),
    22: ("Nguyên liệu pha chế trà/trà sữa", ["NL pha che", "Trà + đường"]),
}
UNIT_VN = {"kg": "kg", "qua": "quả", "lit": "lít", "cai": "cái", "bo": "bộ", "lon": "lon", "chai": "chai", "phan": "phần"}

MENU_VN = {
    1: "Gà Giòn Miếng Đơn", 2: "Gà Giòn Combo 2 Miếng", 3: "Gà Giòn Combo 4 Miếng", 4: "Burger Bò Deluxe",
    5: "Burger Gà Giòn Phô Mai", 6: "Burger Tôm", 7: "Cơm Gà Xốt Cay", 8: "Cơm Sườn Nướng", 9: "Mì Ý Sốt Bò",
    10: "Gà Sốt Cay Hàn Quốc", 11: "Gà Quay Nướng Mật Ong", 12: "Salad Gà Nướng", 13: "Khoai Tây Chiên (S)",
    14: "Khoai Tây Chiên (L)", 15: "Gà Popcorn", 16: "Súp Ngô", 17: "Salad Bắp Cải", 18: "Bánh Trứng Xù",
    19: "Pepsi Lon", 20: "7Up Lon", 21: "Trà Đào", 22: "Trà Sữa Trân Châu", 23: "Nước Cam Ép", 24: "Nước Suối",
    25: "Combo Gà Giòn 2 Miếng + Nước", 26: "Combo Burger Bò + Khoai + Nước", 27: "Combo Cơm Gà + Súp + Nước",
    28: "Combo Gia Đình 4 Người",
}
POS_NAME_VARIANTS = {
    14: ["Khoai Tay Chien L", "Khoai Tay (L)", "KT Chien Lon"],
    13: ["Khoai Tay Chien S", "Khoai Tay (S)", "KT Chien Nho"],
    1: ["Ga Gion Mieng Don", "Ga Gion 1M", "GA GION DON"],
}
POS_CATEGORY_CODE = {"Main": "MN", "Side": "SD", "Drink": "BV", "Combo": "CB"}


def _read(name):
    with open(C.REFERENCE_DIR / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def app_product_ref(item_id):
    return "PID-" + hashlib.sha1(f"app-catalog-{item_id}".encode()).hexdigest()[:6].upper()


class Reference:
    def __init__(self):
        names = {m["internal_branch_id"]: m for m in json.load(open(C.REFERENCE_DIR / "system_names.json", encoding="utf-8"))}
        self.branches = {}
        for b in _read("branches.csv"):
            bid = int(b["branch_id"])
            self.branches[bid] = {**b, "branch_id": bid, "tier": names[bid]["tier"], "names": names[bid]}
        self.menu = {int(m["item_id"]): {**m, "item_id": int(m["item_id"]), "price": int(m["price"]),
                                         "standard_cost": int(m["standard_cost"])} for m in _read("menu_items.csv")}
        self.ingredients = {int(i["ingredient_id"]): {**i, "ingredient_id": int(i["ingredient_id"]),
                                                      "unit_cost": float(i["unit_cost"]),
                                                      "shelf_life_days": int(i["shelf_life_days"])}
                            for i in _read("ingredients.csv")}
        self.recipes_raw = _read("recipes.csv")
        self.combos_raw = _read("combo_components.csv")
        self.staff = {int(s["staff_id"]): {"staff_id": int(s["staff_id"]), "staff_name": s["staff_name"],
                                           "branch_id": int(s["branch_id"]), "role": s["role"],
                                           "hourly_wage": int(s["hourly_wage"]), "hire_date": s["valid_from"]}
                      for s in _read("staff.csv")}
        self.full_recipe = self._explode_recipes()

    def _explode_recipes(self):
        atomic = defaultdict(dict)
        for r in self.recipes_raw:
            atomic[int(r["item_id"])][int(r["ingredient_id"])] = float(r["qty_per_unit"])
        full = {k: dict(v) for k, v in atomic.items()}
        for c in self.combos_raw:
            combo, comp, qty = int(c["combo_item_id"]), int(c["component_item_id"]), float(c["quantity"])
            full.setdefault(combo, {})
            for ing, per in atomic.get(comp, {}).items():
                full[combo][ing] = full[combo].get(ing, 0) + per * qty
        return full

    def tier(self, bid):
        return self.branches[bid]["tier"]
