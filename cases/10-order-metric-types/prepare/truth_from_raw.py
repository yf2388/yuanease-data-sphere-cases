"""直接从 Malloy 样例的原始 parquet（data/users、order_items、inventory_items、products）独立重算本案例全部问答题的标准答案，
并与 questions.yaml 的 expected 比对。不经过本案例的 data/ 与 SQL，用 pyarrow 读原始文件、Python 计算。

用法：python3 -I truth_from_raw.py <malloy-samples 的 data 目录>（需要 pyarrow 与 PyYAML）
"""

import sys
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path

import pyarrow.parquet as pq
import yaml

CASE = Path(__file__).resolve().parent.parent


def main(src: str) -> int:
    src = Path(src)
    users = {u["id"] for u in pq.read_table(src / "users.parquet").to_pylist() if u["state"] == "Florida"}
    items = [r for r in pq.read_table(src / "order_items.parquet").to_pylist() if r["user_id"] in users]
    inv = {r["id"]: r for r in pq.read_table(src / "inventory_items.parquet").to_pylist()}
    for r in items:
        r["inv"] = inv[r["inventory_item_id"]]
    sales = lambda rs: sum(r["sale_price"] for r in rs)
    cost = lambda rs: sum(r["inv"]["cost"] for r in rs)
    rank = lambda d: sorted(d.items(), key=lambda x: -x[1])
    total = sales(items)
    by = lambda key: (lambda d: [d.__setitem__(key(r), d[key(r)] + r["sale_price"]) for r in items] and d)(defaultdict(float))
    cat, brand, prod = by(lambda r: r["inv"]["product_category"]), by(lambda r: r["inv"]["product_brand"]), by(lambda r: r["inv"]["product_name"])
    month22 = defaultdict(float)
    for r in items:
        if r["created_at"].year == 2022:
            month22[r["created_at"].strftime("%Y-%m")] += r["sale_price"]
    status_orders = defaultdict(set)
    for r in items:
        status_orders[r["status"]].add(r["order_id"])
    returned = [r for r in items if r["status"] == "Returned"]
    ret_by_user = defaultdict(list)
    for r in returned:
        ret_by_user[r["user_id"]].append(r["sale_price"])
    y = lambda yr: [r for r in items if r["created_at"].year == yr]
    s22, s21 = sales(y(2022)), sales(y(2021))
    first = {}
    for r in sorted(items, key=lambda r: r["created_at"]):
        first.setdefault(r["user_id"], r)
    cohort = [u for u, r in first.items() if r["created_at"].year == 2021]
    by_user = defaultdict(list)
    for r in items:
        by_user[r["user_id"]].append(r)
    rep = sum(any(f["created_at"] < r["created_at"] <= f["created_at"] + timedelta(days=90) and r["order_id"] != f["order_id"]
                  for r in by_user[u]) for u in cohort for f in [first[u]])
    h1 = [r for r in items if r["created_at"].year == 2022 and r["created_at"].month <= 6]
    r2 = lambda v: round(v, 2)
    truth = {
        "q01": [[r2(total), len({r["order_id"] for r in items}), r2(total - cost(items))]],
        "q02": [[k, r2(v)] for k, v in rank(cat)[:5]],
        "q03": [[k, r2(v), round(v / total, 4)] for k, v in rank(brand)[:3]],
        "q04": [[k, r2(v)] for k, v in rank(month22)[:1]],
        "q05": [[k, len(v)] for k, v in sorted(status_orders.items())],
        "q06": [[u, len(v), r2(sum(v))] for u, v in sorted(ret_by_user.items()) if len(v) > 1],
        "q07": [[r2(s22), r2(s22 - s21), round(s22 / s21 - 1, 4)]],
        "q08": [[k, r2(v)] for k, v in rank(prod)[:1]],
        "q09": [[len(returned), len(items), round(len(returned) / len(items), 4)]],
        "q10": [[r2(sales(h1))]],
        "q11": [[len(cohort), rep, round(rep / len(cohort), 4)]],
        "q12": [[r2(sales(y(2022)) - cost(y(2022)))]],
    }
    doc = yaml.safe_load((CASE / "questions.yaml").read_text(encoding="utf-8"))
    bad = 0
    for q in doc["questions"]:
        exp, got = q["expected"]["rows"], truth[q["id"]]
        same = len(exp) == len(got) and all(
            len(a) == len(b) and all(abs(x - y) < 0.011 if isinstance(x, (int, float)) and isinstance(y, (int, float)) else x == y for x, y in zip(a, b))
            for a, b in zip(exp, got))
        bad += not same
        print(f"[{q['id']}] {'一致' if same else '不一致'}  原始文件重算 {got}" + ("" if same else f"  questions.yaml {exp}"))
    print(f"{len(doc['questions']) - bad}/{len(doc['questions'])} 题与原始文件重算一致")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
