"""从 microsoft/sql-server-samples 的 AdventureWorks OLTP 安装脚本数据生成本案例（采购与供应商）的 data/*.csv。

原始 CSV 为制表符分隔、无表头（列顺序见 instawdb.sql 的 CREATE TABLE）。改动：
- 只取采购相关的 5 张表，加上产品、产品子类、产品大类、计量单位 4 张维表；表名、列名汉化；产品大类与子类名称汉化；
- 去掉 rowguid 与 ModifiedDate 两个审计列；产品只保留 8 个基本列；
- 采购单状态按建库脚本的列说明（1 = Pending; 2 = Approved; 3 = Rejected; 4 = Complete）写成「待审批/已批准/已驳回/已完成」；
- 标志位 0/1 写成「否/是」；时间写成「YYYY-MM-DD」；全量，不抽样。
采购单的 EmployeeID 指向本案例不含的员工表，只作为属性列保留。

用法：python3 -I build_data.py <oltp-install-script 目录> <输出目录>
"""

import csv
import sys
from pathlib import Path

CATEGORIES = {"Bikes": "整车", "Components": "零部件", "Clothing": "服装", "Accessories": "配件"}
SUBCATEGORIES = {
    "Mountain Bikes": "山地车", "Road Bikes": "公路车", "Touring Bikes": "旅行车", "Handlebars": "车把",
    "Bottom Brackets": "中轴", "Brakes": "刹车", "Chains": "链条", "Cranksets": "曲柄", "Derailleurs": "变速器",
    "Forks": "前叉", "Headsets": "车头碗组", "Mountain Frames": "山地车架", "Pedals": "脚踏", "Road Frames": "公路车架",
    "Saddles": "车座", "Touring Frames": "旅行车架", "Wheels": "车轮", "Bib-Shorts": "背带短裤", "Caps": "骑行帽",
    "Gloves": "手套", "Jerseys": "骑行服", "Shorts": "短裤", "Socks": "袜子", "Tights": "紧身裤", "Vests": "背心",
    "Bike Racks": "车架挂架", "Bike Stands": "驻车架", "Bottles and Cages": "水壶与壶架", "Cleaners": "清洁剂",
    "Fenders": "挡泥板", "Helmets": "头盔", "Hydration Packs": "水袋背包", "Lights": "车灯", "Locks": "车锁",
    "Panniers": "驮包", "Pumps": "打气筒", "Tires and Tubes": "轮胎与内胎",
}
STATUS = {"1": "待审批", "2": "已批准", "3": "已驳回", "4": "已完成"}
FLAG, DATE, DROP = "flag", "date", None

TABLES = {
    "Vendor": ("供应商", [
        ("BusinessEntityID", "供应商编号", None), ("AccountNumber", "供应商账号", None), ("Name", "供应商名称", None),
        ("CreditRating", "信用等级", None), ("PreferredVendorStatus", "是否优选", FLAG), ("ActiveFlag", "是否启用", FLAG),
        ("PurchasingWebServiceURL", "采购网址", None), ("ModifiedDate", DROP, None)]),
    "ProductVendor": ("产品供货", [
        ("ProductID", "产品编号", None), ("BusinessEntityID", "供应商编号", None), ("AverageLeadTime", "平均交期_天", None),
        ("StandardPrice", "标准采购价", None), ("LastReceiptCost", "最近收货成本", None),
        ("LastReceiptDate", "最近收货日期", DATE), ("MinOrderQty", "最小订购量", None), ("MaxOrderQty", "最大订购量", None),
        ("OnOrderQty", "在途订购量", None), ("UnitMeasureCode", "计量单位代码", None), ("ModifiedDate", DROP, None)]),
    "PurchaseOrderHeader": ("采购单", [
        ("PurchaseOrderID", "采购单号", None), ("RevisionNumber", "修订次数", None), ("Status", "状态", STATUS),
        ("EmployeeID", "采购员工号", None), ("VendorID", "供应商编号", None), ("ShipMethodID", "运输方式编号", None),
        ("OrderDate", "下单日期", DATE), ("ShipDate", "发运日期", DATE), ("SubTotal", "小计", None),
        ("TaxAmt", "税额", None), ("Freight", "运费", None), ("TotalDue", "应付总额", None), ("ModifiedDate", DROP, None)]),
    "PurchaseOrderDetail": ("采购明细", [
        ("PurchaseOrderID", "采购单号", None), ("PurchaseOrderDetailID", "明细行号", None),
        ("DueDate", "要求到货日期", DATE), ("OrderQty", "订购数量", None), ("ProductID", "产品编号", None),
        ("UnitPrice", "单价", None), ("LineTotal", "行金额", None), ("ReceivedQty", "收货数量", None),
        ("RejectedQty", "拒收数量", None), ("StockedQty", "入库数量", None), ("ModifiedDate", DROP, None)]),
    "ShipMethod": ("运输方式", [
        ("ShipMethodID", "运输方式编号", None), ("Name", "运输方式名称", None), ("ShipBase", "起步运费", None),
        ("ShipRate", "每磅运费", None), ("rowguid", DROP, None), ("ModifiedDate", DROP, None)]),
    "Product": ("产品", [
        ("ProductID", "产品编号", None), ("Name", "产品名称", None), ("ProductNumber", "产品代码", None),
        ("MakeFlag", "是否自制", FLAG), ("FinishedGoodsFlag", DROP, None), ("Color", "颜色", None),
        ("SafetyStockLevel", DROP, None), ("ReorderPoint", DROP, None), ("StandardCost", "标准成本", None),
        ("ListPrice", "标价", None), ("Size", DROP, None), ("SizeUnitMeasureCode", DROP, None),
        ("WeightUnitMeasureCode", DROP, None), ("Weight", DROP, None), ("DaysToManufacture", DROP, None),
        ("ProductLine", DROP, None), ("Class", DROP, None), ("Style", DROP, None),
        ("ProductSubcategoryID", "产品子类编号", None), ("ProductModelID", DROP, None), ("SellStartDate", DROP, None),
        ("SellEndDate", DROP, None), ("DiscontinuedDate", DROP, None), ("rowguid", DROP, None), ("ModifiedDate", DROP, None)]),
    "ProductSubcategory": ("产品子类", [
        ("ProductSubcategoryID", "产品子类编号", None), ("ProductCategoryID", "产品大类编号", None),
        ("Name", "子类名称", SUBCATEGORIES), ("rowguid", DROP, None), ("ModifiedDate", DROP, None)]),
    "ProductCategory": ("产品大类", [
        ("ProductCategoryID", "产品大类编号", None), ("Name", "大类名称", CATEGORIES), ("rowguid", DROP, None),
        ("ModifiedDate", DROP, None)]),
    "UnitMeasure": ("计量单位", [
        ("UnitMeasureCode", "计量单位代码", None), ("Name", "计量单位名称", None), ("ModifiedDate", DROP, None)]),
}


def convert(value: str, how) -> str:
    value = value.strip()
    if how == FLAG:
        return {"0": "否", "1": "是"}[value]
    if how == DATE:
        return value[:10]
    if isinstance(how, dict):
        return how[value]
    if value.startswith(".") or value.startswith("-."):  # 原始金额写成 .0000
        value = value.replace(".", "0.", 1)
    return value


def main(src_dir: str, out_dir: str) -> None:
    src, out = Path(src_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for stem, (name, columns) in TABLES.items():
        text = (src / f"{stem}.csv").read_text(encoding="utf-8-sig")
        rows = [line.split("\t") for line in text.split("\n") if line.strip()]
        assert all(len(r) == len(columns) for r in rows), (stem, {len(r) for r in rows})
        kept = [(i, cn, how) for i, (_, cn, how) in enumerate(columns) if cn]
        with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([cn for _, cn, _ in kept])
            writer.writerows([[convert(r[i], how) for i, _, how in kept] for r in rows])
        print(f"{name}.csv\t{len(rows)} 行")


if __name__ == "__main__":
    main(*sys.argv[1:3])
