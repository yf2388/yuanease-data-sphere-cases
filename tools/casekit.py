"""案例工具：把 data/ 里的表格装进内存 SQLite，独立算出问答期望值、核验金标、给 App 的回答打分。

只依赖 Python 3.9+ 标准库与 PyYAML（读 .xlsx 时另需 openpyxl）。读取下载数据时请用 ``python3 -I`` 运行。

用法（在仓库根目录）::

    python3 -I tools/casekit.py answers cases/01-supply-chain-network          # 打印每题 SQL 的结果
    python3 -I tools/casekit.py answers cases/01-supply-chain-network --write  # 把结果写回 questions.yaml 的 expected
    python3 -I tools/casekit.py answers cases/01-supply-chain-network --check  # 重算并与 expected 比对（不一致退出码 1）
    python3 -I tools/casekit.py gold cases/01-supply-chain-network             # 用数据核验金标
    python3 -I tools/casekit.py gold-json cases/01-supply-chain-network out.json  # 金标转成打分器读的 JSON
    python3 -I tools/casekit.py grade cases/01-supply-chain-network answers/   # 给 answers/<题号>.txt 打分

表名 = 文件名去扩展名；.xlsx 的每个工作表是一张表，表名为「文件名/工作表」（SQL 里用双引号括起来）。
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
import sys
from pathlib import Path

import yaml

INT = re.compile(r"^-?\d+$")
FLOAT = re.compile(r"^-?(\d+\.\d*|\.\d+|\d+)([eE][-+]?\d+)?$")


# ── 装载 ──────────────────────────────────────────────────────────────


def _tables(data_dir: Path) -> dict[str, tuple[list[str], list[list[str]]]]:
    tables = {}
    for path in sorted(data_dir.iterdir()):
        if path.suffix.lower() == ".csv":
            with open(path, encoding="utf-8-sig", newline="") as fh:
                rows = list(csv.reader(fh))
            tables[path.stem] = (rows[0], rows[1:])
        elif path.suffix.lower() == ".xlsx":
            import openpyxl  # 只有 xlsx 案例需要

            book = openpyxl.load_workbook(path, read_only=True, data_only=True)
            for sheet in book.worksheets:
                rows = [["" if v is None else str(v) for v in row] for row in sheet.iter_rows(values_only=True)]
                tables[f"{path.stem}/{sheet.title}"] = (rows[0], rows[1:])
    return tables


def _affinity(values: list[str]) -> str:
    filled = [v for v in values if v != ""]
    if filled and all(INT.match(v) for v in filled):
        return "INTEGER"
    if filled and all(FLOAT.match(v) for v in filled):
        return "REAL"
    return "TEXT"


def connect(case_dir: Path) -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    for name, (header, rows) in _tables(case_dir / "data").items():
        kinds = [_affinity([r[i] if i < len(r) else "" for r in rows]) for i in range(len(header))]
        cols = ", ".join(f'"{h}" {k}' for h, k in zip(header, kinds))
        db.execute(f'CREATE TABLE "{name}" ({cols})')

        def conv(v: str, k: str):
            if v == "":
                return None
            return int(v) if k == "INTEGER" else float(v) if k == "REAL" else v

        db.executemany(
            f'INSERT INTO "{name}" VALUES ({", ".join("?" * len(header))})',
            [[conv(r[i] if i < len(r) else "", k) for i, k in enumerate(kinds)] for r in rows],
        )
    return db


def run(db: sqlite3.Connection, sql: str) -> list[list]:
    cur = db.execute(sql)
    out = []
    for row in cur.fetchall():
        out.append([round(v, 4) if isinstance(v, float) else v for v in row])
    return out


# ── 问答期望值 ────────────────────────────────────────────────────────


def cmd_answers(case_dir: Path, mode: str | None) -> int:
    qpath = case_dir / "questions.yaml"
    doc = yaml.safe_load(qpath.read_text(encoding="utf-8"))
    db = connect(case_dir)
    bad = 0
    for q in doc["questions"]:
        rows = run(db, q["sql"])
        result = {"columns": [d[0] for d in db.execute(q["sql"]).description], "rows": rows}
        if mode == "--check":
            if q.get("expected") != result:
                bad += 1
                print(f"[{q['id']}] 不一致：期望 {q.get('expected')}，重算 {result}")
        else:
            q["expected"] = result
            print(f"[{q['id']}] {q['question']}\n    → {result}")
    if mode == "--write":
        qpath.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    if mode == "--check":
        print(f"{len(doc['questions']) - bad}/{len(doc['questions'])} 题一致")
    return 1 if bad else 0


# ── 金标核验 ──────────────────────────────────────────────────────────


def _q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _where(filters: list[dict]) -> tuple[str, list]:
    parts, args = [], []
    for f in filters or []:
        col, op, val = _q(f["column"]), f["op"], f.get("value")
        if op == "is_null":
            parts.append(f"{col} IS {'' if val else 'NOT '}NULL")
        elif op in ("in", "not_in"):
            parts.append(f"{col} {'NOT ' if op == 'not_in' else ''}IN ({', '.join('?' * len(val))})")
            args.extend(val)
        else:
            sym = {"eq": "=", "ne": "<>", "gt": ">", "gte": ">=", "lt": "<", "lte": "<="}[op]
            parts.append(f"{col} {sym} ?")
            args.append(val)
    return (" WHERE " + " AND ".join(parts)) if parts else "", args


def _calc(db, table: str, m: dict):
    if m["aggregate"] == "ratio":
        num, den = _calc(db, table, m["numerator"]), _calc(db, table, m["denominator"])
        return None if not den else num / den
    where, args = _where(m.get("filters", []))
    agg = m["aggregate"]
    expr = "COUNT(*)" if agg == "count" else f"COUNT(DISTINCT {_q(m['column'])})" if agg == "count_distinct" else f"{agg.upper()}({_q(m['column'])})"
    return db.execute(f"SELECT {expr} FROM {_q(table)}{where}", args).fetchone()[0]


def load_gold(case_dir: Path) -> dict:
    """读 gold.yaml；YAML 1.1 会把不加引号的键 ``on`` 读成布尔 True，这里还原。"""

    gold = yaml.safe_load((case_dir / "gold.yaml").read_text(encoding="utf-8"))
    for r in gold.get("relations", []):
        if True in r and "on" not in r:
            r["on"] = r.pop(True)
    return gold


def cmd_gold(case_dir: Path) -> int:
    gold = load_gold(case_dir)
    db = connect(case_dir)
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    problems = 0

    def say(ok: bool, text: str):
        nonlocal problems
        problems += 0 if ok else 1
        print(("  ok  " if ok else "  !!  ") + text)

    print("实体与唯一标识列")
    for e in gold["entities"]:
        say(e["table"] in tables, f"表 {e['table']} 存在")
        if e["table"] not in tables:
            continue
        n = db.execute(f"SELECT COUNT(*) FROM {_q(e['table'])}").fetchone()[0]
        for cols in e.get("identifier", []):
            key = ", ".join(_q(c) for c in cols)
            distinct = db.execute(f"SELECT COUNT(*) FROM (SELECT DISTINCT {key} FROM {_q(e['table'])})").fetchone()[0]
            nulls = db.execute(f"SELECT COUNT(*) FROM {_q(e['table'])} WHERE " + " AND ".join(f"{_q(c)} IS NULL" for c in cols)).fetchone()[0]
            say(distinct == n and nulls == 0, f"{e['table']}：{'+'.join(cols)} 唯一（{distinct}/{n} 行，全空 {nulls} 行）")
    print("关系（子表非空键值落在父表的比例 ≥95%）")
    for r in gold.get("relations", []):
        cond = " AND ".join(f"c.{_q(a)} = p.{_q(b)}" for a, b in r["on"])
        nonnull = " AND ".join(f"c.{_q(a)} IS NOT NULL" for a, _ in r["on"])
        total = db.execute(f"SELECT COUNT(*) FROM {_q(r['from'])} c WHERE {nonnull}").fetchone()[0]
        hit = db.execute(
            f"SELECT COUNT(*) FROM {_q(r['from'])} c WHERE {nonnull} AND EXISTS (SELECT 1 FROM {_q(r['to'])} p WHERE {cond})"
        ).fetchone()[0]
        pct = 100.0 * hit / total if total else 0.0
        line = f"{r['from']} → {r['to']} {r['on']}：{hit}/{total}（{pct:.1f}%）"
        if r.get("waive") and not (total > 0 and pct >= 95):
            print(f"  注  {line}；豁免：{r['waive']}")
        else:
            say(total > 0 and pct >= 95, line)
    print("指标（能用同一批数据算出值）")
    for m in gold.get("metrics", []):
        try:
            value = _calc(db, m["table"], m)
            say(value is not None, f"{m['table']}：{m.get('label')} = {value}")
        except sqlite3.Error as exc:
            say(False, f"{m['table']}：{m.get('label')} 算不出：{exc}")
    print(f"{'通过' if not problems else f'{problems} 处不通过'}")
    return 1 if problems else 0


def cmd_gold_json(case_dir: Path, out: Path) -> int:
    gold = load_gold(case_dir)
    out.write_text(json.dumps(gold, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"写出 {out}")
    return 0


# ── App 回答打分 ──────────────────────────────────────────────────────


def _norm(text: str) -> str:
    return re.sub(r"[\s,，]", "", text).lower()


def _number_in(value: float, text: str, tolerance: float) -> bool:
    """回答里有没有这个数：去掉千分位逗号；「122万」「1.2亿」「3.9%」按单位折算。
    两种算对：相对误差不超过 tolerance；或回答按自己的精度四舍五入后相等（如 3.92% 答成 3.9%），此时回答至少要有 2 位有效数字。"""

    text = re.sub(r"(?<=\d)[,，](?=\d{3})", "", text)
    for token, unit in re.findall(r"(-?\d+(?:\.\d+)?)\s*(万|亿|%)?", text):
        scales = [{"万": 1e4, "亿": 1e8, "%": 0.01}.get(unit, 1)]
        if unit == "%" and abs(value) >= 1:  # 标准答案按百分点给（41.24）时，「41.24%」也按百分点比
            scales.append(1)
        for scale in scales:
            number = float(token) * scale
            if abs(number - value) <= max(tolerance * abs(value), 1e-9):
                return True
            digits = len(token.split(".")[1]) if "." in token else 0
            significant = len(token.lstrip("-").replace(".", "").lstrip("0"))
            if significant >= 2 and round(value / scale, digits) == float(token):
                return True
    return False


def grade_one(q: dict, text: str) -> tuple[bool, list[str]]:
    """``must_include``（缺省为期望结果的全部取值）里的每一项都要出现在回答里：数字按 ``tolerance`` 相对误差比对，文字忽略空白与大小写。"""

    missing = []
    items = q.get("must_include")
    if items is None:  # 默认：期望结果里的每个取值都要出现
        items = [v for row in q["expected"]["rows"] for v in row if v is not None]
    def found(item) -> bool:
        if isinstance(item, list):  # 备选写法，命中任一即可（如 [0, 没有]）
            return any(found(alt) for alt in item)
        if isinstance(item, (int, float)) and not isinstance(item, bool):
            return _number_in(float(item), text, float(q.get("tolerance", 0.005)))
        return _norm(str(item)) in _norm(text)

    for item in items:
        if not found(item):
            missing.append(str(item))
    return not missing, missing


def cmd_grade(case_dir: Path, answers: Path) -> int:
    doc = yaml.safe_load((case_dir / "questions.yaml").read_text(encoding="utf-8"))
    passed = 0
    for q in doc["questions"]:
        path = answers / f"{q['id']}.txt"
        if not path.exists():
            print(f"[{q['id']}] 无回答")
            continue
        ok, missing = grade_one(q, path.read_text(encoding="utf-8"))
        passed += ok
        print(f"[{q['id']}] {'对' if ok else '错'}" + ("" if ok else f"（缺：{'、'.join(missing)}）"))
    print(f"准确率 {passed}/{len(doc['questions'])} = {passed / len(doc['questions']):.1%}")
    return 0


# ── README 自动段落 ───────────────────────────────────────────────────


def _cell(v) -> str:
    if isinstance(v, float):
        v = f"{v:,.4f}".rstrip("0").rstrip(".")
    elif isinstance(v, int):
        v = f"{v:,}"
    return str(v).replace("|", "\\|")


def _blocks(case_dir: Path) -> dict[str, str]:
    gold, doc = load_gold(case_dir), yaml.safe_load((case_dir / "questions.yaml").read_text(encoding="utf-8"))
    ids = {e["table"]: " 或 ".join("+".join(c) for c in e.get("identifier", [])) or "无" for e in gold["entities"]}
    rows = ["| 文件 | 行数 | 列数 | 唯一标识列 |", "|---|---|---|---|"]
    files = {p.stem: p.name for p in (case_dir / "data").iterdir()}
    for name, (header, data) in _tables(case_dir / "data").items():
        shown = files[name.split("/")[0]] + (f" / {name.split('/', 1)[1]}" if "/" in name else "")
        rows.append(f"| `data/{shown}` | {len(data):,} | {len(header)} | {ids.get(name, '—')} |")
    rels = ["| 从 | 到 | 关联列 | 必需 |", "|---|---|---|---|"]
    for r in gold.get("relations", []):
        rels.append(f"| {r['from']} | {r['to']} | {'，'.join(f'{a} = {b}' for a, b in r['on'])} | {'是' if r.get('required', True) else '可选'} |")
    mets = ["| 实体 | 指标 | 口径 |", "|---|---|---|"]
    for m in gold.get("metrics", []):
        if m.get("required", True):
            mets.append(f"| {m['table']} | {m['label']} | {_formula(m)} |")
    qa = ["| 题号 | 问题 | 标准答案 |", "|---|---|---|"]
    for q in doc["questions"]:
        exp = "；".join("、".join(_cell(v) for v in row if v is not None) for row in q["expected"]["rows"])
        qa.append(f"| {q['id']} | {q['question']} | {exp} |")
    return {
        "tables": "\n".join(rows),
        "gold": f"实体 {len([e for e in gold['entities'] if e.get('kind') != 'exclude'])} 个（每张表一个），关系 {len(gold.get('relations', []))} 条：\n\n"
        + "\n".join(rels) + "\n\n必需指标：\n\n" + "\n".join(mets),
        "answers": "\n".join(qa),
    }


def _formula(m: dict) -> str:
    def part(x: dict) -> str:
        word = {"count": "计数", "sum": "合计", "avg": "平均", "min": "最小", "max": "最大", "count_distinct": "去重计数"}[x["aggregate"]]
        col = "" if x["aggregate"] == "count" else f"「{x.get('column')}」"
        cond = "，".join(f"{f['column']} {({'eq': '=', 'ne': '≠', 'gt': '>', 'gte': '≥', 'lt': '<', 'lte': '≤', 'in': '属于', 'not_in': '不属于', 'is_null': '为空' if f.get('value') else '非空'})[f['op']]}{'' if f['op'] == 'is_null' else ' ' + str(f.get('value'))}" for f in x.get("filters", []))
        return f"{col}{word}" + (f"（{cond}）" if cond else "")
    return f"{part(m['numerator'])} ÷ {part(m['denominator'])}" if m["aggregate"] == "ratio" else part(m)


def cmd_readme(case_dir: Path) -> int:
    """把 README.md 里 ``<!-- 自动生成:名称 -->`` 与 ``<!-- /自动生成 -->`` 之间的内容换成从数据算出的段落。"""

    path = case_dir / "README.md"
    text = path.read_text(encoding="utf-8")
    for name, body in _blocks(case_dir).items():
        text = re.sub(rf"(<!-- 自动生成:{name} -->).*?(<!-- /自动生成 -->)", lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text, flags=re.S)
    path.write_text(text, encoding="utf-8")
    print(f"更新 {path}")
    return 0


# ── 题型与题库冻结 ────────────────────────────────────────────────────

QTYPES = ("多表综合", "跨表关联", "比率", "排名", "时间筛选", "分组统计", "单表聚合")


def qtype(sql: str) -> str:
    """按 SQL 特征给题目定题型（确定性，取优先级最高的一类）。"""

    s = " ".join(sql.upper().split())
    joins = s.count(" JOIN ")
    if joins >= 2 or "EXISTS" in s:
        return "多表综合"
    if joins == 1:
        return "跨表关联"
    if re.search(r"\)\s*/|/\s*(SUM|COUNT)\(", s):
        return "比率"
    if " LIMIT " in s:
        return "排名"
    if re.search(r"'\d{4}-\d{2}", s):
        return "时间筛选"
    if "GROUP BY" in s:
        return "分组统计"
    return "单表聚合"


def cmd_classify(case_dir: Path) -> int:
    qpath = case_dir / "questions.yaml"
    doc = yaml.safe_load(qpath.read_text(encoding="utf-8"))
    for q in doc["questions"]:
        q["qtype"] = qtype(q["sql"])
    qpath.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    print(case_dir.name, " ".join(q["qtype"] for q in doc["questions"]))
    return 0


def cmd_bank(root: Path) -> int:
    """题库清单：每个案例 questions.yaml 的 sha256、题数与题型分布，写到 BANK.md。"""

    import hashlib
    from collections import Counter

    lines, total, types = [], 0, Counter()
    for case in sorted((root / "cases").iterdir()):
        raw = (case / "questions.yaml").read_bytes()
        qs = yaml.safe_load(raw)["questions"]
        total += len(qs)
        types.update(q.get("qtype", "?") for q in qs)
        lines.append(f"| {case.name} | {len(qs)} | `{hashlib.sha256(raw).hexdigest()}` |")
    body = "\n".join([
        "# 问答题库清单", "",
        f"共 {total} 题。题型（按 SQL 特征自动判定，见 tools/casekit.py qtype）：" + "、".join(f"{t} {types[t]}" for t in QTYPES if types[t]) + "。", "",
        "| 案例 | 题数 | questions.yaml 的 sha256 |", "|---|---|---|", *lines, "",
    ])
    (root / "BANK.md").write_text(body, encoding="utf-8")
    print(body)
    return 0


def main(argv: list[str]) -> int:
    cmd, case = argv[0], Path(argv[1])
    if cmd == "classify":
        return cmd_classify(case)
    if cmd == "bank":
        return cmd_bank(case)
    if cmd == "readme":
        return cmd_readme(case)
    if cmd == "answers":
        return cmd_answers(case, argv[2] if len(argv) > 2 else None)
    if cmd == "gold":
        return cmd_gold(case)
    if cmd == "gold-json":
        return cmd_gold_json(case, Path(argv[2]))
    if cmd == "grade":
        return cmd_grade(case, Path(argv[2]))
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
