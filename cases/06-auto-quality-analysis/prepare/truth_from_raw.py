"""直接从 Malloy 样例里的原始 auto_recalls.csv 独立重算本案例全部问答题的标准答案，并与 questions.yaml 的 expected 比对。

不经过 data/ 与 SQL：只用原始列名和 Python 标准库计算，用来证明标准答案出自原始数据。另外核对 data/召回.csv 与原始文件的对应行逐列相同。

用法：python3 -I truth_from_raw.py <auto_recalls.csv>
"""

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

CASE = Path(__file__).resolve().parent.parent


def iso(mdy: str) -> str:
    m, d, y = mdy.split("/")
    return f"{y}-{m}-{d}"


def main(src: str) -> int:
    with open(src, encoding="utf-8-sig", newline="") as fh:
        raw = list(csv.reader(fh))
    kept = [r for r in raw[1:] if iso(r[0]) >= "2021-01-01"]
    with open(CASE / "data" / "召回.csv", encoding="utf-8-sig", newline="") as fh:
        assert list(csv.reader(fh))[1:] == kept, "data/召回.csv 与原始文件不一致"
    rows = [dict(zip(raw[0], r)) for r in kept]
    for r in rows:
        r["iso"], r["n"] = iso(r["Report Received Date"]), int(r["Potentially Affected"])
    total = len(rows)
    by_mfr, aff_mfr = Counter(r["Manufacturer"] for r in rows), defaultdict(int)
    for r in rows:
        aff_mfr[r["Manufacturer"]] += r["n"]
    rank = lambda cnt: sorted(cnt.items(), key=lambda x: -x[1])
    by_type = Counter(r["Recall Type"] for r in rows)
    latest = max(r["iso"] for r in rows)
    on_latest = [r for r in rows if r["iso"] == latest]
    brake = [r for r in rows if "brake" in r["Recall Description"].lower()]
    aff_comp = defaultdict(int)
    for r in rows:
        aff_comp[r["Component"]] += r["n"]
    ford = [r for r in rows if r["Manufacturer"] == "Ford Motor Company"]
    air = [r for r in rows if r["Component"] == "AIR BAGS"]
    tire = [r for r in rows if r["Recall Type"] == "Tire"]
    truth = {
        "q01": [[m, c, aff_mfr[m], round(100 * c / total, 2)] for m, c in rank(by_mfr)[:3]],
        "q02": [[t, c, round(100 * c / total, 2)] for t, c in rank(by_type)],
        "q03": [[int(y), c] for y, c in sorted(Counter(r["iso"][:4] for r in rows).items())],
        "q04": [[latest, len(on_latest), on_latest[0]["Manufacturer"], on_latest[0]["NHTSA ID"]]],
        "q05": [[r["Manufacturer"], r["NHTSA ID"], r["n"]] for r in sorted(rows, key=lambda r: -r["n"])[:3]],
        "q06": [[len(brake), *rank(Counter(r["Manufacturer"] for r in brake))[0]]],
        "q07": [list(x) for x in rank(Counter(r["Manufacturer"] for r in rows if r["iso"][:4] == "2021"))[:5]],
        "q08": [[len(air), sum(r["n"] for r in air)]],
        "q09": [[sum("2022-01-01" <= r["iso"] <= "2022-03-31" for r in rows)]],
        "q10": [[len(ford), sum(r["n"] for r in ford), *rank(Counter(r["Component"] for r in ford))[0]]],
        "q11": [[len(tire), sum(r["n"] for r in tire)]],
        "q12": [list(rank(aff_comp)[0])],
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
