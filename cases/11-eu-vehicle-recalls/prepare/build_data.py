"""从欧盟 Safety Gate（非食品类危险产品快速预警系统）2025 年的 52 份周报生成本案例的 data/*.csv。

原始文件：周报索引 list/xml/en，以及 2025 年每份周报的 XML（下载地址与 sha256 见 prepare/sources.tsv）。周报由欧盟委员会发布，
内容按委员会网站法律声明以 CC BY 4.0 授权；本案例只用文字字段，不含周报里的产品图片。
改动只有四类，原始取值一律不改（文字连首尾空格照原样保留）：
- 裁剪行：只取产品类别（category）为 Motor vehicles 的通报，共 448 条。
- 召回通报：一条通报一行，字段名译成中文；不含类别列（全部相同）、图片、以及在机动车通报里全部为空的批号、条码、网店三列；
  另记下通报所在的周报编号（来自周报索引的 reference）。
- 周报：取周报索引里 2025 年的 52 份周报，字段名译成中文，另给出由发布日期推出的标准日期（YYYY-MM-DD）。
- 通报风险：通报的风险类型可能是复合的（例如 Fire, Injuries），按「, 」拆成一行一个风险类型，便于按单一风险统计。

用法：python3 -I build_data.py <下载目录：含 list-en.xml 与 weekly/Report-2025-*.xml> <输出目录>
"""

import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FIELDS = {  # 周报 XML 里 notifications 的子元素 → 中文列名
    "caseNumber": "通报编号", "order": "周内序号", "product": "产品类型", "brand": "品牌", "name": "车型",
    "type_numberOfModel": "型号或型式批准号", "riskType": "风险类型", "level": "风险等级", "danger": "风险说明",
    "measures": "措施", "description": "产品说明", "notifyingCountry": "通报国", "countryOfOrigin": "原产国",
    "type": "用户类型", "productionDates": "生产日期", "companyRecallCode": "企业召回编号", "URLrecall": "召回公告链接",
    "reference": "通报详情链接",
}
DROPPED = {"category", "batchNumber", "barcode", "onlineTrader", "pictures"}


def write(out: Path, name: str, header: list, rows: list) -> None:
    with open(out / f"{name}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"{name}.csv\t{len(rows)} 行")


def main(src: str, out_dir: str) -> None:
    src, out = Path(src), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    reports = [w for w in ET.parse(src / "list-en.xml").getroot().findall("weeklyReport") if w.findtext("year") == "2025"]
    assert len(reports) == 52, len(reports)
    weeks, notes, risks = [], [], []
    for w in sorted(reports, key=lambda w: int(w.findtext("week"))):
        ref, (d, m, y) = w.findtext("reference"), w.findtext("publicationDate").split("/")
        weeks.append([ref, w.findtext("publicationDate"), f"{y}-{m}-{d}", w.findtext("year"), w.findtext("week")])
        root = ET.parse(src / "weekly" / f"{ref}.xml").getroot()
        assert f"Report-{root.findtext('report_year')}-{root.findtext('report_week')}" == ref, ref
        for n in root.findall("notifications"):
            if n.findtext("category") != "Motor vehicles":
                continue
            tags = {c.tag for c in n}
            assert tags <= set(FIELDS) | DROPPED, tags - set(FIELDS) - DROPPED
            assert all(not (n.findtext(t) or "").strip() for t in ("batchNumber", "barcode", "onlineTrader")), n.findtext("caseNumber")
            row = {f: n.findtext(f) or "" for f in FIELDS}
            notes.append([row["caseNumber"], ref] + [row[f] for f in list(FIELDS)[1:]])
            risks += [[row["caseNumber"], r] for r in row["riskType"].split(", ")]
    assert len({r[0] for r in notes}) == len(notes)
    write(out, "周报", ["周报编号", "发布日期", "标准日期", "年份", "周次"], weeks)
    write(out, "召回通报", ["通报编号", "周报编号"] + [FIELDS[f] for f in list(FIELDS)[1:]], notes)
    write(out, "通报风险", ["通报编号", "风险类型"], risks)


if __name__ == "__main__":
    main(*sys.argv[1:3])
