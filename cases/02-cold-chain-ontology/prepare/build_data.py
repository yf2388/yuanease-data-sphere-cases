"""从 microsoft/fabric-samples 的 docs-samples/iq/ontology/new-experience 生成本案例的 data/*.csv。

改动：表名与列名汉化；布尔值 true/false 写成「是/否」；ISO 时间戳（UTC，带 Z）写成「YYYY-MM-DD HH:MM:SS」；其余取值原样保留。
不含 SalesReport.pbix（Power BI 语义模型，原教程用它建「销售」实体）。

用法：python3 -I build_data.py <new-experience 目录> <输出目录>
"""

import csv
import re
import sys
from pathlib import Path

TABLES = {
    "dimlocations": ("地点", {
        "LocationId": "地点编号", "LocationType": "地点类型", "Name": "名称", "Region": "区域", "City": "城市",
        "StateProvince": "州省", "Country": "国家", "PriorityTier": "优先级", "OperatingStatus": "营业状态",
        "SellingAreaSqFt": "营业面积_平方英尺", "StorageCapacityPallets": "仓储容量_托盘", "Latitude": "纬度",
        "Longitude": "经度"}),
    "dimproducts": ("产品", {
        "ProductId": "产品编号", "ProductName": "产品名称", "Brand": "品牌", "Category": "品类", "Subcategory": "子品类",
        "StorageClass": "储存类别", "MinimumStorageTempC": "最低储存温度_摄氏度", "MaximumStorageTempC": "最高储存温度_摄氏度",
        "ShelfLifeDays": "保质期_天", "SellByDateRequired": "需标注售卖期限", "SupplierId": "供应商编号",
        "StandardUnitPrice": "标准售价", "StandardUnitCost": "标准成本"}),
    "dimsuppliers": ("供应商", {
        "SupplierId": "供应商编号", "SupplierName": "供应商名称", "Country": "国家",
        "ServiceLevelTargetPct": "服务水平目标_百分比", "PrimaryContactRole": "主要联系角色", "Active": "是否启用"}),
    "dim_refrigeration_units": ("冷柜", {
        "UnitId": "冷柜编号", "StoreId": "门店编号", "Model": "型号", "Zone": "区位",
        "MinimumSafeTempC": "最低安全温度_摄氏度", "MaximumSafeTempC": "最高安全温度_摄氏度",
        "CommissionedDate": "投用日期", "Active": "是否启用"}),
    "fact_inventory_positions": ("库存", {
        "StoreId": "门店编号", "ProductId": "产品编号", "SnapshotDateTime": "快照时间", "OnHandQuantity": "在库数量",
        "SafetyStockQuantity": "安全库存", "ReorderPointQuantity": "再订货点", "InboundQuantity": "在途数量",
        "ShelfAvailableUnits": "货架可售数量", "ShelfCapacityUnits": "货架容量", "NextDeliveryDateTime": "下次到货时间",
        "InventoryStatus": "库存状态"}),
    "factshipments": ("货运", {
        "ShipmentId": "货运单号", "FromLocationId": "发出地点编号", "ToStoreId": "目的门店编号", "ProductId": "产品编号",
        "Quantity": "数量", "ScheduledArrival": "计划到达时间", "EstimatedArrival": "预计到达时间", "Status": "状态",
        "Carrier": "承运商", "TemperatureControlled": "是否温控"}),
    "refrigeration_telemetry": ("冷柜遥测", {
        "TelemetryId": "遥测编号", "UnitId": "冷柜编号", "Timestamp": "时间", "TemperatureC": "温度_摄氏度",
        "HumidityPct": "湿度_百分比", "DoorOpen": "门是否打开", "SensorStatus": "传感器状态"}),
}
STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.\d+)?Z$")


def cell(value: str) -> str:
    if value.lower() in ("true", "false"):
        return "是" if value.lower() == "true" else "否"
    m = STAMP.match(value)
    return f"{m.group(1)} {m.group(2)}" if m else value


def main(src: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for stem, (name, mapping) in TABLES.items():
        with open(Path(src) / f"{stem}.csv", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))
        header = [mapping[h] for h in rows[0]]
        with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows([[cell(v) for v in r] for r in rows[1:]])
        print(f"{name}.csv\t{len(rows) - 1} 行")


if __name__ == "__main__":
    main(*sys.argv[1:3])
