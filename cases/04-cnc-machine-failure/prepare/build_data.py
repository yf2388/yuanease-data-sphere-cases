"""用 UCI AI4I 2020 预测性维护数据（CC BY 4.0）做信号层，叠加自建的中文主数据，生成本案例的 data/*.csv。

规则（确定性，无随机数）：
- 加工记录：原始 10,000 行一行一条，记录编号 = 原 UDI；按 UDI 顺序每 1,000 行分给一台设备（CNC-01 … CNC-10），
  保留原数据里刀具磨损随加工次数累积的顺序；每台设备的第 k 条记录（k 从 0 起）的加工时间 = 2026-09-01 00:00 + 40 分钟 × k。
- 班组：按加工时间所在班次分配，08:00–16:00 甲组（早班）、16:00–24:00 乙组（中班）、00:00–08:00 丙组（夜班）。
- 故障事件：原数据五个失效模式标志（TWF/HDF/PWF/OSF/RNF）每有一个为 1，就生成一条故障事件；原数据里有 9 条记录
  「设备故障 = 1」但五个标志都为 0、18 条反之，照原样保留。
- 设备台账、产线、班组、失效模式四张主数据表为自建内容（失效模式的判定说明转述自数据集文档）。

用法：python3 -I build_data.py <ai4i2020.csv> <输出目录>
"""

import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

LINES = [("L1", "轴类加工线", "机加一车间"), ("L2", "法兰加工线", "机加一车间"), ("L3", "壳体加工线", "机加二车间")]
MACHINES = [  # 设备编号, 设备名称, 型号, 产线, 投用日期, 额定功率_kW
    (f"CNC-{i:02d}", f"数控铣床 {i} 号", "XK7140" if i <= 4 else "XK7150" if i <= 7 else "VMC850",
     "L1" if i <= 4 else "L2" if i <= 7 else "L3", f"20{19 + (i % 5)}-0{1 + i % 9}-15", 11.0 if i <= 4 else 15.0 if i <= 7 else 18.5)
    for i in range(1, 11)
]
TEAMS = [("T1", "甲组", "早班", "08:00", "16:00"), ("T2", "乙组", "中班", "16:00", "24:00"), ("T3", "丙组", "夜班", "00:00", "08:00")]
MODES = [
    ("TWF", "刀具磨损失效", "刀具累计磨损到 200–240 分钟之间的某个时刻时被更换或失效"),
    ("HDF", "散热失效", "加工温度与环境温度之差低于 8.6 K，且主轴转速低于 1380 rpm"),
    ("PWF", "功率失效", "扭矩与转速（rad/s）之积得到的功率低于 3500 W 或高于 9000 W"),
    ("OSF", "过应变失效", "刀具磨损（分钟）与扭矩（Nm）之积超过阈值：低等级 11,000、中等级 12,000、高等级 13,000"),
    ("RNF", "随机失效", "与工艺参数无关的随机失效，每次加工约 0.1% 的概率"),
]
GRADE = {"L": "低", "M": "中", "H": "高"}
START = datetime(2026, 9, 1)


def team_of(t: datetime) -> str:
    return "T1" if 8 <= t.hour < 16 else "T2" if t.hour >= 16 else "T3"


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
    records, events = [], []
    for r in raw:
        udi = int(r["UDI"])
        machine, k = (udi - 1) // 1000 + 1, (udi - 1) % 1000
        t = START + timedelta(minutes=40 * k)
        records.append([
            udi, f"CNC-{machine:02d}", team_of(t), t.strftime("%Y-%m-%d %H:%M"), r["Product ID"], GRADE[r["Type"]],
            r["Air temperature [K]"], r["Process temperature [K]"], r["Rotational speed [rpm]"], r["Torque [Nm]"],
            r["Tool wear [min]"], "是" if r["Machine failure"] == "1" else "否",
        ])
        for code, _, _ in MODES:
            if r[code] == "1":
                events.append([f"F{len(events) + 1:05d}", udi, f"CNC-{machine:02d}", t.strftime("%Y-%m-%d %H:%M"), code])
    write(out, "产线", ["产线编号", "产线名称", "车间"], LINES)
    write(out, "设备台账", ["设备编号", "设备名称", "设备型号", "产线编号", "投用日期", "额定功率_kW"], MACHINES)
    write(out, "班组", ["班组编号", "班组名称", "班次", "开始时间", "结束时间"], TEAMS)
    write(out, "失效模式", ["失效模式代码", "失效模式名称", "判定说明"], MODES)
    write(out, "加工记录", ["记录编号", "设备编号", "班组编号", "加工时间", "产品序列号", "质量等级", "环境温度_K",
                          "加工温度_K", "主轴转速_rpm", "扭矩_Nm", "刀具磨损_分钟", "是否故障"], records)
    write(out, "故障事件", ["故障编号", "记录编号", "设备编号", "发生时间", "失效模式代码"], events)


if __name__ == "__main__":
    main(*sys.argv[1:3])
