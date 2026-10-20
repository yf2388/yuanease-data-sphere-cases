"""用 UCI「Steel Industry Energy Consumption」数据（CC BY 4.0）生成本案例的 data/*.csv。

规则（确定性）：
- 抽样：只取 2018 年 1–3 月（原始日期为 dd/mm/yyyy，按月份 01–03 筛选），共 8,640 条 15 分钟用电记录。
- 用电记录：列名汉化；记录时间改写为「YYYY-MM-DD HH:MM」；原数据把每天最后一个 15 分钟区间（23:45–24:00）记成当天的 00:00、
  当日秒数为 0，本案例照原样保留，并把它归入当天；记录编号按原始行序编为 E000001 起。
- 班次：按 15 分钟区间的起点（当日秒数 − 900，取模一天）分配：00:00–08:00 夜班 S3、08:00–16:00 早班 S1、16:00–24:00 中班 S2。
- 日历：原数据每行的 WeekStatus、Day_of_week 拆成一张日历表（日期、星期、是否周末、月份）。
- 负荷类型：原始取值 Light_Load / Medium_Load / Maximum_Load 保留为代码，另建一张代码表给出中文名。

用法：python3 -I build_data.py <Steel_industry_data.csv> <输出目录>
"""

import csv
import sys
from pathlib import Path

WEEKDAYS = {"Monday": "周一", "Tuesday": "周二", "Wednesday": "周三", "Thursday": "周四", "Friday": "周五",
            "Saturday": "周六", "Sunday": "周日"}
LOADS = [("Light_Load", "轻载", "用电负荷较低的时段"), ("Medium_Load", "中载", "用电负荷中等的时段"),
         ("Maximum_Load", "重载", "用电负荷最高的时段")]
SHIFTS = [("S1", "早班", "08:00", "16:00"), ("S2", "中班", "16:00", "24:00"), ("S3", "夜班", "00:00", "08:00")]


def shift_of(nsm: int) -> str:
    start = (nsm - 900) % 86400
    return "S3" if start < 28800 else "S1" if start < 57600 else "S2"


def write(out: Path, name: str, header: list, rows: list) -> None:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv\t{len(rows)} 行")


def main(src: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(src, encoding="utf-8-sig", newline="") as fh:
        raw = list(csv.DictReader(fh))
    records, calendar = [], {}
    for n, r in enumerate(raw, start=1):
        dd, mm, rest = r["date"].split("/", 2)
        yyyy, hhmm = rest.split(" ")
        if mm not in ("01", "02", "03"):
            continue
        day = f"{yyyy}-{mm}-{dd}"
        calendar.setdefault(day, [day, WEEKDAYS[r["Day_of_week"]], "是" if r["WeekStatus"] == "Weekend" else "否", f"{yyyy}-{mm}"])
        records.append([
            f"E{n:06d}", f"{day} {hhmm}", day, r["Usage_kWh"], r["Lagging_Current_Reactive.Power_kVarh"],
            r["Leading_Current_Reactive_Power_kVarh"], r["CO2(tCO2)"], r["Lagging_Current_Power_Factor"],
            r["Leading_Current_Power_Factor"], r["NSM"], r["Load_Type"], shift_of(int(r["NSM"])),
        ])
    write(out, "日历", ["日期", "星期", "是否周末", "月份"], sorted(calendar.values()))
    write(out, "负荷类型", ["负荷类型代码", "负荷类型名称", "说明"], LOADS)
    write(out, "班次", ["班次代码", "班次名称", "开始时间", "结束时间"], SHIFTS)
    write(out, "用电记录", ["记录编号", "记录时间", "日期", "用电量_kWh", "滞后无功_kVarh", "超前无功_kVarh", "二氧化碳_tCO2",
                          "滞后功率因数", "超前功率因数", "当日秒数", "负荷类型代码", "班次代码"], records)


if __name__ == "__main__":
    main(*sys.argv[1:3])
