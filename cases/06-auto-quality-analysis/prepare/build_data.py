"""生成本案例（整车质量分析）的合成数据 data/*.csv。全部为自建虚构数据，随机数种子固定，重复运行逐字节相同。

业务口径（与公开的汽车行业质量评价体系一致）：
- 每千辆维修频次 = 维修次数 / 在保车辆数 × 1000；单车维修成本 = 维修费用合计 / 维修过的车辆数；
- 每百辆问题数（PP100）= 市场调查报告问题数合计 / 调查样本车辆数合计 × 100；
- 客户满意度 = 回访满意度评分（1–5 分）的平均值；投诉率 = 投诉回访数 / 回访数。
维修费用合计 = 工时费 + 配件费。

用法：python3 -I build_data.py <输出目录>
"""

import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path

SEED = 20261021
MODELS = [  # 车型代码, 车型名称, 级别, 动力类型, 上市日期, 质量系数（越大问题越多，不写进数据）
    ("M01", "远航 S5", "紧凑型 SUV", "燃油", "2023-03-18", 1.0), ("M02", "远航 S7", "中型 SUV", "混动", "2024-04-26", 1.3),
    ("M03", "启明 E3", "紧凑型轿车", "纯电", "2024-09-10", 1.6), ("M04", "启明 E5", "中型轿车", "纯电", "2025-05-20", 1.1),
    ("M05", "锐途 X1", "小型 SUV", "燃油", "2022-08-08", 0.8), ("M06", "家悦 M8", "MPV", "混动", "2025-01-15", 1.2),
]
BASES = [("B1", "华东基地", "浙江"), ("B2", "西南基地", "重庆"), ("B3", "华南基地", "广东")]
REGIONS = ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
STATIONS = [(f"SS{i:02d}", f"{REGIONS[(i - 1) % 7]}{'一二'[(i - 1) // 7]}号服务站", REGIONS[(i - 1) % 7]) for i in range(1, 15)]
FAULTS = [  # 故障代码, 故障部位, 所属系统, 故障描述, 工时费区间, 配件费区间
    ("P101", "发动机", "动力系统", "怠速抖动", (200, 600), (0, 1500)), ("P102", "变速箱", "动力系统", "换挡顿挫", (300, 900), (0, 4000)),
    ("P103", "动力电池", "动力系统", "续航衰减异常", (300, 800), (0, 9000)), ("P104", "电驱总成", "动力系统", "异响", (400, 900), (0, 6000)),
    ("C201", "悬架", "底盘系统", "过坎异响", (150, 500), (100, 1800)), ("C202", "制动系统", "底盘系统", "制动尖叫", (100, 400), (100, 1200)),
    ("C203", "转向系统", "底盘系统", "方向盘跑偏", (150, 450), (0, 1500)), ("B301", "车门", "车身系统", "关门异响", (100, 300), (0, 800)),
    ("B302", "天窗", "车身系统", "漏水", (200, 600), (0, 2500)), ("B303", "车漆", "车身系统", "漆面起泡", (300, 900), (0, 600)),
    ("E401", "中控屏", "电气系统", "黑屏死机", (100, 300), (0, 3500)), ("E402", "车机系统", "电气系统", "蓝牙连接失败", (80, 200), (0, 0)),
    ("E403", "倒车影像", "电气系统", "画面延迟", (80, 250), (0, 1200)), ("E404", "车灯", "电气系统", "灯罩起雾", (100, 300), (100, 900)),
    ("I501", "座椅", "内饰系统", "加热失效", (100, 300), (0, 1500)), ("I502", "空调", "内饰系统", "制冷不足", (200, 500), (0, 2200)),
]
COMPLAINTS = ["维修等待时间长", "同一问题重复维修", "服务态度", "费用争议", "配件缺货"]


def write(out: Path, name: str, header: list, rows: list) -> None:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv\t{len(rows)} 行")


def vin(rnd: random.Random, n: int) -> str:
    return "LYE" + "".join(rnd.choice("ABCDEFGHJKLMNPRSTUVWXYZ0123456789") for _ in range(8)) + f"{n:06d}"


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(SEED)
    vehicles, repairs, visits = [], [], []
    quality = {m[0]: m[5] for m in MODELS}
    for n in range(1, 3001):
        model = rnd.choices(MODELS, weights=[25, 18, 15, 12, 20, 10])[0]
        built = max(date.fromisoformat(model[4]), date(2025, 1, 1)) + timedelta(days=rnd.randint(0, 420))
        built = min(built, date(2026, 3, 31))
        sold = built + timedelta(days=rnd.randint(7, 60))
        vehicles.append([vin(rnd, n), model[0], rnd.choice(BASES)[0], built.isoformat(), sold.isoformat(), rnd.choice(REGIONS)])
    for v in vehicles:
        q = quality[v[1]]
        sold = date.fromisoformat(v[4])
        for _ in range(rnd.choices([0, 1, 2, 3], weights=[100, 30 * q, 8 * q, 2 * q])[0]):
            day = sold + timedelta(days=rnd.randint(10, 300))
            if day > date(2026, 9, 30):
                continue
            fault = rnd.choice(FAULTS[2:4] if v[1] in ("M03", "M04") and rnd.random() < 0.4 else FAULTS)
            labor, parts = rnd.randint(*fault[4]) // 10 * 10, rnd.randint(*fault[5]) // 10 * 10
            warranty = "保修" if rnd.random() < 0.85 else "自费"
            station = rnd.choice([s for s in STATIONS if s[2] == v[5]])
            repairs.append([f"WX{len(repairs) + 1:06d}", v[0], day.isoformat(), (day - sold).days * rnd.randint(30, 80), fault[0],
                            warranty, labor, parts, labor + parts, station[0]])
        if rnd.random() < 0.7:
            day = sold + timedelta(days=rnd.randint(30, 200))
            if day <= date(2026, 9, 30):
                score = max(1, min(5, round(rnd.gauss(4.4 - 0.4 * (q - 1), 0.7))))
                complaint = score <= 2 and rnd.random() < 0.7
                visits.append([f"HF{len(visits) + 1:06d}", v[0], day.isoformat(), score, "是" if complaint else "否",
                               rnd.choice(COMPLAINTS) if complaint else ""])
    surveys = []
    for batch, period in (("2026Q1", "2026-03-31"), ("2026Q2", "2026-06-30"), ("2026Q3", "2026-09-30")):
        for m in MODELS:
            sample = rnd.randint(180, 320)
            problems = round(sample * rnd.uniform(0.9, 1.2) * m[5] * 1.1)
            surveys.append([f"DC-{batch}-{m[0]}", batch, period, m[0], sample, problems])
    write(out, "车型", ["车型代码", "车型名称", "级别", "动力类型", "上市日期"], [m[:5] for m in MODELS])
    write(out, "生产基地", ["基地代码", "基地名称", "省份"], BASES)
    write(out, "服务站", ["服务站代码", "服务站名称", "区域"], STATIONS)
    write(out, "故障代码", ["故障代码", "故障部位", "所属系统", "故障描述"], [f[:4] for f in FAULTS])
    write(out, "车辆", ["VIN码", "车型代码", "基地代码", "生产日期", "销售日期", "销售区域"], vehicles)
    write(out, "维修记录", ["维修单号", "VIN码", "维修日期", "行驶里程_km", "故障代码", "维修类型", "工时费", "配件费",
                          "维修费用合计", "服务站代码"], repairs)
    write(out, "客户回访", ["回访编号", "VIN码", "回访日期", "满意度评分", "是否投诉", "投诉类别"], visits)
    write(out, "市场调查", ["调查编号", "调查批次", "截止日期", "车型代码", "样本车辆数", "报告问题数"], surveys)


if __name__ == "__main__":
    main(sys.argv[1])
