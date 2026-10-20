"""生成本案例（定制加工订单的五类指标）的合成数据 data/*.csv。全部为自建虚构数据，随机数种子固定，重复运行逐字节相同。

一家机加工厂按客户图纸接单：先报价，成交后生成订单，生产后交付。五类指标：
- 简单指标：订单金额、订单数；比率指标：按期交付率 = 按期交付订单数 / 已交付订单数；
- 转化指标：报价成交率 = 成交报价数 / 报价数；
- 累计指标（按月累计订单金额）与派生指标（毛利 = 订单金额 − 订单成本）在数据里给出原始列，留给问数计算。
是否按期 = 实际交付日期不晚于承诺交期（生成时写成「是/否」列；未交付的订单为空）。

用法：python3 -I build_data.py <输出目录>
"""

import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path

SEED = 20261023
CUSTOMERS = [("C01", "江南精密机械", "装备制造"), ("C02", "北辰液压", "液压件"), ("C03", "东海船舶配套", "船舶"),
             ("C04", "华中汽配", "汽车零部件"), ("C05", "西部能源装备", "能源装备"), ("C06", "岭南电机", "电机"),
             ("C07", "齐鲁重工", "工程机械"), ("C08", "天府航空部件", "航空"), ("C09", "滨海泵业", "泵阀"), ("C10", "燕山轴承", "轴承")]
PRODUCTS = [  # 产品编码, 产品名称, 品类, 标准单价, 标准成本
    ("P01", "法兰盘", "盘类件", 180, 118), ("P02", "传动轴", "轴类件", 420, 290), ("P03", "齿轮箱壳体", "箱体件", 1650, 1180),
    ("P04", "液压阀块", "阀体件", 980, 640), ("P05", "轴承座", "支座件", 260, 170), ("P06", "联轴器", "传动件", 340, 225),
    ("P07", "精密丝杠", "轴类件", 1280, 860), ("P08", "端盖", "盘类件", 95, 62),
]
START, END = date(2026, 1, 1), date(2026, 9, 30)


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
    quotes, orders, lines = [], [], []
    span = (END - START).days
    for n in range(1, 401):
        cu = rnd.choice(CUSTOMERS)
        qday = START + timedelta(days=rnd.randint(0, span - 10))
        picks = [(rnd.choice(PRODUCTS), rnd.choice([20, 50, 100, 200, 500])) for _ in range(rnd.choice([1, 1, 2, 3]))]
        discount = rnd.choice([1.0, 0.97, 0.95, 0.92])
        amount = round(sum(p[3] * q for p, q in picks) * discount, 2)
        won = rnd.random() < (0.62 if discount < 0.96 else 0.45)
        order_no = ""
        if won:
            order_no = f"SO{len(orders) + 1:04d}"
            oday = qday + timedelta(days=rnd.randint(1, 7))
            due = oday + timedelta(days=rnd.randint(15, 40))
            cost = round(sum(p[4] * q for p, q in picks) * rnd.uniform(0.97, 1.08), 2)
            if rnd.random() < 0.04:
                status, delivered, ontime = "已取消", "", ""
            else:
                done = due + timedelta(days=rnd.choice([-6, -3, -1, 0, 0, 2, 5, 9]))
                if done > END:
                    status, delivered, ontime = "生产中", "", ""
                else:
                    status, delivered, ontime = "已交付", done.isoformat(), "是" if done <= due else "否"
            orders.append([order_no, cu[0], oday.isoformat(), due.isoformat(), delivered, status, ontime, amount, cost])
            for k, (p, q) in enumerate(picks, start=1):
                lines.append([order_no, k, p[0], q, round(p[3] * discount, 2), round(p[3] * discount * q, 2)])
        quotes.append([f"QT{n:04d}", cu[0], qday.isoformat(), amount, "是" if won else "否", order_no])
    write(out, "客户", ["客户编码", "客户名称", "行业"], CUSTOMERS)
    write(out, "产品", ["产品编码", "产品名称", "品类", "标准单价", "标准成本"], PRODUCTS)
    write(out, "报价单", ["报价单号", "客户编码", "报价日期", "报价金额", "是否成交", "成交订单号"], quotes)
    write(out, "订单", ["订单号", "客户编码", "下单日期", "承诺交期", "实际交付日期", "订单状态", "是否按期", "订单金额", "订单成本"], orders)
    write(out, "订单明细", ["订单号", "行号", "产品编码", "数量", "成交单价", "金额"], lines)


if __name__ == "__main__":
    main(sys.argv[1])
