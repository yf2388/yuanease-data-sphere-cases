"""从 UCI「Productivity Prediction of Garment Employees」（CC BY 4.0）生成本案例的 data/*.csv。

原始文件：garments_worker_productivity.csv（1,197 行，一家服装企业 2015-01-01 至 2015-03-11 的班组日报；UCI 数据集页说明数据由人工采集、
经行业专家核验，激励金额单位为孟加拉塔卡 BDT）。
改动只有三类，原始取值一律不改：
- 班组日报：原始文件逐行逐列照搬，只把 15 个列名译成中文；行序不变。原始数据里的拼写与空格也照原样保留
  （部门写作 sweing / finishing / 「finishing 」带一个尾随空格，日期写作 月/日/年）。
- 部门：从班组日报的部门列取全部不同取值（3 个），给出中文名（sweing = 缝制，两种 finishing 写法 = 后整），是对照表，不改原表。
- 日历：从班组日报取全部不同日期（59 天），带上原始的星期与月内时段（quarter，原数据说明为「把一个月分成四段」，29 日以后记作 Quarter5），
  另给出由日期推出的标准日期（YYYY-MM-DD）与月份（YYYY-MM）。

用法：python3 -I build_data.py <garments_worker_productivity.csv> <输出目录>
"""

import csv
import sys
from pathlib import Path

COLUMNS = {
    "date": "日期", "quarter": "月内时段", "department": "部门", "day": "星期", "team": "班组",
    "targeted_productivity": "目标效率", "smv": "标准工时_分钟", "wip": "在制品数", "over_time": "加班时间_分钟",
    "incentive": "激励金额_塔卡", "idle_time": "闲置时间", "idle_men": "闲置人数", "no_of_style_change": "款式变更次数",
    "no_of_workers": "工人数", "actual_productivity": "实际效率",
}
DEPARTMENTS = {"sweing": "缝制", "finishing": "后整", "finishing ": "后整"}


def write(out: Path, name: str, header: list, rows: list) -> None:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv\t{len(rows)} 行")


def iso(mdy: str) -> str:
    m, d, y = mdy.split("/")
    return f"{y}-{int(m):02d}-{int(d):02d}"


def main(src: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(src, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header, body = rows[0], rows[1:]
    assert header == list(COLUMNS), header
    write(out, "班组日报", [COLUMNS[h] for h in header], body)

    depts = sorted({r[2] for r in body})
    assert set(depts) == set(DEPARTMENTS), depts
    write(out, "部门", ["部门", "部门名称", "说明"],
          [[d, DEPARTMENTS[d], "原始数据的拼写" + ("（带尾随空格）" if d.endswith(" ") else "")] for d in depts])

    days = {}
    for r in body:
        assert days.setdefault(r[0], (r[3], r[1])) == (r[3], r[1]), r[0]
    write(out, "日历", ["日期", "标准日期", "月份", "星期", "月内时段"],
          [[d, iso(d), iso(d)[:7], wd, q] for d, (wd, q) in sorted(days.items(), key=lambda x: iso(x[0]))])


if __name__ == "__main__":
    main(*sys.argv[1:3])
