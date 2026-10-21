"""casekit 判分的自检：python3 -I tools/test_casekit.py（在仓库根目录运行）。

正向：每题的标准答案原样作为回答，必须判对；阴性：判对条件里含非零数字的题，把标准答案里的数字放大 10%，必须判错。
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from casekit import _number_in, grade_one  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    bad = []
    for case in sorted((ROOT / "cases").iterdir()):
        for q in yaml.safe_load((case / "questions.yaml").read_text(encoding="utf-8"))["questions"]:
            rows = q["expected"]["rows"]
            if not grade_one(q, "；".join("、".join(str(v) for v in r) for r in rows))[0]:
                bad.append(f"正向判错 {case.name} {q['id']}")
            items = q.get("must_include")
            items = [v for r in rows for v in r] if items is None else [x for i in items for x in (i if isinstance(i, list) else [i])]
            nums = [v for v in items if isinstance(v, (int, float)) and not isinstance(v, bool) and v != 0]
            if nums:  # 判对条件里有数字的题，才做「改错数字必须判错」的阴性对照
                wrong = "；".join("、".join(str(round(v * 1.1, 4)) if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v) for v in r) for r in rows)
                if grade_one(q, wrong)[0]:
                    bad.append(f"阴性判对 {case.name} {q['id']}")
    assert _number_in(0.0392, "3.9%", 0.005) and not _number_in(0.0392, "约 4%", 0.005)
    assert _number_in(63791994.84, "6379.2万", 0.005) and not _number_in(0.0392, "0.04", 0.005)
    # 标准答案按百分点给（41.24），回答写成「41.24%」也算对；小于 1 的期望值不放宽，免得 0.5 与「0.5%」互相冒认
    assert _number_in(41.24, "41.24%", 0.005) and _number_in(19.95, "占 20.0%", 0.005)
    assert not _number_in(0.5, "0.5%", 0.005) and not _number_in(41.24, "42.5%", 0.005)
    print("\n".join(bad) or "判分自检通过")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
