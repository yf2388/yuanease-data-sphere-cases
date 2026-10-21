"""casekit 判分的自检：python3 -I tools/test_casekit.py（在仓库根目录运行）。

正向：每题的标准答案原样作为回答，必须判对；阴性：把标准答案里的非零数字放大 10%，必须判错。
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
            nums = [v for r in rows for v in r if isinstance(v, (int, float)) and not isinstance(v, bool) and v != 0]
            if nums:
                wrong = "；".join("、".join(str(round(v * 1.1, 4)) if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v) for v in r) for r in rows)
                if grade_one(q, wrong)[0]:
                    bad.append(f"阴性判对 {case.name} {q['id']}")
    assert _number_in(0.0392, "3.9%", 0.005) and not _number_in(0.0392, "约 4%", 0.005)
    assert _number_in(63791994.84, "6379.2万", 0.005) and not _number_in(0.0392, "0.04", 0.005)
    print("\n".join(bad) or "判分自检通过")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
