"""
Goc nhin cua tung he thong nguon tren cac su kien that. Moi he thong chi thay mot phan, ghi theo dinh dang
va quy uoc rieng cua no, kem loi rieng. Day la noi tao ra "do ban" cua du lieu tho.
"""
from datetime import timedelta

from . import config as C
from .reference import (INGREDIENT_VN, MENU_VN, POS_CATEGORY_CODE, POS_NAME_VARIANTS, UNIT_VN,
                        app_product_ref)
from .world import pos_code


def _vnd_text(x):
    return f"{int(x):,}".replace(",", ".")


# ---------------------------------------------------------------- POS
def pos_receipts(world, b, d, orders):
    """Don tai quay (moi trang thai) + don san da hoan thanh ma nhan vien co nhap tay vao POS."""
    rng = world.rng
    ref = world.ref
    tier = ref.tier(b)
    prefix = ref.branches[b]["names"]["pos_terminal_prefix"]
    old = b in C.OLD_POS_BRANCHES
    entries = []
    for o in orders:
        if o["channel"] == "WALKIN":
            entries.append((o["ts"], o))
        elif o["channel"] in C.MARKETPLACES and o.get("pos_entered"):
            entries.append((o["ts"] + timedelta(minutes=o["prep_min"]), o))
    entries.sort(key=lambda e: e[0])

    n_term = C.TERMINALS_BY_TIER[tier]
    seq = {k: 0 for k in range(1, n_term + 1)}
    out = []
    for ts, o in entries:
        term_no = int(rng.integers(1, n_term + 1))
        seq[term_no] += 1
        terminal = f"{prefix}-{term_no:02d}"
        is_mkt = o["channel"] in C.MARKETPLACES
        lines = []
        for k, line in enumerate(o["items"], start=1):
            item = ref.menu[line["item_id"]]
            variants = POS_NAME_VARIANTS.get(line["item_id"], [item["item_name"]])
            lines.append({
                "line_id": k, "sku": f"SKU-{line['item_id']:03d}",
                "name_on_receipt": variants[int(rng.integers(len(variants)))],
                "category_code": POS_CATEGORY_CODE[item["category"]], "qty": line["qty"],
                "unit_price": line["unit_price"], "line_discount_amount": 0, "line_tax_amount": 0,
                "modifier_list": [[], [], [], ["extra_sauce"], ["no_ice"], ["extra_cheese"]][int(rng.integers(6))],
                "void_item_flag": False,
            })
        if is_mkt:
            pay, total, discount, code, rounding = f"{o['channel']}_TRANSFER", o["subtotal"], 0, None, 0
        else:
            pay, total, discount, code, rounding = (o["payment"], o["total"], o["discount_amount"],
                                                    o["discount_code"], o["rounding"])
        status = o["status"] if not is_mkt else "COMPLETED"
        is_void = status in ("VOID_NORMAL", "VOID_FRAUD")
        is_refund = status == "REFUNDED"
        loyalty = (not is_mkt) and o.get("loyalty")
        r = {
            "receipt_no": f"{terminal}-{d.strftime('%Y%m%d')}-{seq[term_no]:05d}",
            "terminal_id": terminal,
            "cashier_code": pos_code(o["cashier_id"]) if o.get("cashier_id") else None,
            "txn_time": ts.strftime("%Y-%m-%dT%H:%M:%S" if old else "%d/%m/%Y %H:%M:%S"),
            "shift_id": f"SHIFT-{terminal}-{d.strftime('%Y%m%d')}-{'AM' if ts.hour < 14 else 'PM'}",
            "order_source": "POS" if not is_mkt else o["channel"],
            "order_type": "DELIVERY_PICKUP" if is_mkt else ("DINE_IN" if rng.random() < 0.12 else "TAKEAWAY"),
            "table_number": None, "guest_count": None,
            "items": lines,
            "subtotal_amount": o["subtotal"], "tax_rate": 0, "tax_amount": 0, "service_charge_amount": 0,
            "tip_amount": 0, "rounding_adjustment": rounding,
            "discount_code": code, "discount_type": "percentage" if code else None, "discount_amount": discount,
            "coupon_id": None,
            "loyalty_member_phone_masked": f"09xxxxx{int(rng.integers(100, 1000))}" if loyalty else None,
            "loyalty_points_earned": int(total // 10000) if loyalty else None,
            "loyalty_points_redeemed": None,
            "payment_method": pay,
            "payment_reference_no": None if pay == "CASH" else f"REF{int(rng.integers(100000, 1000000))}",
            "card_last4": f"{int(rng.integers(1000, 10000))}" if pay == "CARD" else None,
            "void_flag": is_void,
            "void_reason": o.get("void_reason") if is_void else None,
            "void_by": pos_code(o["void_by"]) if is_void and o.get("void_by") else None,
            "void_timestamp": ((ts + timedelta(minutes=o["void_delay_min"])).strftime("%d/%m/%Y %H:%M:%S")
                               if is_void else None),
            "refund_flag": is_refund,
            "refund_amount": total if is_refund else 0,
            "refund_by": pos_code(o["refund_by"]) if is_refund and o.get("refund_by") else None,
            "pos_software_version": "v2.8.0" if old else "v3.2.1",
            "pos_device_id": f"DEV-{terminal}",
            "sync_status": rng.choice(["SYNCED", "PENDING", "FAILED"], p=[0.96, 0.03, 0.01]).item(),
            "sync_timestamp": (ts - timedelta(hours=7) + timedelta(seconds=int(rng.integers(1, 120)))).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "printed_flag": bool(o.get("printed", True)),
            "reprint_count": int(rng.choice([0, 1, 2], p=[0.93, 0.06, 0.01])),
            "currency": "VND",
            "notes": None if rng.random() < 0.9 else rng.choice(["khach yeu cau it da", "giao gap", "khach quen"]).item(),
            "branch_manager_on_duty": None,
            "total_paid": total,
        }
        if old:
            # POS v2.8: ten cot tong tien khac, tien la chuoi "125.000", chua co cac truong moi
            r["grand_total"] = _vnd_text(r.pop("total_paid"))
            for k in ("subtotal_amount", "discount_amount", "refund_amount"):
                r[k] = _vnd_text(r[k])
            for k in ("void_timestamp", "refund_by", "loyalty_points_redeemed", "sync_timestamp"):
                r.pop(k)
        out.append(r)
    return out


# ---------------------------------------------------------------- App rieng
APP_STATUS = {"COMPLETED": "DELIVERED", "STORE_CANCELLED": "CANCELLED_BY_STORE",
              "CUSTOMER_CANCELLED": "CANCELLED_BY_CUSTOMER", "REFUNDED": "REFUNDED"}


def app_orders(world, orders):
    rng = world.rng
    ref = world.ref
    out = []
    for o in orders:
        if o["channel"] != "APP":
            continue
        created_utc = o["ts"] - timedelta(hours=7)
        status = APP_STATUS[o["status"]]
        cancelled = status.startswith("CANCELLED")
        ready = None if o["status"] == "STORE_CANCELLED" else created_utc + timedelta(minutes=o["prep_min"])
        lines = [{"product_ref": app_product_ref(l["item_id"]), "product_name": MENU_VN[l["item_id"]],
                  "category_ref": f"CAT-{ref.menu[l['item_id']]['category'][:3].upper()}", "qty": l["qty"],
                  "price_vnd": l["unit_price"],
                  "modifiers": [[], [], ["extra_sauce"], ["no_ice"]][int(rng.integers(4))]} for l in o["items"]]
        total = o["subtotal"] + o["delivery_fee"] + o["packaging_fee"] + o["service_fee"] - o["promo_value"]
        out.append({
            "order_uuid": f"{world.book.seed:x}{o['order_seq']:09x}",
            "created_at_utc": created_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at_utc": (created_utc + timedelta(minutes=o["prep_min"] + float(rng.uniform(5, 30)))).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "kitchen_ready_at_utc": ready.strftime("%Y-%m-%dT%H:%M:%SZ") if ready else None,
            "branch_ref": {"code": ref.branches[o["branch_id"]]["names"]["owned_app_branch_code"],
                           "display_name": ref.branches[o["branch_id"]]["branch_name"]},
            "customer_id_hashed": f"{(o['customer_idx'] * 2654435761) % (1 << 64):016x}",
            "is_first_order_flag": o["is_first"],
            "customer_tier_display": rng.choice(["Bronze", "Bronze", "Silver", "Gold"]).item(),
            "platform": rng.choice(["iOS", "Android"]).item(),
            "app_version": rng.choice(["4.1.0", "4.1.0", "4.0.2", "3.9.8"]).item(),
            "device_os_version": rng.choice(["17.2", "16.5", "14", "13"]).item(),
            "line_items": lines,
            "subtotal": o["subtotal"], "delivery_fee": o["delivery_fee"], "packaging_fee": o["packaging_fee"],
            "service_fee": o["service_fee"],
            "promo_applied": {"code": o["promo_code"], "value": o["promo_value"]},
            "total_amount": total,
            "payment_method": rng.choice(["MOMO", "ZALOPAY", "CARD", "CASH_ON_DELIVERY"]).item(),
            "payment_status": "VOIDED" if cancelled else ("REFUNDED" if status == "REFUNDED" else "PAID"),
            "order_status": status,
            "cancel_reason": o.get("cancel_reason") if cancelled else None,
            "delivery_type": "PICKUP" if o["delivery_fee"] == 0 else "DELIVERY",
            "delivery_ward": f"Phuong {int(rng.integers(1, 16))}" if o["delivery_fee"] > 0 else None,
            "utm_source": rng.choice([None] * 12 + ["facebook_ads", "zalo_oa", "tiktok_ads"]),
            "utm_campaign": None,
            "session_id": f"{int(rng.integers(1 << 62)):016x}",
            "rating": o.get("rating"),
            "review_text": None,
            "notes_from_customer": None if rng.random() < 0.92 else rng.choice(["it da giup em", "giao truoc 12h"]).item(),
        })
    return out


# ---------------------------------------------------------------- Kho: so nhap & phieu kiem ke
def ingredient_name_as_written(world, ing, template):
    """Ten nguyen lieu nguoi quan ly go tay: mau A tieng Viet co dau, mau B khong dau; thinh thoang viet tat."""
    rng = world.rng
    vn, variants = INGREDIENT_VN[ing]
    if rng.random() < C.RECEIPT_NAME_VARIANT_RATE:
        return variants[int(rng.integers(len(variants)))]
    return vn if template == "A" else world.ref.ingredients[ing]["ingredient_name"]


def receipt_rows(world, b, rows):
    rng = world.rng
    template = "B" if b in C.RECEIPT_TEMPLATE_B_BRANCHES else "A"
    out = []
    for r in rows:
        qty = r["quantity"]
        if r["unit"] == "kg" and rng.random() < C.RECEIPT_KG_TYPO_RATE:
            qty = round(qty * 1000)  # go so gram vao cot kg
        out.append({"template": template,
                    "name": ingredient_name_as_written(world, r["ingredient_id"], template),
                    "unit": UNIT_VN[r["unit"]] if template == "A" else r["unit"],
                    "quantity": qty, "unit_price": r["unit_price"], "supplier": r["supplier"],
                    "expiry": r["expiry"], "date": r["date"]})
    return template, out
