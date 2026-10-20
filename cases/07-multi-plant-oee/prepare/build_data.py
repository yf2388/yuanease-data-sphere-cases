"""生成本案例（多工厂设备综合效率 OEE）的合成数据 data/*.csv。全部为自建虚构数据，随机数种子固定，重复运行逐字节相同。

口径（写进数据列，便于用指标直接表达）：
- 运行时间 = 计划时间 − 停机时间；可用率 = 运行时间 / 计划时间；
- 理论加工时间 = 理想节拍 × 实际产量；性能率 = 理论加工时间 / 运行时间；
- 质量率 = 合格品数 / 实际产量；
- 合格品理论时间 = 理想节拍 × 合格品数；OEE = 合格品理论时间 / 计划时间（= 可用率 × 性能率 × 质量率）。
设备班次运行里的停机时间，等于停机事件里同一设备、同一日期、同一班次的停机时长之和。

用法：python3 -I build_data.py <输出目录>
"""

import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path

SEED = 20261020
PLANTS = [("P01", "苏州工厂", "苏州"), ("P02", "佛山工厂", "佛山"), ("P03", "重庆工厂", "重庆")]
LINES = [  # 产线代码, 产线名称, 工厂代码, 产品类别
    ("L11", "注塑一线", "P01", "家电外壳"), ("L12", "装配一线", "P01", "空调室内机"),
    ("L21", "冲压一线", "P02", "钣金件"), ("L22", "装配二线", "P02", "洗衣机"),
    ("L31", "注塑二线", "P03", "汽车内饰件"), ("L32", "包装一线", "P03", "汽车内饰件"),
]
KINDS = {"注塑": ("注塑机", 36), "装配": ("装配机器人", 24), "冲压": ("冲压机", 12), "包装": ("包装机", 8)}
SHIFTS = [("S1", "早班", "08:00", "16:00", 480), ("S2", "中班", "16:00", "24:00", 480), ("S3", "夜班", "00:00", "08:00", 480)]
REASONS = [  # 原因代码, 原因名称, 停机类别
    ("D01", "计划保养", "计划停机"), ("D02", "模具更换", "换型调整"), ("D03", "工艺参数调整", "换型调整"),
    ("D04", "液压系统故障", "故障停机"), ("D05", "电气控制故障", "故障停机"), ("D06", "模具损坏", "故障停机"),
    ("D07", "待料", "待料"), ("D08", "质量异常停线", "故障停机"),
]
START, DAYS = date(2026, 9, 1), 30


def write(out: Path, name: str, header: list, rows: list) -> None:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv\t{len(rows)} 行")


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(SEED)
    devices = []
    for code, line_name, plant, _ in LINES:
        kind, cycle = next(v for k, v in KINDS.items() if line_name.startswith(k))
        for n in range(1, 4):
            devices.append((f"EQ-{code[1:]}{n}", f"{line_name}{n} 号{kind}", kind, code, cycle + rnd.choice([-2, 0, 0, 2])))
    runs, stops = [], []
    for d in range(DAYS):
        day = (START + timedelta(days=d)).isoformat()
        for dev, _, kind, line, cycle in devices:
            health = 0.04 if dev.endswith("2") and line in ("L21", "L31") else 0.015  # 两台设备故障偏多
            for shift, _, begin, _, planned in SHIFTS:
                stop_total = 0
                for _ in range(rnd.choice([0, 0, 1, 1, 2])):
                    reason = rnd.choice(REASONS[3:7] if rnd.random() < health * 20 else REASONS[:3] + REASONS[6:])
                    minutes = rnd.randint(8, 70 if reason[2] == "故障停机" else 40)
                    if stop_total + minutes > 200:
                        continue
                    start_min = int(begin[:2]) * 60 + rnd.randint(10, 400)
                    stops.append([f"ST{len(stops) + 1:05d}", dev, day, shift, f"{start_min // 60 % 24:02d}:{start_min % 60:02d}",
                                  minutes, reason[0]])
                    stop_total += minutes
                run_min = planned - stop_total
                speed = rnd.uniform(0.82, 0.97)
                output = int(run_min * 60 * speed / cycle)
                scrap_rate = rnd.uniform(0.005, 0.02) + (0.02 if health > 0.02 else 0)
                good = output - round(output * scrap_rate)
                runs.append([
                    f"R{len(runs) + 1:05d}", dev, day, shift, planned, stop_total, run_min, output, good,
                    round(cycle * output / 60, 2), round(cycle * good / 60, 2),
                ])
    write(out, "工厂", ["工厂代码", "工厂名称", "城市"], PLANTS)
    write(out, "产线", ["产线代码", "产线名称", "工厂代码", "产品类别"], LINES)
    write(out, "设备", ["设备编号", "设备名称", "设备类型", "产线代码", "理想节拍_秒"], devices)
    write(out, "班次", ["班次代码", "班次名称", "开始时间", "结束时间", "计划时长_分钟"], SHIFTS)
    write(out, "停机原因", ["原因代码", "原因名称", "停机类别"], REASONS)
    write(out, "设备班次运行", ["记录编号", "设备编号", "生产日期", "班次代码", "计划时间_分钟", "停机时间_分钟", "运行时间_分钟",
                            "实际产量", "合格品数", "理论加工时间_分钟", "合格品理论时间_分钟"], runs)
    write(out, "停机事件", ["停机编号", "设备编号", "生产日期", "班次代码", "开始时间", "停机时长_分钟", "原因代码"], stops)


if __name__ == "__main__":
    main(sys.argv[1])
