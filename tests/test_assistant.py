"""Kiem thu tro ly AI khong can goi mo hinh that: rao chan SQL, kiem tra con so co can cu, vong lap goi cong cu
(dung client gia lap tra ve tool_use roi cau tra loi)."""
from types import SimpleNamespace as NS

import pytest

from analytics import assistant as A


@pytest.mark.parametrize("sql", ["drop table gold.dim_date", "select 1; drop table x", "copy gold.dim_date to 'x.csv'",
                                 "with x as (select 1) delete from y", "pragma database_list", "attach 'a.db' as a"])
def test_sql_khong_phai_select_bi_chan(sql):
    with pytest.raises(ValueError):
        A.check_sql(sql)


def test_sql_select_hop_le_va_tu_khoa_trong_chuoi_duoc_phep():
    assert A.check_sql("select 'drop' as w;") == "select 'drop' as w"
    assert A.check_sql("WITH t AS (SELECT 1) SELECT * FROM t").startswith("WITH")


def test_kiem_tra_con_so_bat_duoc_so_bia():
    calls = [("trace_branch_week", {}, {"chenh_lech_vnd": -48314275, "chenh_lech_pct": -17.2, "aov_vnd": 85348})]
    found, total, missing = A.grounding("Thấp hơn kỳ vọng 48,3 triệu đ (17,2%), AOV 85.348 đ; "
                                        "tuần 06/05/2024; thiệt hại 120 triệu đ.", calls)
    assert (found, total) == (3, 4) and missing == ["120 triệu"]


class FakeClient:
    """Luot 1 goi list_tables, luot 2 tra loi bang van ban."""
    def __init__(self):
        self.calls = []
        self.messages = self

    def create(self, **kw):
        self.calls.append(kw)
        usage = NS(input_tokens=100, output_tokens=20, cache_read_input_tokens=0, cache_creation_input_tokens=0)
        if len(self.calls) == 1:
            return NS(stop_reason="tool_use", usage=usage,
                      content=[NS(type="tool_use", id="t1", name="list_tables", input={})])
        return NS(stop_reason="end_turn", usage=usage, content=[NS(type="text", text="Kho có 2 bảng.")])


class FakeBox:
    def run(self, name, args):
        assert name == "list_tables"
        return {"bang": [{"ten": "gold.a"}, {"ten": "gold.b"}]}


def test_vong_lap_goi_cong_cu_roi_tra_loi_va_giu_lich_su():
    client, messages = FakeClient(), [{"role": "user", "content": "Kho có bao nhiêu bảng?"}]
    turn = A.ask(client, A.MODEL, {}, "he thong", messages, FakeBox())
    assert turn.answer == "Kho có 2 bảng." and [c[0] for c in turn.calls] == ["list_tables"]
    # lich su noi them (append-only): cau hoi, luot goi cong cu, ket qua cong cu, cau tra loi
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    assert messages[2]["content"][0]["tool_use_id"] == "t1"
    assert all(t.get("strict") for t in client.calls[0]["tools"])
    assert turn.input_tokens == 200 and turn.output_tokens == 40


def test_loi_cong_cu_tra_ve_cho_mo_hinh_khong_lam_dung_vong_lap():
    class BadBox:
        def run(self, name, args):
            raise ValueError("Không có cột xyz")
    turn = A.ask(FakeClient(), A.MODEL, {}, "he thong", [{"role": "user", "content": "?"}], BadBox())
    assert turn.calls[0][2] == {"loi": "Không có cột xyz"} and turn.answer == "Kho có 2 bảng."
