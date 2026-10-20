"""从 Snowflake 供应链助手仓库的 setup.sql 生成本案例的 data/*.csv。

只把 INSERT 语句当文本解析，不执行任何 SQL。改动：表名与列名汉化；布尔值 TRUE/FALSE 写成「是/否」；
时间戳去掉时区后缀写成「YYYY-MM-DD HH:MM:SS」；NULL 写成空单元格；其余取值原样保留。不含天气表与会话表。

用法：python3 -I build_data.py <setup.sql 路径> <输出目录>
"""

import csv
import re
import sys
from pathlib import Path

TABLES = {
    "SUPPLIERS": ("供应商", {
        "SUPPLIER_ID": "供应商编号", "SUPPLIER_NAME": "供应商名称", "ADDRESS": "地址", "CITY": "城市", "STATE": "州省",
        "COUNTRY": "国家", "ZIP_CODE": "邮编", "CONTACT_PERSON_NAME": "联系人", "CONTACT_EMAIL": "联系邮箱",
        "CONTACT_PHONE": "联系电话", "SUPPLIER_TYPE": "供应商类型", "BUSINESS_LINE": "业务线", "IS_PREFERRED": "是否优选",
        "PAYMENT_TERMS": "付款条件"}),
    "RAW_MATERIAL": ("原材料", {
        "MATERIAL_ID": "原材料编号", "MATERIAL_NAME": "原材料名称", "MATERIAL_DESCRIPTION": "原材料说明",
        "SUPPLIER_ID": "供应商编号", "MATERIAL_COST": "采购单价", "PLANT_TRANSPORT_COST": "厂间运输基准成本",
        "BUSINESS_LINE": "业务线"}),
    "COMPONENT": ("零部件", {
        "COMPONENT_ID": "零部件编号", "COMPONENT_NAME": "零部件名称", "COMPONENT_DESCRIPTION": "零部件说明",
        "BILL_OF_MATERIALS_ID": "关联物料清单", "BUSINESS_LINE": "业务线"}),
    "PRODUCT": ("产品", {
        "PRODUCT_ID": "产品编号", "PRODUCT_NAME": "产品名称", "PRODUCT_DESCRIPTION": "产品说明",
        "PRODUCT_CATEGORY": "产品类别", "UNIT_PRICE": "单价", "BUSINESS_LINE": "业务线"}),
    "MFG_PLANT": ("工厂", {
        "MFG_PLANT_ID": "工厂编号", "MFG_PLANT_NAME": "工厂名称", "ADDRESS": "地址", "CITY": "城市", "STATE": "州省",
        "COUNTRY": "国家", "ZIP_CODE": "邮编", "LATITUDE": "纬度", "LONGITUDE": "经度",
        "PLANT_MANAGER_CONTACT_ID": "厂长联系人编号", "SQUARE_FOOTAGE": "面积_平方英尺", "NUMBER_OF_EMPLOYEES": "员工人数",
        "IS_ACTIVE": "是否在产", "BUSINESS_LINE": "业务线"}),
    "CUSTOMER": ("客户", {
        "CUSTOMER_ID": "客户编号", "CUSTOMER_NAME": "客户名称", "ADDRESS": "地址", "CITY": "城市", "STATE": "州省",
        "COUNTRY": "国家", "ZIP_CODE": "邮编", "CONTACT_PERSON_ID": "联系人编号", "INDUSTRY": "行业",
        "BUSINESS_LINE": "业务线"}),
    "BILL_OF_MATERIALS": ("物料清单", {
        "BOM_ID": "物料清单编号", "PARENT_PRODUCT_ID": "父产品编号", "PARENT_COMPONENT_ID": "父零部件编号",
        "CHILD_MATERIAL_ID": "子原材料编号", "CHILD_COMPONENT_ID": "子零部件编号", "QUANTITY_REQUIRED": "单位用量",
        "UNIT_OF_MEASURE": "计量单位", "SCRAP_FACTOR": "损耗率", "EFFECTIVE_DATE": "生效日期",
        "EXPIRATION_DATE": "失效日期"}),
    "MFG_INVENTORY": ("工厂库存", {
        "MFG_PLANT_ID": "工厂编号", "MATERIAL_ID": "原材料编号", "COMPONENT_ID": "零部件编号", "PRODUCT_ID": "产品编号",
        "QUANTITY_ON_HAND": "在库数量", "QUANTITY_ON_ORDER": "在途数量", "SAFETY_STOCK_LEVEL": "安全库存",
        "REPLENISHMENT_POINT": "补货目标量", "LAST_UPDATED_TIMESTAMP": "最后更新时间",
        "MATERIAL_LEAD_TIME": "采购提前期_天", "DAYS_FORWARD_COVERAGE": "可支撑天数",
        "LEAD_TIME_VARIABILITY": "提前期波动_天"}),
    "ORDERS": ("订单", {
        "ORDER_ID": "订单编号", "CUSTOMER_ID": "客户编号", "MFG_PLANT_ID": "工厂编号", "ORDER_DATE": "下单时间",
        "PRODUCT_ID": "产品编号", "QUANTITY": "数量", "UNIT_PRICE": "单价", "TOTAL_PRICE": "订单金额",
        "ORDER_STATUS": "订单状态"}),
    "SHIPMENT": ("发货", {
        "SHIPMENT_ID": "发货单号", "ORIGIN_MFG_PLANT_ID": "发货工厂编号", "DESTINATION_CUSTOMER_ID": "收货客户编号",
        "SHIP_DATE": "发货日期", "EXPECTED_DELIVERY_DATE": "预计到货日期", "ACTUAL_DELIVERY_DATE": "实际到货日期",
        "SHIPPING_COST": "运费", "TRACKING_NUMBER": "运单号"}),
    "TRANSPORT_COST_SURCHARGE": ("厂间运输附加费", {
        "SOURCE_FACILITY_ID": "调出工厂编号", "DESTINATION_FACILITY_ID": "调入工厂编号",
        "TRANSPORT_COST_SURCHARGE": "运输附加系数"}),
}

INSERT = re.compile(r"INSERT INTO (\w+) \(([^)]*)\) VALUES\s*(.*?);\s*$", re.S | re.M)
TOKEN = re.compile(r"\s*('(?:[^']|'')*'|[^,()]+)\s*(,|\))")
STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.\d+)?Z?$")


def rows(values: str):
    """逐个解析 ``(v1, v2, …)`` 元组；字符串里的 ``''`` 还原为单引号。"""

    pos = 0
    while (start := values.find("(", pos)) != -1:
        pos, row = start + 1, []
        while True:
            m = TOKEN.match(values, pos)
            if not m:
                raise ValueError(f"无法解析：{values[pos:pos + 80]!r}")
            raw, pos = m.group(1).strip(), m.end()
            row.append(raw)
            if m.group(2) == ")":
                break
        yield row


def cell(raw: str) -> str:
    if raw.upper() == "NULL":
        return ""
    if raw.upper() in ("TRUE", "FALSE"):
        return "是" if raw.upper() == "TRUE" else "否"
    if raw.startswith("'"):
        text = raw[1:-1].replace("''", "'")
        m = STAMP.match(text)
        return f"{m.group(1)} {m.group(2)}" if m else text
    return raw


def main(sql_path: str, out_dir: str) -> None:
    text = Path(sql_path).read_text(encoding="utf-8")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    seen = {}
    for m in INSERT.finditer(text):
        table = m.group(1)
        if table not in TABLES:
            continue
        name, mapping = TABLES[table]
        columns = [c.strip() for c in m.group(2).split(",")]
        data = [[cell(v) for v in row] for row in rows(m.group(3))]
        assert all(len(r) == len(columns) for r in data), table
        seen.setdefault(table, (name, columns, mapping, []))[3].extend(data)
    assert set(seen) == set(TABLES), set(TABLES) - set(seen)
    for name, columns, mapping, data in seen.values():
        with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow([mapping[c] for c in columns])
            writer.writerows(data)
        print(f"{name}.csv\t{len(data)} 行")


if __name__ == "__main__":
    main(*sys.argv[1:3])
