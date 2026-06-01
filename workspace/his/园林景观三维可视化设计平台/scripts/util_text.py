# -*- coding: utf-8 -*-
from __future__ import annotations


def wrap_lines(text: str, width: int = 80) -> list[str]:
    out: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.rstrip("\n")
        while len(line) > width:
            cut = line.rfind(" ", 0, width + 1)
            if cut <= 0:
                cut = width
            out.append(line[:cut].rstrip())
            line = line[cut:].lstrip()
        out.append(line)
    return out


def normalize_ws(text: str) -> str:
    return " ".join((text or "").split())


def clamp(n: int, *, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(n)))


def is_blank(text: str | None) -> bool:
    return not (text or "").strip()


def title_case(text: str) -> str:
    return " ".join(w[:1].upper() + w[1:] for w in normalize_ws(text).split(" ") if w)
