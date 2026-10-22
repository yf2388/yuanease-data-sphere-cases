"""直接从 UCI 原始文件 garments_worker_productivity.csv 独立重算本案例全部问答题的标准答案，并与 questions.yaml 的 expected 比对。

不经过 data/ 与 SQL：只用原始列名和 Python 标准库计算，用来证明标准答案出自原始数据。后整部门把 finishing 与「finishing 」两种写法合并。
另外核对 data/班组日报.csv 与原始文件逐行逐列相同（只换了列名）。

用法：python3 -I truth_from_raw.py <garments_worker_productivity.csv>（在案例目录或任意目录运行均可）
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import yaml

CASE = Path(__file__).resolve().parent.parent
DEPT = {"sweing": "缝制", "finishing": "后整", "finishing ": "后整"}


def iso(mdy: str) -> str:
    m, d, y = mdy.split("/")
    return f"{y}-{int(m):02d}-{int(d):02d}"


def avg(xs):
    return round(sum(xs) / len(xs), 4)


def main(src: str) -> int:
    with open(src, encoding="utf-8-sig", newline="") as fh:
        raw = list(csv.reader(fh))
    with open(CASE / "data" / "班组日报.csv", encoding="utf-8-sig", newline="") as fh:
        ours = list(csv.reader(fh))
    assert raw[1:] == ours[1:], "data/班组日报.csv 与原始文件的取值不一致"
    rows = [dict(zip(raw[0], r)) for r in raw[1:]]
    for r in rows:
        r["dept"], r["iso"], r["ap"], r["tp"] = DEPT[r["department"]], iso(r["date"]), float(r["actual_productivity"]), float(r["targeted_productivity"])

    by_dept, by_team, by_day, inc_team = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(int)
    for r in rows:
        by_dept[r["dept"]].append(r["ap"])
        by_team[(r["dept"], int(r["team"]))].append(r["ap"])
        by_day[r["iso"]].append(r["ap"])
        inc_team[(r["dept"], int(r["team"]))] += int(r["incentive"])
    low_team = min(by_team, key=lambda k: avg(by_team[k]))
    idle_top = max(rows, key=lambda r: float(r["idle_time"]))
    low_day = min(by_day, key=lambda k: avg(by_day[k]))
    top_inc = max(inc_team, key=inc_team.get)
    hit = sum(r["ap"] >= r["tp"] for r in rows)
    styled = [r["ap"] for r in rows if int(r["no_of_style_change"]) > 0]
    q09 = [r for r in rows if r["iso"] == "2015-01-15" and r["dept"] == "缝制" and r["team"] == "8"][0]
    truth = {
        "q01": [[len(rows), len(by_day), min(by_day), max(by_day)]],
        "q02": [[d, len(by_dept[d]), avg(by_dept[d])] for d in sorted(by_dept)],
        "q03": [[hit, len(rows), round(hit / len(rows), 4)]],
        "q04": [[low_team[0], f"第{low_team[1]}组", avg(by_team[low_team])]],
        "q05": [[sum(float(r["idle_time"]) for r in rows), idle_top["iso"], idle_top["dept"], f"第{idle_top['team']}组", float(idle_top["idle_time"])]],
        "q06": [[len(styled), avg(styled)]],
        "q07": [[sum(int(r["over_time"]) for r in rows if r["iso"][:7] == "2015-02" and r["dept"] == "缝制")]],
        "q08": [[low_day, avg(by_day[low_day])]],
        "q09": [[round(q09["ap"], 4), q09["tp"]]],
        "q10": [[sum(int(r["incentive"]) for r in rows), top_inc[0], f"第{top_inc[1]}组", inc_team[top_inc]]],
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
