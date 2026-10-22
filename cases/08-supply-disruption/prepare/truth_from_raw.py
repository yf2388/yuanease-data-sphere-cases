"""直接从 Brunel 原始文件 Supply chain logisitcs problem.xlsx 独立重算本案例全部问答题的标准答案，并与 questions.yaml 的 expected 比对。

不经过 data/ 与 SQL：只用原始工作表与列名、Python 标准库计算，用来证明标准答案出自原始数据。
另外核对 data/订单.csv 与原始 OrderList 工作表逐行相同（只换了列名、日期写成 YYYY-MM-DD）。

用法：python3 -I truth_from_raw.py <Supply chain logisitcs problem.xlsx>（需要 openpyxl 与 PyYAML）
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import openpyxl
import yaml

CASE = Path(__file__).resolve().parent.parent
OUT = "PLANT08"


def sheet(book, name):
    rows = [r for r in book[name].iter_rows(values_only=True) if any(v is not None for v in r)]
    keep = [i for i, h in enumerate(rows[0]) if h is not None]
    return [{rows[0][i]: r[i] for i in keep} for r in rows[1:]]


def main(src: str) -> int:
    book = openpyxl.load_workbook(src, read_only=True, data_only=True)
    orders, caps, costs = sheet(book, "OrderList"), sheet(book, "WhCapacities"), sheet(book, "WhCosts")
    pp, vmi = sheet(book, "ProductsPerPlant"), sheet(book, "VmiCustomers")
    with open(CASE / "data" / "订单.csv", encoding="utf-8-sig", newline="") as fh:
        ours = list(csv.reader(fh))[1:]
    assert len(ours) == len(orders) and all(
        [str(o[k]) if k != "Order Date" else o[k].date().isoformat() for k in o] == r for o, r in zip(orders, ours)), "data/订单.csv 与原始工作表不一致"

    plants_of = defaultdict(set)
    for r in pp:
        plants_of[r["Product ID"]].add(r["Plant Code"])
    cap = {r["Plant ID"]: r["Daily Capacity "] for r in caps}
    by_plant, qty_out = defaultdict(int), defaultdict(int)
    for o in orders:
        by_plant[o["Plant Code"]] += 1
        if o["Plant Code"] == OUT:
            qty_out[o["Product ID"]] += o["Unit quantity"]
    out = [o for o in orders if o["Plant Code"] == OUT]
    p12 = [o for o in orders if o["Plant Code"] == "PLANT12"]
    top_plant = max(by_plant, key=by_plant.get)
    top_prod = max(qty_out, key=qty_out.get)
    svc, vmi_n = defaultdict(int), defaultdict(int)
    for o in orders:
        svc[o["Service Level"]] += 1
    for r in vmi:
        vmi_n[r["Plant Code"]] += 1
    top_cap = max(caps, key=lambda r: r["Daily Capacity "])
    top_cost = max(costs, key=lambda r: r["Cost/unit"])
    v444 = [o for o in orders if o["Carrier"] == "V444_0"]
    port04 = sum(o["Origin Port"] == "PORT04" for o in orders)
    truth = {
        "q01": [[min(o["Order Date"] for o in orders).date().isoformat(), max(o["Order Date"] for o in orders).date().isoformat(),
                 len(orders), len({o["Customer"] for o in orders}), len({o["Product ID"] for o in orders})]],
        "q02": [[len(by_plant), top_plant, by_plant[top_plant]]],
        "q03": [[len(p12), sum(o["Unit quantity"] for o in p12), len({o["Customer"] for o in p12})]],
        "q04": [[len(qty_out), p] for p in sorted(qty_out) if not plants_of[p] - {OUT}],
        "q05": [[sum(o["Ship Late Day count"] > 0 for o in out)]],
        "q06": [[k, svc[k]] for k in sorted(svc)],
        "q07": [[top_cap["Plant ID"], top_cap["Daily Capacity "], top_cost["WH"], round(top_cost["Cost/unit"], 4)]],
        "q08": [[k, vmi_n[k]] for k in sorted(vmi_n)],
        "q09": [[len(v444), round(sum(o["Weight"] for o in v444), 2)]],
        "q10": [[port04, len(orders), round(port04 / len(orders), 4)]],
        "q11": [[top_prod, qty_out[top_prod], p, cap[p]] for p in sorted(plants_of[top_prod] - {OUT})],
        "q12": [[len(out), sum(o["Unit quantity"] for o in out), len({o["Customer"] for o in out})]],
        "q13": [[p, q] for p, q in sorted(qty_out.items(), key=lambda x: -x[1])],
    }
    doc = yaml.safe_load((CASE / "questions.yaml").read_text(encoding="utf-8"))
    bad = 0
    for q in doc["questions"]:
        exp, got = q["expected"]["rows"], truth[q["id"]]
        same = len(exp) == len(got) and all(
            len(a) == len(b) and all(abs(x - y) < 1e-4 if isinstance(x, (int, float)) and isinstance(y, (int, float)) else x == y for x, y in zip(a, b))
            for a, b in zip(exp, got))
        bad += not same
        print(f"[{q['id']}] {'一致' if same else '不一致'}  原始文件重算 {got}" + ("" if same else f"  questions.yaml {exp}"))
    print(f"{len(doc['questions']) - bad}/{len(doc['questions'])} 题与原始文件重算一致")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
