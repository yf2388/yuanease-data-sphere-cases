"""从 Google Malloy 官方样例仓库 malloydata/malloy-samples 的 auto_recalls/auto_recalls.csv 生成本案例的 data/*.csv。

原始文件：美国国家公路交通安全管理局（NHTSA）的全量召回数据（1966–2022 年 26,020 条），Malloy 样例 README 注明取自
https://catalog.data.gov/dataset/recalls-data ；样例仓库 MIT 许可，底层是美国联邦政府作品（公有领域）。
Malloy 用它演示语义模型：auto_recalls.malloy 定义了召回数、占比、潜在受影响合计三个度量和按厂商、类型、年份等视图。
改动只有三类，原始取值一律不改：
- 裁剪行：只取报告接收日期在 2021 年及以后的召回（2021-01-01 至数据截止的 2022-06，共 1,574 条）；列名译成中文，行序不变。
- 日历：从召回表取全部不同的接收日期（原始写法 MM/DD/YYYY），给出由它推出的标准日期、年份、月份、季度。
- 部件、召回类型：取召回表里出现的全部原始取值，另给出本仓库的中文译名，是对照表，召回表里仍是英文原文。

用法：python3 -I build_data.py <auto_recalls.csv> <输出目录>
"""

import csv
import sys
from pathlib import Path

COLUMNS = {
    "Report Received Date": "报告接收日期", "NHTSA ID": "NHTSA编号", "Recall Link": "召回链接", "Manufacturer": "厂商",
    "Subject": "主题", "Component": "部件", "Mfr Campaign Number": "厂商召回编号", "Recall Type": "召回类型",
    "Potentially Affected": "潜在受影响数量", "Recall Description": "召回描述", "Consequence Summary": "后果摘要",
    "Corrective Action": "纠正措施",
}
COMPONENTS = {  # 原始取值 → 本仓库译名
    "AIR BAGS": "安全气囊", "BACK OVER PREVENTION": "倒车防撞", "CHILD SEAT": "儿童座椅", "COMMUNICATION": "通信",
    "ELECTRICAL SYSTEM": "电气系统", "ELECTRONIC STABILITY CONTROL": "电子稳定控制", "ENGINE": "发动机",
    "ENGINE AND ENGINE COOLING": "发动机及冷却", "EQUIPMENT": "设备", "EQUIPMENT ADAPTIVE/MOBILITY": "无障碍改装设备",
    "EXTERIOR LIGHTING": "外部照明", "FORWARD COLLISION AVOIDANCE": "前向防撞", "FUEL SYSTEM, DIESEL": "燃油系统（柴油）",
    "FUEL SYSTEM, GASOLINE": "燃油系统（汽油）", "FUEL SYSTEM, OTHER": "燃油系统（其他）", "HYBRID PROPULSION SYSTEM": "混合动力系统",
    "LANE DEPARTURE": "车道偏离", "LATCHES/LOCKS/LINKAGES": "门锁与连杆", "OTHER": "其他", "PARKING BRAKE": "驻车制动",
    "POWER TRAIN": "动力总成", "SEAT BELTS": "安全带", "SEATS": "座椅", "SERVICE BRAKES": "行车制动",
    "SERVICE BRAKES, AIR": "行车制动（气压）", "SERVICE BRAKES, HYDRAULIC": "行车制动（液压）", "STEERING": "转向",
    "STRUCTURE": "车身结构", "SUSPENSION": "悬架", "TIRES": "轮胎", "TRAILER HITCHES": "挂车连接装置",
    "UNKNOWN OR OTHER": "未知或其他", "VEHICLE SPEED CONTROL": "车速控制", "VISIBILITY": "视野", "WHEELS": "车轮",
}
TYPES = {"Vehicle": "整车", "Equipment": "设备", "Tire": "轮胎", "Child Seat": "儿童座椅"}


def write(out: Path, name: str, header: list, rows: list) -> None:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv\t{len(rows)} 行")


def iso(mdy: str) -> str:
    m, d, y = mdy.split("/")
    return f"{y}-{m}-{d}"


def main(src: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(src, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header = rows[0]
    assert header == list(COLUMNS), header
    body = [r for r in rows[1:] if iso(r[0]) >= "2021-01-01"]
    write(out, "召回", [COLUMNS[h] for h in header], body)
    days = sorted({r[0] for r in body}, key=iso)
    write(out, "日历", ["日期", "标准日期", "年份", "月份", "季度"],
          [[d, iso(d), iso(d)[:4], iso(d)[:7], f"{iso(d)[:4]}-Q{(int(iso(d)[5:7]) - 1) // 3 + 1}"] for d in days])
    comps = sorted({r[5] for r in body})
    write(out, "部件", ["部件", "部件中文名"], [[c, COMPONENTS[c]] for c in comps])
    types = sorted({r[7] for r in body})
    write(out, "召回类型", ["召回类型", "召回类型中文名"], [[t, TYPES[t]] for t in types])


if __name__ == "__main__":
    main(*sys.argv[1:3])
