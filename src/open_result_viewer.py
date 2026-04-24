from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    result_path = project_root / "results" / "3d_cantilever_result.vtu"

    try:
        from .viewer import open_saved_result
    except ImportError as exc:
        print(exc)
        return 1

    if not result_path.exists():
        print("결과 파일이 없습니다. 먼저 02_run_analysis.bat을 실행하세요.")
        return 1

    open_saved_result(result_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
