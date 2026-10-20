"""从 microsoft/sql-server-samples 的 AdventureWorks OLTP 安装脚本数据生成本案例的 data/*.csv。

原始 CSV 为制表符分隔、无表头（列顺序见 instawdb.sql 的 CREATE TABLE）。改动：
- 只取生产相关的 11 张表；表名、列名汉化；工位、报废原因、产品大类与子类的名称汉化（原文见本文件的对照表）；
- 去掉 rowguid 与 ModifiedDate 两个审计列，去掉产品型号的两个 XML 列；
- 标志位 0/1 写成「否/是」；时间写成「YYYY-MM-DD」（原始数据的时分秒都是 00:00:00）；
- 抽样：工单只取开工日期在 2025-05-01 至 2025-05-31 之间的工单，工单工序只取这些工单的工序（外键完整）；其余表全量。

用法：python3 -I build_data.py <oltp-install-script 目录> <输出目录>
"""

import csv
import sys
from pathlib import Path

LOCATIONS = {
    "Tool Crib": "工具库", "Sheet Metal Racks": "钣金料架", "Paint Shop": "油漆车间", "Paint Storage": "油漆库",
    "Metal Storage": "金属材料库", "Miscellaneous Storage": "杂项库", "Finished Goods Storage": "成品库",
    "Frame Forming": "车架成型", "Frame Welding": "车架焊接", "Debur and Polish": "去毛刺抛光", "Paint": "喷漆",
    "Specialized Paint": "特种喷漆", "Subassembly": "部件装配", "Final Assembly": "总装",
}
SCRAP = {
    "Brake assembly not as ordered": "制动总成与订单不符", "Color incorrect": "颜色错误", "Gouge in metal": "金属表面划伤",
    "Drill pattern incorrect": "钻孔图样错误", "Drill size too large": "钻孔尺寸过大", "Drill size too small": "钻孔尺寸过小",
    "Handling damage": "搬运损坏", "Paint process failed": "喷漆工艺失败", "Primer process failed": "底漆工艺失败",
    "Seat assembly not as ordered": "座椅总成与订单不符", "Stress test failed": "应力测试不合格",
    "Thermoform temperature too high": "热成型温度过高", "Thermoform temperature too low": "热成型温度过低",
    "Trim length too long": "修边长度过长", "Trim length too short": "修边长度过短", "Wheel misaligned": "车轮偏位",
}
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

# 源文件 → (输出表名, [(原列名, 中文列名或 None 表示丢弃, 取值转换)])
FLAG = "flag"
DATE = "date"
TABLES = {
    "Product": ("产品", [
        ("ProductID", "产品编号", None), ("Name", "产品名称", None), ("ProductNumber", "产品代码", None),
        ("MakeFlag", "是否自制", FLAG), ("FinishedGoodsFlag", "是否成品", FLAG), ("Color", "颜色", None),
        ("SafetyStockLevel", "安全库存", None), ("ReorderPoint", "再订货点", None), ("StandardCost", "标准成本", None),
        ("ListPrice", "标价", None), ("Size", "尺寸", None), ("SizeUnitMeasureCode", "尺寸单位代码", None),
        ("WeightUnitMeasureCode", "重量单位代码", None), ("Weight", "重量", None), ("DaysToManufacture", "制造天数", None),
        ("ProductLine", "产品线", None), ("Class", "等级", None), ("Style", "款式", None),
        ("ProductSubcategoryID", "产品子类编号", None), ("ProductModelID", "产品型号编号", None),
        ("SellStartDate", "开售日期", DATE), ("SellEndDate", "停售日期", DATE), ("DiscontinuedDate", "停产日期", DATE),
        ("rowguid", None, None), ("ModifiedDate", None, None)]),
    "ProductCategory": ("产品大类", [
        ("ProductCategoryID", "产品大类编号", None), ("Name", "大类名称", CATEGORIES), ("rowguid", None, None),
        ("ModifiedDate", None, None)]),
    "ProductSubcategory": ("产品子类", [
        ("ProductSubcategoryID", "产品子类编号", None), ("ProductCategoryID", "产品大类编号", None),
        ("Name", "子类名称", SUBCATEGORIES), ("rowguid", None, None), ("ModifiedDate", None, None)]),
    "ProductModel": ("产品型号", [
        ("ProductModelID", "产品型号编号", None), ("Name", "型号名称", None), ("CatalogDescription", None, None),
        ("Instructions", None, None), ("rowguid", None, None), ("ModifiedDate", None, None)]),
    "BillOfMaterials": ("物料清单", [
        ("BillOfMaterialsID", "物料清单编号", None), ("ProductAssemblyID", "装配件产品编号", None),
        ("ComponentID", "组件产品编号", None), ("StartDate", "生效日期", DATE), ("EndDate", "失效日期", DATE),
        ("UnitMeasureCode", "计量单位代码", None), ("BOMLevel", "层级", None), ("PerAssemblyQty", "单件用量", None),
        ("ModifiedDate", None, None)]),
    "Location": ("工位", [
        ("LocationID", "工位编号", None), ("Name", "工位名称", LOCATIONS), ("CostRate", "小时费率", None),
        ("Availability", "可用工时", None), ("ModifiedDate", None, None)]),
    "ProductInventory": ("产品库存", [
        ("ProductID", "产品编号", None), ("LocationID", "工位编号", None), ("Shelf", "货架", None), ("Bin", "货位", None),
        ("Quantity", "数量", None), ("rowguid", None, None), ("ModifiedDate", None, None)]),
    "ScrapReason": ("报废原因", [
        ("ScrapReasonID", "报废原因编号", None), ("Name", "报废原因", SCRAP), ("ModifiedDate", None, None)]),
    "UnitMeasure": ("计量单位", [
        ("UnitMeasureCode", "计量单位代码", None), ("Name", "计量单位名称", None), ("ModifiedDate", None, None)]),
    "WorkOrder": ("工单", [
        ("WorkOrderID", "工单编号", None), ("ProductID", "产品编号", None), ("OrderQty", "计划数量", None),
        ("StockedQty", "入库数量", None), ("ScrappedQty", "报废数量", None), ("StartDate", "开工日期", DATE),
        ("EndDate", "完工日期", DATE), ("DueDate", "交期", DATE), ("ScrapReasonID", "报废原因编号", None),
        ("ModifiedDate", None, None)]),
    "WorkOrderRouting": ("工单工序", [
        ("WorkOrderID", "工单编号", None), ("ProductID", "产品编号", None), ("OperationSequence", "工序号", None),
        ("LocationID", "工位编号", None), ("ScheduledStartDate", "计划开始日期", DATE),
        ("ScheduledEndDate", "计划结束日期", DATE), ("ActualStartDate", "实际开始日期", DATE),
        ("ActualEndDate", "实际结束日期", DATE), ("ActualResourceHrs", "实际工时", None), ("PlannedCost", "计划成本", None),
        ("ActualCost", "实际成本", None), ("ModifiedDate", None, None)]),
}
SAMPLE_FROM, SAMPLE_TO = "2025-05-01", "2025-06-01"


def read(src: Path, stem: str) -> list[list[str]]:
    text = (src / f"{stem}.csv").read_text(encoding="utf-8-sig")
    if stem == "ProductModel":  # 该表用 +| 分隔字段、&| 结束一行（字段里有换行）
        return [r.split("+|") for r in text.split("&|\n") if r.strip()]
    return [line.split("\t") for line in text.split("\n") if line.strip()]


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
    keep_orders = None
    for stem in ["WorkOrder", "WorkOrderRouting"] + [t for t in TABLES if t not in ("WorkOrder", "WorkOrderRouting")]:
        name, columns = TABLES[stem]
        rows = read(src, stem)
        assert all(len(r) == len(columns) for r in rows), (stem, {len(r) for r in rows})
        if stem == "WorkOrder":
            rows = [r for r in rows if SAMPLE_FROM <= r[5][:10] < SAMPLE_TO]
            keep_orders = {r[0] for r in rows}
        elif stem == "WorkOrderRouting":
            rows = [r for r in rows if r[0] in keep_orders]
        kept = [(i, cn, how) for i, (_, cn, how) in enumerate(columns) if cn]
        with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([cn for _, cn, _ in kept])
            writer.writerows([[convert(r[i], how) for i, _, how in kept] for r in rows])
        print(f"{name}.csv\t{len(rows)} 行")


if __name__ == "__main__":
    main(*sys.argv[1:3])
