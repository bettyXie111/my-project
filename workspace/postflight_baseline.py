# -*- coding: utf-8 -*-
from __future__ import annotations

import runpy
from pathlib import Path


def main() -> int:
    script = Path(__file__).resolve().parent / "shared" / "scripts" / "postflight_baseline.py"
    namespace = runpy.run_path(str(script))
    return int(namespace["main"]())


if __name__ == "__main__":
    raise SystemExit(main())
