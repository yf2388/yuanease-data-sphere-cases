"""从 Google Malloy 官方样例仓库 malloydata/malloy-samples 的 thelook 电商数据（data/*.parquet）生成本案例的 data/*.csv。

thelook 是 Looker / Google 用来演示语义层的虚构电商数据库（样例仓库 README：fictitious eCommerce business），MIT 许可；
Malloy 样例 ecommerce/ecommerce.malloy 在它上面定义了销售额、毛利、订单数等度量和一组看板视图。
改动只有三类，原始取值一律不改：
- 裁剪行：只取所在州（state）为 Florida 的用户，以及这些用户的全部订单明细、订单明细引用的库存件、库存件引用的商品（外键完整）。
- 去列：用户表不带姓名、邮箱、邮编、经纬度（虽然是虚构数据，也不带个人信息样式的字段）。其余列全部保留，表名、列名译成中文，行序不变。
- 格式：parquet 里的时间写成「YYYY-MM-DD HH:MM:SS」，日期写成「YYYY-MM-DD」，空值写成空单元格；数字按 parquet 里存的值原样写出。

用法：python3 -I build_data.py <malloy-samples 的 data 目录> <输出目录>（需要 pyarrow）
"""

import csv
import sys
from pathlib import Path

import pyarrow.parquet as pq

TABLES = {  # 源表 → (输出表名, {原列名: 中文列名}；不在映射里的列丢弃)
    "users": ("用户", {"id": "用户编号", "age": "年龄", "gender": "性别", "city": "城市", "state": "州", "country": "国家",
                     "created_at": "注册时间", "traffic_source": "来源渠道"}),
    "order_items": ("订单明细", {"id": "订单明细编号", "order_id": "订单编号", "user_id": "用户编号", "inventory_item_id": "库存件编号",
                              "sale_price": "售价", "status": "状态", "created_at": "下单时间", "returned_at": "退货时间",
                              "shipped_at": "发货时间", "delivered_at": "送达时间"}),
    "inventory_items": ("库存件", {"id": "库存件编号", "product_id": "商品编号", "created_at": "入库日期", "sold_at": "售出日期",
                                 "cost": "成本", "product_category": "商品品类", "product_name": "商品名称", "product_brand": "商品品牌",
                                 "product_retail_price": "商品零售价", "product_department": "商品部门", "product_sku": "商品SKU",
                                 "product_distribution_center_id": "商品配送中心编号"}),
    "products": ("商品", {"id": "商品编号", "cost": "成本", "category": "品类", "name": "商品名称", "brand": "品牌",
                        "retail_price": "零售价", "department": "部门", "sku": "SKU", "distribution_center_id": "配送中心编号"}),
}
DROPPED_USER_COLUMNS = {"first_name", "last_name", "email", "zip", "latitude", "longitude"}


def cell(v) -> str:
    return "" if v is None else str(v)


def write(out: Path, src: str, rows: list) -> None:
    name, mapping = TABLES[src]
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(list(mapping.values()))
        writer.writerows([[cell(r[k]) for k in mapping] for r in rows])
    print(f"{name}.csv\t{len(rows)} 行")


def main(src_dir: str, out_dir: str) -> None:
    src, out = Path(src_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    load = {t: pq.read_table(src / f"{t}.parquet").to_pylist() for t in TABLES}
    cols = set(load["users"][0])
    assert cols == set(TABLES["users"][1]) | DROPPED_USER_COLUMNS, cols
    for t in ("order_items", "inventory_items", "products"):
        assert set(load[t][0]) == set(TABLES[t][1]), (t, set(load[t][0]) ^ set(TABLES[t][1]))
    users = [u for u in load["users"] if u["state"] == "Florida"]
    uid = {u["id"] for u in users}
    items = [r for r in load["order_items"] if r["user_id"] in uid]
    inv_ids = {r["inventory_item_id"] for r in items}
    inventory = [r for r in load["inventory_items"] if r["id"] in inv_ids]
    prod_ids = {r["product_id"] for r in inventory}
    products = [r for r in load["products"] if r["id"] in prod_ids]
    assert len(inventory) == len(inv_ids) and len(products) == len(prod_ids)
    write(out, "users", users)
    write(out, "order_items", items)
    write(out, "inventory_items", inventory)
    write(out, "products", products)


if __name__ == "__main__":
    main(*sys.argv[1:3])
