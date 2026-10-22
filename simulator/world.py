"""
The gioi Fast&Fat: moi ngay sinh ra cac SU KIEN THAT (khach dat don, ai lam ca, bep tai bao nhieu,
nguyen lieu dung bao nhieu, giao hang, kiem ke). Cac he thong nguon (POS, App, san, kho, cham cong)
chi la GOC NHIN cua cac su kien nay - xem views.py.

Chuoi nhan qua chinh:
  nhan su ca -> tai bep (util) -> thoi gian chuan bi -> khach tai quay bo di / cua hang huy don / rating
  -> rating tuan -> thu hang tren san -> so don san tuan sau -> doanh thu
"""
from datetime import datetime, timedelta

import numpy as np

from . import config as C
from .reference import Reference


class World:
    def __init__(self, book):
        self.book = book
        self.rng = np.random.default_rng(book.seed)
        self.ref = Reference()
        self.day_idx = 0
        self.order_seq = 0
        self.batch_seq = 0
        self.branch_ids = sorted(self.ref.branches)
        self.prices = {i: m["price"] for i, m in self.ref.menu.items()}
        self.staff = {sid: dict(s) for sid, s in self.ref.staff.items()}
        self.branch_level = {b: float(np.exp(self.rng.normal(0, C.BRANCH_LEVEL_SD))) for b in self.branch_ids}
        self.hour_p = np.array([C.HOUR_WEIGHT[h] for h in C.OPEN_HOURS])
        self.hour_p = self.hour_p / self.hour_p.sum()
        self._init_items()
        self._assign_shift_prefs()
        self._init_customers()
        self.capacity = {b: self._calibrate_capacity(b) for b in self.branch_ids}
        self.usage_hist, self.stock = {}, {}
        for (b, ing), u in self._expected_usage().items():
            cat = self.ref.ingredients[ing]["category"]
            self.usage_hist[(b, ing)] = [u]
            self.stock[(b, ing)] = u * C.INITIAL_STOCK_DAYS[cat]
        self.rating = {(b, p): C.RANKING_REF_RATING for b in self.branch_ids for p in C.MARKETPLACES}
        self.mkt_mult = {(b, p): 1.0 for b in self.branch_ids for p in C.MARKETPLACES}
        self.week_acc = self._empty_week()
        self._resolve_fraud_cashiers()

    # ------------------------------------------------------------------ khoi tao
    def _init_items(self):
        self.item_ids = sorted(self.ref.menu)
        rank = {item: r for r, item in enumerate(C.ITEM_POPULARITY_RANK, start=1)}
        w = np.array([1.0 / rank[i] ** C.ITEM_ZIPF_EXPONENT for i in self.item_ids])
        self.item_p = w / w.sum()

    def _assign_shift_prefs(self):
        for b in self.branch_ids:
            for role in ("Kitchen", "Cashier", "ShiftManager"):
                members = sorted((s for s in self.staff.values() if s["branch_id"] == b and s["role"] == role),
                                 key=lambda s: s["staff_id"])
                for k, s in enumerate(members):
                    if role == "ShiftManager" and len(members) == 1:
                        s["shift_pref"] = "flex"
                    else:
                        s["shift_pref"] = "morning" if k % 2 == 0 else "evening"

    def _init_customers(self):
        n = C.N_CUSTOMERS
        branch_w = np.array([C.TIER_BASE_ORDERS[self.ref.tier(b)] for b in self.branch_ids], dtype=float)
        self.cust_home = self.rng.choice(self.branch_ids, size=n, p=branch_w / branch_w.sum())
        zipf = 1.0 / ((np.arange(n) % 500 + 1) ** 1.1)
        self.cust_all_p = zipf / zipf.sum()
        self.cust_has_ordered = np.zeros(n, dtype=bool)
        self.cust_pool = {}
        for b in self.branch_ids:
            idx = np.where(self.cust_home == b)[0]
            self.cust_pool[b] = (idx, zipf[idx] / zipf[idx].sum())

    def _calibrate_capacity(self, b):
        """Nang luc bep (don/nhan vien bep/gio): ngay dong nhat, ca chi co so bep toi thieu thi tai 95%."""
        tier = self.ref.tier(b)
        peak_share = 3.0 / sum(C.HOUR_WEIGHT.values())
        demand_peak = C.TIER_BASE_ORDERS[tier] * self.branch_level[b] * max(C.WEEKDAY_FACTOR) * peak_share
        return demand_peak / (C.MIN_KITCHEN_BY_TIER[tier] * C.UTIL_AT_MIN_COVERAGE)

    def _expected_usage(self):
        items_k, items_p = C.ITEMS_PER_ORDER
        qty_k, qty_p = C.QTY_PER_LINE
        lines_per_order = sum(k * p for k, p in zip(items_k, items_p)) * sum(k * p for k, p in zip(qty_k, qty_p))
        per_order = {}
        for item, p in zip(self.item_ids, self.item_p):
            for ing, q in self.ref.full_recipe.get(item, {}).items():
                per_order[ing] = per_order.get(ing, 0.0) + p * lines_per_order * q
        avg_weekday = sum(C.WEEKDAY_FACTOR) / 7
        usage = {}
        for b in self.branch_ids:
            orders = C.TIER_BASE_ORDERS[self.ref.tier(b)] * self.branch_level[b] * avg_weekday
            for ing in self.ref.ingredients:
                usage[(b, ing)] = max(per_order.get(ing, 0.0) * orders, 0.01)
        return usage

    def reload_scenarios(self, book):
        """Thay so kich ban (chi dung cho tap van hanh thu). Kich ban gian lan da gan thu ngan thi giu nguyen."""
        old = {s["id"]: s for s in self.book.items}
        for s in book.items:
            for k in ("resolved_staff_id", "resolved_pos_code"):
                if s["id"] in old and k in old[s["id"]]:
                    s[k] = old[s["id"]][k]
        self.book = book
        self._resolve_fraud_cashiers()

    def _resolve_fraud_cashiers(self):
        self.fraud_cashier = {}
        for s in self.book.items:
            if s["type"] != "cashier_void_fraud":
                continue
            if "resolved_staff_id" in s:          # da gan tu truoc (nap lai kich ban): giu nguyen nguoi cu
                self.fraud_cashier[s["id"]] = s["resolved_staff_id"]
                continue
            cashiers = sorted((st for st in self.staff.values()
                               if st["branch_id"] == s["branch_id"] and st["role"] == "Cashier"),
                              key=lambda st: st["staff_id"])
            sid = cashiers[s["cashier_rank"]]["staff_id"]
            s["resolved_staff_id"] = sid
            s["resolved_pos_code"] = pos_code(sid)
            self.fraud_cashier[s["id"]] = sid

    def _empty_week(self):
        keys = ("completed", "cancelled", "store_cancelled", "gross", "merchant_promo",
                "prep_sum", "prep_n", "rating_sum", "rating_n")
        return {(b, p): dict.fromkeys(keys, 0.0) for b in self.branch_ids for p in C.MARKETPLACES}

    # ------------------------------------------------------------------ 1 ngay
    def current_date(self):
        return C.START_DATE + timedelta(days=self.day_idx)

    def simulate_day(self):
        d = self.current_date()
        out = {"date": d, "orders": {}, "punches": {}, "receipts": {}, "counts": {}, "settlement": None,
               "weather": None, "master": [], "truth": []}
        self._apply_master_changes(d, out)

        wet = d.month in C.WET_SEASON_MONTHS
        rain = bool(self.rng.random() < C.RAIN_PROB["wet" if wet else "dry"])
        out["weather"] = {
            "date": d.isoformat(), "location": "Ho Chi Minh City",
            "precipitation_mm": round(float(self.rng.gamma(2.0, 9.0)), 1) if rain else 0.0,
            "condition": "Rain" if rain else self.rng.choice(["Sunny", "Partly cloudy", "Cloudy"]).item(),
            "temp_max_c": round(float(self.rng.normal(31 if wet else 33, 1.2)), 1),
        }
        holiday = C.HOLIDAYS.get(d)
        is_count_day = self.day_idx % C.COUNT_EVERY_DAYS == C.COUNT_EVERY_DAYS - 1

        for b in self.branch_ids:
            self._simulate_branch_day(b, d, rain, holiday, is_count_day, out)
        if d.weekday() == 6:
            self._close_week(d, out)
        self.day_idx += 1
        return out

    def _apply_master_changes(self, d, out):
        if self.day_idx == 0:
            out["master"] = ["branches", "menu_items", "app_catalog", "ingredients", "recipes", "combo_components",
                             "staff", "marketplace_contracts"]
        if d in C.PRICE_CHANGES:
            self.prices.update(C.PRICE_CHANGES[d])
            out["master"] += ["menu_items", "app_catalog"]
        for ch in C.STAFF_CHANGES:
            if ch["date"] == d:
                self.staff[ch["staff_id"]].update(role=ch["role"], hourly_wage=ch["hourly_wage"])
                out["master"].append("staff")

    # ------------------------------------------------------------------ chi nhanh x ngay
    def _simulate_branch_day(self, b, d, rain, holiday, is_count_day, out):
        rng = self.rng
        tier = self.ref.tier(b)
        out["receipts"][b] = self._morning_deliveries(b, d)

        roster = self._roster(b, d)
        out["punches"][b], labor_hours, labor_cost = self._punches(b, d, roster)
        kitchen_h, cashiers_h, managers_h = self._coverage(roster)

        noise = float(np.exp(rng.normal(0, C.DAILY_NOISE_SD)))
        base = C.TIER_BASE_ORDERS[tier] * self.branch_level[b] * C.WEEKDAY_FACTOR[d.weekday()] * noise
        hourly = {}
        for ch in C.CHANNELS:
            lam = base * C.CHANNEL_MIX[ch]
            if holiday:
                lam *= C.HOLIDAY_FACTOR[ch]
            if rain:
                lam *= C.RAIN_FACTOR[ch]
            if ch in C.MARKETPLACES:
                lam *= self.mkt_mult[(b, ch)]
            hourly[ch] = rng.multinomial(rng.poisson(lam), self.hour_p)

        t = {"date": d.isoformat(), "branch_id": b, "rain": int(rain), "holiday": int(bool(holiday)),
             "orders_demand": 0, "walkin_balked": 0, "balked_value": 0, "store_cancelled": 0,
             "store_cancelled_value": 0, "customer_cancelled": 0, "orders_served": 0, "served_value": 0,
             "fraud_void_count": 0, "fraud_void_value": 0, "mkt_not_entered": 0, "mkt_not_entered_value": 0,
             "peak_util": 0.0, "prep_sum": 0.0, "prep_n": 0}
        for ch in C.CHANNELS:
            t[f"served_{ch.lower()}"] = 0

        orders = []
        ctx = {"fraud": self.book.active("cashier_void_fraud", b, d),
               "miss": self.book.active("marketplace_not_entered", b, d)}
        for hi, h in enumerate(C.OPEN_HOURS):
            n_h = int(sum(hourly[ch][hi] for ch in C.CHANNELS))
            kitchen = kitchen_h[h]
            util = n_h / (self.capacity[b] * kitchen) if kitchen > 0 else 5.0
            rho = min(util, C.UTIL_CAP)
            prep_mean = C.PREP_BASE + C.PREP_SCALE / (1 - rho) ** C.PREP_POWER
            balk = min(C.BALK_MAX, C.BALK_SLOPE * max(0.0, util - C.BALK_START))
            p_store_cancel = C.STORE_CANCEL_BASE + C.STORE_CANCEL_SLOPE * max(0.0, util - C.STORE_CANCEL_START)
            t["peak_util"] = max(t["peak_util"], round(util, 3))
            for ch in C.CHANNELS:
                for _ in range(int(hourly[ch][hi])):
                    o = self._new_order(b, d, h, ch, prep_mean, balk, p_store_cancel,
                                        cashiers_h[h], managers_h[h], roster, ctx, t)
                    if o is not None:
                        orders.append(o)
        out["orders"][b] = orders

        waste_value, theft_value = self._consume(b, d, orders)
        if is_count_day:
            out["counts"][b] = self._count(b)
        for o in orders:
            if o["channel"] in C.MARKETPLACES:
                self._accumulate_week(o)

        prep_avg = t.pop("prep_sum") / max(t.pop("prep_n"), 1)
        t.update(avg_prep_min=round(prep_avg, 2), waste_excess_value=round(waste_value),
                 theft_value=round(theft_value), labor_hours=round(labor_hours, 2), labor_cost=round(labor_cost),
                 kitchen_evening=kitchen_h[19], kitchen_morning=kitchen_h[12],
                 mkt_mult_grab=round(self.mkt_mult[(b, "GRABFOOD")], 3),
                 mkt_mult_shopee=round(self.mkt_mult[(b, "SHOPEEFOOD")], 3),
                 scenario_ids=";".join(self.book.active_ids(b, d)))
        out["truth"].append(t)

    # ------------------------------------------------------------------ nhan su
    def _roster(self, b, d):
        wd = d.weekday()
        members = [s for s in self.staff.values() if s["branch_id"] == b]
        roster = {}
        for s in members:
            if self.rng.random() > C.ATTENDANCE_BY_WEEKDAY[wd]:
                continue
            pref = s["shift_pref"]
            roster[s["staff_id"]] = ("morning" if self.rng.random() < 0.5 else "evening") if pref == "flex" else pref

        need = C.MIN_KITCHEN_BY_TIER[self.ref.tier(b)]
        for window in ("morning", "evening"):
            have = sum(1 for sid, sh in roster.items() if sh == window and self.staff[sid]["role"] == "Kitchen")
            off = sorted((s for s in members if s["role"] == "Kitchen" and s["staff_id"] not in roster),
                         key=lambda s: s["shift_pref"] != window)
            for s in off[:max(0, need - have)]:
                roster[s["staff_id"]] = window

        under = self.book.active("evening_understaffing", b, d)
        if under:
            for sid, sh in roster.items():
                if sh == "evening" and self.staff[sid]["role"] != "ShiftManager" and self.rng.random() < under["move_share"]:
                    roster[sid] = "morning"
        return [(self.staff[sid], sh) for sid, sh in roster.items()]

    def _coverage(self, roster):
        kitchen = {h: 0.0 for h in C.OPEN_HOURS}
        cashiers = {h: [] for h in C.OPEN_HOURS}
        managers = {h: [] for h in C.OPEN_HOURS}
        for s, shift in roster:
            hours = C.MORNING_HOURS if shift == "morning" else C.EVENING_HOURS
            for h in hours:
                if s["role"] == "Kitchen":
                    kitchen[h] += 1
                elif s["role"] == "Cashier":
                    cashiers[h].append(s["staff_id"])
                else:
                    kitchen[h] += 0.5
                    managers[h].append(s["staff_id"])
        return kitchen, cashiers, managers

    def _punches(self, b, d, roster):
        rows, hours_total, cost_total = [], 0.0, 0.0
        for s, shift in roster:
            (sh, sm), (eh, em) = C.SHIFT_TIMES[shift]
            cin = datetime(d.year, d.month, d.day, sh, sm) + timedelta(minutes=float(self.rng.normal(0, 6)))
            cout = datetime(d.year, d.month, d.day, eh, em) + timedelta(minutes=abs(float(self.rng.normal(8, 8))))
            hours = (cout - cin).total_seconds() / 3600
            hours_total += hours
            cost_total += hours * s["hourly_wage"]
            rows.append({"staff_id": s["staff_id"], "event_type": "CHECK_IN", "event_time": cin})
            if self.rng.random() < C.TK_DUP_RATE:
                rows.append({"staff_id": s["staff_id"], "event_type": "CHECK_IN",
                             "event_time": cin + timedelta(seconds=int(self.rng.integers(20, 90)))})
            if self.rng.random() >= C.TK_MISSING_OUT_RATE:
                rows.append({"staff_id": s["staff_id"], "event_type": "CHECK_OUT", "event_time": cout})
        rows.sort(key=lambda r: r["event_time"])
        return rows, hours_total, cost_total

    # ------------------------------------------------------------------ don hang
    def _pick_items(self):
        rng = self.rng
        k = int(rng.choice(C.ITEMS_PER_ORDER[0], p=C.ITEMS_PER_ORDER[1]))
        idx = rng.choice(len(self.item_ids), size=k, replace=False, p=self.item_p)
        items = []
        for i in idx:
            item = self.item_ids[int(i)]
            qty = int(rng.choice(C.QTY_PER_LINE[0], p=C.QTY_PER_LINE[1]))
            items.append({"item_id": item, "qty": qty, "unit_price": self.prices[item]})
        return items

    def _pick_one(self, ids):
        return int(ids[int(self.rng.integers(len(ids)))]) if ids else None

    def _new_order(self, b, d, h, ch, prep_mean, balk, p_store_cancel, cashiers, managers, roster, ctx, t):
        rng = self.rng
        items = self._pick_items()
        subtotal = sum(i["qty"] * i["unit_price"] for i in items)
        t["orders_demand"] += 1
        if ch == "WALKIN" and rng.random() < balk:
            t["walkin_balked"] += 1
            t["balked_value"] += subtotal
            return None

        self.order_seq += 1
        ts = datetime(d.year, d.month, d.day, h, int(rng.integers(60)), int(rng.integers(60)))
        prep = round(max(2.0, float(rng.normal(prep_mean, prep_mean * 0.25))), 1)
        o = {"order_seq": self.order_seq, "branch_id": b, "channel": ch, "ts": ts, "items": items,
             "subtotal": subtotal, "prep_min": prep, "consumed": 1.0}
        any_staff = [s["staff_id"] for s, _ in roster]
        if ch == "WALKIN":
            self._walkin_details(o, cashiers, managers, any_staff, ctx, t)
        else:
            self._delivery_details(o, b, prep, p_store_cancel, cashiers, managers, any_staff, ctx, t)
        if o["status"] in ("COMPLETED", "REFUNDED", "VOID_FRAUD"):
            t["orders_served"] += 1
            t["served_value"] += subtotal
            t[f"served_{ch.lower()}"] += 1
            t["prep_sum"] += prep
            t["prep_n"] += 1
        return o

    def _walkin_details(self, o, cashiers, managers, any_staff, ctx, t):
        rng = self.rng
        cashier = self._pick_one(cashiers) or self._pick_one(managers) or self._pick_one(any_staff)
        manager = self._pick_one(managers)
        pay = rng.choice(["CASH", "CARD", "MOMO", "ZALOPAY"], p=[0.45, 0.15, 0.25, 0.15]).item()
        has_combo = any(self.ref.menu[i["item_id"]]["category"] == "Combo" for i in o["items"])
        code, pct = None, 0.0
        if has_combo and rng.random() < C.COMBO_DISCOUNT_RATE:
            code, pct = "COMBO10", 0.10
        elif rng.random() < C.STAFF_MEAL_RATE:
            code, pct = "STAFF20", 0.20
        discount = int(round(o["subtotal"] * pct, -2))
        total = o["subtotal"] - discount
        rounding = int(round(total, -3) - total) if pay == "CASH" else 0
        o.update(payment=pay, cashier_id=cashier, discount_code=code, discount_amount=discount,
                 rounding=rounding, total=total + rounding, loyalty=bool(rng.random() < C.LOYALTY_RATE),
                 void_by=None, void_delay_min=None, refund_by=None)

        fraud = ctx["fraud"]
        if (fraud and pay == "CASH" and cashier == fraud["resolved_staff_id"]
                and rng.random() < fraud["fraud_rate"]):
            o.update(status="VOID_FRAUD", void_by=cashier, void_reason="CUSTOMER_CANCEL", printed=True,
                     void_delay_min=float(rng.uniform(3, 15)))
            t["fraud_void_count"] += 1
            t["fraud_void_value"] += o["total"]
        elif rng.random() < C.NORMAL_VOID_RATE:
            by = manager if (manager and rng.random() < 0.9) else cashier
            o.update(status="VOID_NORMAL", void_by=by, consumed=0.0, printed=bool(rng.random() < 0.3),
                     void_reason=rng.choice(["CUSTOMER_CANCEL", "WRONG_ORDER", "SYSTEM_ERROR"]).item(),
                     void_delay_min=float(rng.uniform(0, 2)))
        elif rng.random() < C.REFUND_RATE:
            o.update(status="REFUNDED", refund_by=manager or cashier, printed=True, void_reason=None)
        else:
            o.update(status="COMPLETED", printed=True, void_reason=None)

    def _delivery_details(self, o, b, prep, p_store_cancel, cashiers, managers, any_staff, ctx, t):
        rng = self.rng
        ch = o["channel"]
        if rng.random() < p_store_cancel:
            o.update(status="STORE_CANCELLED", consumed=0.0,
                     cancel_reason="STORE_TOO_BUSY" if rng.random() < 0.8 else "OUT_OF_STOCK")
            t["store_cancelled"] += 1
            t["store_cancelled_value"] += o["subtotal"]
        elif rng.random() < C.CUST_CANCEL_BASE + C.CUST_CANCEL_SLOPE * max(0.0, prep - C.CUST_CANCEL_PREP_START):
            o.update(status="CUSTOMER_CANCELLED", consumed=0.5,
                     cancel_reason="WAITING_TOO_LONG" if prep > 25 else "CUSTOMER_CHANGED_MIND")
            t["customer_cancelled"] += 1
        elif ch == "APP" and rng.random() < 0.012:
            o.update(status="REFUNDED", cancel_reason=None)
        else:
            o.update(status="COMPLETED", cancel_reason=None)

        o["rating"] = None
        if o["status"] == "COMPLETED" and rng.random() < C.RATING_SHARE:
            mean = C.RATING_BASE - C.RATING_PREP_SLOPE * max(0.0, prep - C.RATING_PREP_START)
            o["rating"] = int(min(5, max(1, round(float(rng.normal(mean, C.RATING_SD))))))

        if ch in C.MARKETPLACES:
            promo = int(rng.integers(10, 21)) * 1000 if rng.random() < C.MKT_PROMO_SHARE else 0
            o["mkt_promo"] = promo
            o["merchant_promo"] = int(promo * C.MKT_PROMO_MERCHANT_SHARE)
            miss = ctx["miss"]["miss_rate"] if ctx["miss"] else C.POS_MISS_MARKETPLACE
            o["pos_entered"] = o["status"] == "COMPLETED" and rng.random() >= miss
            if o["status"] == "COMPLETED" and not o["pos_entered"]:
                t["mkt_not_entered"] += 1
                t["mkt_not_entered_value"] += o["subtotal"]
            o["cashier_id"] = self._pick_one(cashiers) or self._pick_one(managers) or self._pick_one(any_staff)
        else:
            self._app_customer(o, b)

    def _app_customer(self, o, b):
        rng = self.rng
        if rng.random() < 0.85:
            idx, p = self.cust_pool[b]
            c = int(rng.choice(idx, p=p))
        else:
            c = int(rng.choice(len(self.cust_all_p), p=self.cust_all_p))
        first = not bool(self.cust_has_ordered[c])
        self.cust_has_ordered[c] = True
        delivery_fee = int(rng.choice([0, 0, 15000, 20000]))
        promo_code = rng.choice([None] * 10 + ["APPWELCOME", "FREESHIP20K"])
        promo_value = 0
        if promo_code == "APPWELCOME" and first:
            promo_value = int(round(o["subtotal"] * 0.15, -2))
        elif promo_code == "FREESHIP20K":
            promo_value = min(delivery_fee, 20000)
        o.update(customer_idx=c, is_first=first, delivery_fee=delivery_fee,
                 packaging_fee=int(rng.choice([0, 0, 0, 3000])), service_fee=int(round(o["subtotal"] * 0.02, -2)),
                 promo_code=promo_code, promo_value=promo_value)

    # ------------------------------------------------------------------ kho
    def _avg_usage(self, b, ing):
        h = self.usage_hist[(b, ing)]
        return sum(h) / len(h)

    def _morning_deliveries(self, b, d):
        rng, wd, rows = self.rng, d.weekday(), []
        for ing, info in self.ref.ingredients.items():
            cat = info["category"]
            if (cat == "fresh" and wd not in C.FRESH_DELIVERY_WEEKDAYS) or (cat == "dry" and wd not in C.DRY_DELIVERY_WEEKDAYS):
                continue
            avg = self._avg_usage(b, ing)
            cover = C.COVER_DAYS["fresh_saturday"] if (cat == "fresh" and wd == 5) else C.COVER_DAYS[cat]
            stock = self.stock[(b, ing)]
            if stock >= avg * min(C.REORDER_DAYS[cat], cover * 0.8):
                continue
            qty = avg * cover - stock
            qty = round(qty, 1) if info["unit"] in ("kg", "lit") else float(np.ceil(qty))
            if qty <= 0:
                continue
            self.stock[(b, ing)] += qty
            self.batch_seq += 1
            price = round(info["unit_cost"] * (1 + float(rng.normal(0, C.SUPPLIER_PRICE_NOISE))), -2)
            rows.append({"batch_no": f"B{self.batch_seq:07d}", "date": d, "ingredient_id": ing, "quantity": qty,
                         "unit": info["unit"], "unit_price": int(price),
                         "supplier": C.SUPPLIERS[cat][int(rng.integers(len(C.SUPPLIERS[cat])))],
                         "expiry": d + timedelta(days=info["shelf_life_days"])})
        return rows

    def _consume(self, b, d, orders):
        rng = self.rng
        theo = {}
        for o in orders:
            if o["consumed"] <= 0:
                continue
            for line in o["items"]:
                for ing, q in self.ref.full_recipe.get(line["item_id"], {}).items():
                    theo[ing] = theo.get(ing, 0.0) + q * line["qty"] * o["consumed"]
        waste_sc = self.book.active("fresh_waste", b, d)
        theft_sc = self.book.active("stock_theft", b, d)
        waste_value = theft_value = 0.0
        for ing, info in self.ref.ingredients.items():
            cat = info["category"]
            need = theo.get(ing, 0.0)
            factor = float(rng.uniform(*C.WASTE_FACTOR[cat]))
            if waste_sc and cat == "fresh":
                factor *= float(rng.uniform(waste_sc["factor_min"], waste_sc["factor_max"]))
            actual = need * factor
            waste_value += (actual - need) * info["unit_cost"]
            stock = self.stock[(b, ing)] - actual
            if theft_sc and ing in theft_sc["ingredient_ids"] and stock > 0:
                stolen = stock * theft_sc["daily_rate"]
                stock -= stolen
                theft_value += stolen * info["unit_cost"]
            self.stock[(b, ing)] = max(stock, 0.0)
            hist = self.usage_hist[(b, ing)]
            hist.append(max(actual, 0.01))
            if len(hist) > 7:
                hist.pop(0)
        return waste_value, theft_value

    def _count(self, b):
        rows = []
        for ing, info in self.ref.ingredients.items():
            true = self.stock[(b, ing)]
            counted = true * (1 + float(self.rng.normal(0, C.COUNT_NOISE_SD)))
            counted = round(counted, 1) if info["unit"] in ("kg", "lit") else float(round(counted))
            rows.append({"ingredient_id": ing, "true_stock": round(true, 2),
                         "counted": None if self.rng.random() < C.COUNT_BLANK_RATE else max(counted, 0.0)})
        return rows

    # ------------------------------------------------------------------ doi soat san theo tuan
    def _accumulate_week(self, o):
        a = self.week_acc[(o["branch_id"], o["channel"])]
        if o["status"] == "COMPLETED":
            a["completed"] += 1
            a["gross"] += o["subtotal"]
            a["merchant_promo"] += o["merchant_promo"]
            a["prep_sum"] += o["prep_min"]
            a["prep_n"] += 1
            if o["rating"] is not None:
                a["rating_sum"] += o["rating"]
                a["rating_n"] += 1
        else:
            a["cancelled"] += 1
            if o["status"] == "STORE_CANCELLED":
                a["store_cancelled"] += 1

    def _close_week(self, d, out):
        rng = self.rng
        week_start = d - timedelta(days=6)
        rows = {p: [] for p in C.MARKETPLACES}
        for (b, p), a in self.week_acc.items():
            rate = C.COMMISSION_CONTRACT[p]
            sc = self.book.overlapping("commission_overcharge", b, week_start, d)
            if sc and sc["platform"] == p:
                rate = sc["actual_rate"]
            gross = int(a["gross"])
            commission = int(round(gross * rate))
            ads = int(round(gross * C.ADS_RATE)) if b in C.ADS_BRANCHES else 0
            adjustment = int(rng.choice([0, 0, 0, -50000, 80000]))
            promo = int(a["merchant_promo"])
            week_rating = a["rating_sum"] / a["rating_n"] if a["rating_n"] else self.rating[(b, p)]
            cancel_rate = a["store_cancelled"] / max(a["completed"] + a["cancelled"], 1)
            new_rating = ((1 - C.RATING_EMA) * self.rating[(b, p)]
                          + C.RATING_EMA * (week_rating - C.RATING_CANCEL_PENALTY * cancel_rate))
            self.rating[(b, p)] = new_rating
            self.mkt_mult[(b, p)] = min(C.RANKING_MAX, max(C.RANKING_MIN,
                                        1 + C.RANKING_SLOPE * (new_rating - C.RANKING_REF_RATING)))
            rows[p].append({"branch_id": b, "orders_completed": int(a["completed"]),
                            "orders_cancelled": int(a["cancelled"]), "gross_sales": gross, "commission": commission,
                            "commission_rate_applied": rate, "ads_spend": ads, "merchant_promo": promo,
                            "adjustment": adjustment, "net_payout": gross - commission - ads - promo + adjustment,
                            "avg_prep_min": round(a["prep_sum"] / max(a["prep_n"], 1), 1),
                            "store_rating": round(new_rating, 1)})
        out["settlement"] = {"week_start": week_start, "week_end": d, "rows": rows}
        self.week_acc = self._empty_week()


def pos_code(staff_id):
    return f"NV{staff_id:04d}"
