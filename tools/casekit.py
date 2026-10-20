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
    """回答里有没有这个数：去掉千分位逗号；「122万」「1.2亿」按单位折算；百分数也按小数比一次。"""

    text = re.sub(r"(?<=\d)[,，](?=\d{3})", "", text)
    for token, unit in re.findall(r"(-?\d+(?:\.\d+)?)\s*(万|亿|%)?", text):
        number = float(token) * {"万": 1e4, "亿": 1e8, "%": 0.01}.get(unit, 1)
        if unit == "%" and abs(float(token) - value) <= max(tolerance * abs(value), 1e-9):
            return True
        if abs(number - value) <= max(tolerance * abs(value), 1e-9) or round(number, 2) == round(value, 2):
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


def main(argv: list[str]) -> int:
    cmd, case = argv[0], Path(argv[1])
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
