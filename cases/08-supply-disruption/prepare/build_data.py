"""生成本案例（配送中心停运后的订单影响与调拨）的合成数据 data/*.csv。全部为自建虚构数据，随机数种子固定，重复运行逐字节相同。

剧本：一家工业泵阀制造商有 4 个配送中心。2026-10-12 华东配送中心（DC-EC）因火灾停运。需要找出由它发货、尚未发出的订单，
受影响的客户与金额，以及其他配送中心的库存能否补上缺口；工厂的生产计划可以作为补充来源。

用法：python3 -I build_data.py <输出目录>
"""

import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path

SEED = 20261022
OUTAGE = date(2026, 10, 12)
DCS = [  # 配送中心代码, 名称, 城市, 区域, 状态, 停运日期, 停运原因
    ("DC-EC", "华东配送中心", "苏州", "华东", "停运", OUTAGE.isoformat(), "仓库火灾"),
    ("DC-NC", "华北配送中心", "天津", "华北", "正常", "", ""),
    ("DC-SC", "华南配送中心", "东莞", "华南", "正常", "", ""),
    ("DC-WC", "西南配送中心", "成都", "西南", "正常", "", ""),
]
PRODUCTS = [  # 成品编码, 成品名称, 产品线, 单价
    ("FG-101", "单级离心泵 IS80-65", "离心泵", 4200), ("FG-102", "多级离心泵 D46-50", "离心泵", 18600),
    ("FG-103", "管道泵 ISG100", "离心泵", 6800), ("FG-201", "电动闸阀 Z941H-DN150", "阀门", 9200),
    ("FG-202", "气动球阀 Q641F-DN80", "阀门", 3600), ("FG-203", "蝶阀 D341X-DN300", "阀门", 7400),
    ("FG-204", "截止阀 J41H-DN50", "阀门", 1800), ("FG-301", "隔膜计量泵 JMZ-500", "计量泵", 12500),
    ("FG-302", "柱塞计量泵 J-ZM", "计量泵", 15800), ("FG-401", "泵阀控制柜 PLC-A", "控制系统", 26800),
]
PLANTS = [("PL-WX", "无锡工厂", "无锡"), ("PL-CQ", "重庆工厂", "重庆")]
INDUSTRIES = ["化工", "水务", "电力", "冶金", "制药", "石化"]
PROVINCES = {"华东": ["江苏", "浙江", "上海", "安徽"], "华北": ["北京", "天津", "河北", "山东"], "华南": ["广东", "广西", "福建"],
             "西南": ["四川", "重庆", "云南"]}
NAMES = ["恒远", "华泰", "新源", "宏达", "永昌", "中科", "瑞丰", "蓝海", "鼎盛", "国泰", "金石", "天成", "盛世", "泰和", "安澜"]


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
    customers = []
    for n in range(1, 61):
        region = rnd.choices(list(PROVINCES), weights=[40, 20, 25, 15])[0]
        customers.append([f"CU{n:03d}", f"{rnd.choice(NAMES)}{rnd.choice(INDUSTRIES)}{rnd.choice(['有限公司', '股份有限公司', '集团'])}",
                          rnd.choice(INDUSTRIES), rnd.choice(PROVINCES[region]), rnd.choices("ABC", weights=[2, 3, 5])[0], region])
    dc_of_region = {"华东": "DC-EC", "华北": "DC-NC", "华南": "DC-SC", "西南": "DC-WC"}
    inventory = []
    for dc in DCS:
        for p in PRODUCTS:
            safety = rnd.choice([10, 20, 30])
            inventory.append([dc[0], p[0], rnd.randint(0, 120) if dc[0] != "DC-EC" else 0, safety])
    orders, lines = [], []
    for n in range(1, 241):
        cu = rnd.choice(customers)
        placed = OUTAGE - timedelta(days=rnd.randint(0, 40))
        due = placed + timedelta(days=rnd.randint(10, 30))
        shipped = placed + timedelta(days=rnd.randint(3, 12))
        status = "已签收" if shipped + timedelta(days=4) < OUTAGE else "已发货" if shipped < OUTAGE else "待发货"
        no = f"SO{n:05d}"
        total = 0
        for k in range(1, rnd.choice([1, 1, 2, 3]) + 1):
            p = rnd.choice(PRODUCTS)
            qty = rnd.choice([1, 2, 3, 4, 5, 8, 10])
            lines.append([no, k, p[0], qty, p[3], p[3] * qty])
            total += p[3] * qty
        orders.append([no, cu[0], placed.isoformat(), due.isoformat(), dc_of_region[cu[5]], status, total])
    plans = []
    for n in range(1, 31):
        p = rnd.choice(PRODUCTS)
        plans.append([f"MP{n:04d}", rnd.choice(PLANTS)[0], p[0], (OUTAGE + timedelta(days=rnd.randint(1, 25))).isoformat(),
                      rnd.choice([20, 30, 40, 50])])
    write(out, "配送中心", ["配送中心代码", "配送中心名称", "城市", "区域", "状态", "停运日期", "停运原因"], DCS)
    write(out, "成品", ["成品编码", "成品名称", "产品线", "单价"], PRODUCTS)
    write(out, "工厂", ["工厂代码", "工厂名称", "城市"], PLANTS)
    write(out, "客户", ["客户编码", "客户名称", "行业", "省份", "客户等级"], [c[:5] for c in customers])
    write(out, "配送中心库存", ["配送中心代码", "成品编码", "在库数量", "安全库存"], inventory)
    write(out, "销售订单", ["订单号", "客户编码", "下单日期", "承诺交期", "发货配送中心代码", "订单状态", "订单金额"], orders)
    write(out, "订单明细", ["订单号", "行号", "成品编码", "数量", "单价", "金额"], lines)
    write(out, "生产计划", ["计划号", "工厂代码", "成品编码", "计划完工日期", "计划数量"], plans)


if __name__ == "__main__":
    main(sys.argv[1])
