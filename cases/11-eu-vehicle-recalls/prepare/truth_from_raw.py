"""直接从 Safety Gate 原始周报 XML 独立重算本案例全部问答题的标准答案，并与 questions.yaml 的 expected 比对。

不经过 data/ 与 SQL：只读原始 XML 的元素名，用 Python 标准库计算，用来证明标准答案出自原始数据。
另外按 prepare/sources.tsv 核对每份周报 XML 的 sha256，确认用的是登记过的原始文件。

用法：python3 -I truth_from_raw.py <下载目录：含 list-en.xml 与 weekly/Report-2025-*.xml>
"""

import csv
import hashlib
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import yaml

CASE = Path(__file__).resolve().parent.parent
CN = "People's Republic of China"


def main(src: str) -> int:
    src = Path(src)
    with open(CASE / "prepare" / "sources.tsv", encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            if row["file"].startswith("weekly/"):
                assert hashlib.sha256((src / row["file"]).read_bytes()).hexdigest() == row["sha256"], row["file"]
    week_date = {}
    for w in ET.parse(src / "list-en.xml").getroot().findall("weeklyReport"):
        if w.findtext("year") == "2025":
            d, m, y = w.findtext("publicationDate").split("/")
            week_date[w.findtext("reference")] = f"{y}-{m}-{d}"
    notes = []  # (周报编号, 通报元素的取值字典)
    for ref in week_date:
        for n in ET.parse(src / "weekly" / f"{ref}.xml").getroot().findall("notifications"):
            if n.findtext("category") == "Motor vehicles":
                notes.append((ref, {c.tag: c.text or "" for c in n}))
    get = lambda k: [v[k] for _, v in notes]
    product = lambda v: v["product"].strip()
    risks = lambda v: v["riskType"].split(", ")
    brands = Counter(get("brand"))
    top3 = sorted(brands.items(), key=lambda x: (-x[1], x[0]))[:3]
    fire = sum("Fire" in risks(v) for _, v in notes)
    country = Counter(get("notifyingCountry")).most_common(1)[0]
    cn = [v for _, v in notes if v["countryOfOrigin"] == CN]
    cn_top = Counter(product(v) for v in cn).most_common(1)[0]
    per_week = Counter(ref for ref, _ in notes)
    pro = [v for _, v in notes if v["type"] == "Professional"]
    kia = [v for _, v in notes if v["brand"] == "Kia"]
    other = sorted((v["caseNumber"], v["brand"]) for _, v in notes if v["level"] != "Serious risk")
    truth = {
        "q01": [[len(notes), sum(product(v) == "Passenger car" for _, v in notes)]],
        "q02": [list(x) for x in top3],
        "q03": [[fire, round(fire / len(notes), 4)]],
        "q04": [list(country)],
        "q05": [[len(cn), *cn_top]],
        "q06": [[w, week_date[w], per_week[w]] for w in sorted(per_week) if per_week[w] == max(per_week.values())],
        "q07": [[sum("2025-07-01" <= week_date[ref] <= "2025-09-30" for ref, _ in notes)]],
        "q08": [[len(pro), sum(product(v) == "Lorry" for v in pro)]],
        "q09": [[len(kia), sum("Injuries" in risks(v) for v in kia)]],
        "q10": [[len(other), *x] for x in other],
    }
    doc = yaml.safe_load((CASE / "questions.yaml").read_text(encoding="utf-8"))
    bad = 0
    for q in doc["questions"]:
        exp, got = q["expected"]["rows"], truth[q["id"]]
        same = len(exp) == len(got) and all(
            len(a) == len(b) and all(abs(x - y) < 1e-4 if isinstance(x, (int, float)) and isinstance(y, (int, float)) else x == y for x, y in zip(a, b))
            for a, b in zip(exp, got))
        bad += not same
        print(f"[{q['id']}] {'一致' if same else '不一致'}  原始文件重算 {got}" + ("" if same else f"  questions.yaml {exp}"))
    print(f"{len(doc['questions']) - bad}/{len(doc['questions'])} 题与原始文件重算一致")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
