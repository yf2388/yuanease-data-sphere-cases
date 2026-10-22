"""从 Brunel University London 的「Supply Chain Logistics Problem Dataset」（CC BY 4.0）生成本案例的 data/*.csv。

原始文件：Supply chain logisitcs problem.xlsx（文件名的拼写照原样），7 个工作表。据配套论文（Dzalbs & Kalganova 2020,
Computers & Industrial Engineering 147:106610）第 4 节，这是一家全球芯片制造商提供的真实出库物流数据：9,215 张订单、
19 个仓库（原列名 Plant Code）、若干港口与承运商；订单表是历史上这些订单的实际路由记录，其余工作表是当前的网络约束。
改动只有三类，原始取值一律不改：
- 每个工作表存成一个 CSV，表名、列名译成中文；行序不变；去掉工作表右侧没有列名的空白列。
- 订单日期在 xlsx 里是日期单元格，写成「YYYY-MM-DD」（原值都是 2013-05-26 00:00:00）。
- 数字按 xlsx 里存的值原样写出（例如订单编号 1447296446.7、运费 43.227199999999996），文字里的空格照原样保留（例如运输方式「AIR   」）。

用法：python3 -I build_data.py <Supply chain logisitcs problem.xlsx> <输出目录>（需要 openpyxl）
"""

import csv
import datetime
import sys
from pathlib import Path

import openpyxl

SHEETS = {
    "OrderList": ("订单", {
        "Order ID": "订单编号", "Order Date": "订单日期", "Origin Port": "起运港", "Carrier": "承运商", "TPT": "运输天数",
        "Service Level": "服务方式", "Ship ahead day count": "提前发货天数", "Ship Late Day count": "延迟发货天数",
        "Customer": "客户", "Product ID": "产品编号", "Plant Code": "仓库代码", "Destination Port": "目的港",
        "Unit quantity": "数量", "Weight": "重量"}),
    "FreightRates": ("运费费率", {
        "Carrier": "承运商", "orig_port_cd": "起运港", "dest_port_cd": "目的港", "minm_wgh_qty": "最小重量",
        "max_wgh_qty": "最大重量", "svc_cd": "服务方式", "minimum cost": "最低运费", "rate": "费率", "mode_dsc": "运输方式",
        "tpt_day_cnt": "运输天数", "Carrier type": "承运商类型"}),
    "WhCosts": ("仓库成本", {"WH": "仓库代码", "Cost/unit": "单位仓储成本"}),
    "WhCapacities": ("仓库产能", {"Plant ID": "仓库代码", "Daily Capacity ": "日处理订单能力"}),
    "ProductsPerPlant": ("仓库可供产品", {"Plant Code": "仓库代码", "Product ID": "产品编号"}),
    "VmiCustomers": ("VMI客户", {"Plant Code": "仓库代码", "Customers": "客户"}),
    "PlantPorts": ("仓库港口", {"Plant Code": "仓库代码", "Port": "港口"}),
}


def cell(v) -> str:
    if v is None:
        return ""
    if isinstance(v, datetime.datetime):
        assert v.time() == datetime.time(0), v
        return v.date().isoformat()
    return str(v)


def main(src: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    book = openpyxl.load_workbook(src, read_only=True, data_only=True)
    assert [ws.title for ws in book.worksheets] == list(SHEETS), [ws.title for ws in book.worksheets]
    for sheet, (name, mapping) in SHEETS.items():
        rows = [r for r in book[sheet].iter_rows(values_only=True) if any(v is not None for v in r)]
        keep = [i for i, h in enumerate(rows[0]) if h is not None]
        header = [rows[0][i] for i in keep]
        assert header == list(mapping), (sheet, header)
        assert all(r[i] is None for r in rows for i in range(len(r)) if i not in keep), sheet
        with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([mapping[h] for h in header])
            writer.writerows([[cell(r[i]) for i in keep] for r in rows[1:]])
        print(f"{name}.csv\t{len(rows) - 1} 行")


if __name__ == "__main__":
    main(*sys.argv[1:3])
