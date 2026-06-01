# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
from pathlib import Path


def normalize_utf8(path: Path) -> tuple[bool, str]:
    raw = path.read_bytes()
    had_bom = raw.startswith(b"\xef\xbb\xbf")
    text = path.read_text(encoding="utf-8-sig", errors="strict")
    had_replacement = "\ufffd" in text
    path.write_text(text, encoding="utf-8", newline="\n")
    changed = had_bom
    issues = []
    if had_bom:
        issues.append("bom_removed")
    if had_replacement:
        issues.append("replacement_char_found")
    return changed, ",".join(issues) if issues else "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description="UTF-8 preflight guard")
    parser.add_argument("--paths", nargs="+", required=True)
    args = parser.parse_args()

    failed = []
    for p in args.paths:
        path = Path(p).resolve()
        if not path.exists():
            failed.append(f"missing:{path}")
            continue
        try:
            _, status = normalize_utf8(path)
            print(f"[encoding_guard] PASS {path} status={status}")
            if "replacement_char_found" in status:
                failed.append(f"replacement_char_found:{path}")
        except UnicodeDecodeError:
            failed.append(f"decode_error:{path}")
        except Exception as exc:
            failed.append(f"error:{path}:{exc}")

    if failed:
        for item in failed:
            print(f"[encoding_guard] FAIL {item}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
