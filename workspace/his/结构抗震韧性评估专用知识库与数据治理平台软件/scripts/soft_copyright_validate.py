# -*- coding: utf-8 -*-
"""
Strict validator for software copyright (软著) materials.

Design goals:
- No third-party dependencies (stdlib only).
- Fail-fast with clear reasons and file pointers.
- Enforce the full rule set derived from the user's provided text:
  - triple consistency (name/version/modules/features)
  - document anti-template / anti-hallucination checks
  - sensitive info leakage checks
  - "feature described must be locatable in code" checks (string-based)

Usage:
  python -X utf8 .\\workspace\\scripts\\soft_copyright_validate.py --project-root E:\\copyRight\\workspace --name 项目名 --code-root E:\\copyRight\\workspace\\some_project

Notes:
- This script does not attempt to compute "similarity percentage" (no official algorithm).
- "Locatable in code" is enforced by requiring explicit evidence markers in docs
  and verifying that those markers appear in the codebase text.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class Finding:
    level: str  # "ERROR" | "WARN"
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None


NAME_VERSION_RE = re.compile(r"(?P<name>.+?)(?P<version>V\d+(?:\.\d+)*)")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _iter_files(root: Path, exts: Sequence[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def _find_first(pattern: re.Pattern[str], text: str) -> Optional[re.Match[str]]:
    return pattern.search(text)


def _line_no(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _extract_softname_version(doc_text: str) -> Tuple[Optional[str], Optional[str]]:
    m = _find_first(NAME_VERSION_RE, doc_text)
    if not m:
        return None, None
    name = m.group("name").strip()
    version = m.group("version").strip()
    # Normalize common separators
    name = re.sub(r"[\u3000 \t]+$", "", name)
    return name, version


def _detect_sensitive_markers(text: str) -> List[str]:
    hits: List[str] = []
    patterns = [
        r"https?://",
        r"\bwww\.",
        r"\b(?:C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z):\\",
        r"\\Users\\",
        r"\b(author|created\s*at|updated\s*at|timestamp)\b",
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    ]
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append(pat)
    return hits


def _detect_template_talk(text: str) -> List[str]:
    # Strongly discouraged phrases per rule set.
    phrases = [
        "界面简洁",
        "操作简单",
        "功能强大",
        "性能优越",
        "首先",
        "其次",
        "最后",
        "综上所述",
        "总而言之",
        "易用",
        "先进",
        "高效",
    ]
    hits = []
    for ph in phrases:
        if ph in text:
            hits.append(ph)
    return hits


EVIDENCE_RE = re.compile(
    r"(?:代码定位证据|代码位置|对应代码|实现位置)[:：]\s*(?P<evidence>.+)",
    flags=re.IGNORECASE,
)


def _extract_evidence_lines(text: str) -> List[Tuple[int, str]]:
    out: List[Tuple[int, str]] = []
    for m in EVIDENCE_RE.finditer(text):
        ln = _line_no(text, m.start())
        ev = m.group("evidence").strip()
        # Trim trailing punctuation / markdown
        ev = ev.strip("` \t")
        out.append((ln, ev))
    return out


def _evidence_tokens(evidence: str) -> List[str]:
    # Evidence may contain: paths, symbols, routes, endpoints, filenames.
    # Split by common separators while keeping tokens that can be searched in code.
    raw = re.split(r"[，,;；\s]+", evidence)
    tokens: List[str] = []
    for t in raw:
        t = t.strip()
        if not t:
            continue
        # Drop very short noise tokens.
        if len(t) < 3:
            continue
        tokens.append(t)
    # Deduplicate while keeping order
    seen = set()
    uniq: List[str] = []
    for t in tokens:
        if t in seen:
            continue
        seen.add(t)
        uniq.append(t)
    return uniq


def _search_tokens_in_code(code_root: Path, tokens: Sequence[str]) -> List[str]:
    # Search tokens in common text code/config files. Ignore node_modules/dist/build outputs.
    exts = {
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".vue",
        ".py",
        ".java",
        ".go",
        ".cs",
        ".rb",
        ".php",
        ".rs",
        ".kt",
        ".kts",
        ".json",
        ".yml",
        ".yaml",
        ".toml",
        ".xml",
        ".md",
        ".sql",
        ".env",
        ".ini",
        ".properties",
    }
    deny_dirs = {"node_modules", "dist", "build", "out", ".next", ".nuxt", "target", ".git"}

    def is_denied(p: Path) -> bool:
        parts = set(p.parts)
        return any(d in parts for d in deny_dirs)

    cache: List[Tuple[Path, str]] = []
    for p in _iter_files(code_root, tuple(exts)):
        if is_denied(p):
            continue
        try:
            cache.append((p, _read_text(p)))
        except OSError:
            continue

    missing: List[str] = []
    for tok in tokens:
        found = False
        for _, txt in cache:
            if tok in txt:
                found = True
                break
        if not found:
            missing.append(tok)
    return missing


def validate(
    materials_root: Path,
    a_name: str,
    code_root: Path,
    require_docx_pdf: bool,
) -> List[Finding]:
    findings: List[Finding] = []

    a_dir = materials_root / a_name
    if not a_dir.exists():
        return [Finding("ERROR", f"Materials directory not found: {a_dir}")]

    manual_md = a_dir / f"{a_name}操作手册.md"
    code_md = a_dir / f"{a_name}源代码文档.md"
    form_md = a_dir / "软件著作权登记申请表.md"

    required = [manual_md, code_md, form_md]
    for p in required:
        if not p.exists():
            findings.append(Finding("ERROR", f"Missing required file: {p}", p))

    if require_docx_pdf:
        docx_pdf = [
            a_dir / f"{a_name}操作手册.docx",
            a_dir / f"{a_name}操作手册.pdf",
            a_dir / f"{a_name}源代码文档.docx",
            a_dir / f"{a_name}源代码文档.pdf",
            a_dir / "软件著作权登记申请表.docx",
        ]
        for p in docx_pdf:
            if not p.exists():
                findings.append(Finding("ERROR", f"Missing required file: {p}", p))
        img_dir = a_dir / "images"
        if not img_dir.exists() or not any(img_dir.iterdir()):
            findings.append(Finding("ERROR", f"Missing or empty images directory: {img_dir}", img_dir))

    if any(f.level == "ERROR" and f.message.startswith("Missing required file") for f in findings):
        return findings

    manual_txt = _read_text(manual_md)
    code_txt = _read_text(code_md)
    form_txt = _read_text(form_md)

    # 1) Triple consistency: name + version
    m_name, m_ver = _extract_softname_version(manual_txt)
    c_name, c_ver = _extract_softname_version(code_txt)
    f_name, f_ver = _extract_softname_version(form_txt)

    # We accept that extraction may be imperfect; but then it must be explicitly provided.
    if not (m_name and m_ver):
        findings.append(Finding("ERROR", "Cannot extract 软件名称/版本号 from 操作手册.md (expect '软件全称 V1.0' somewhere).", manual_md))
    if not (c_name and c_ver):
        findings.append(Finding("ERROR", "Cannot extract 软件名称/版本号 from 源代码文档.md (expect '软件全称 V1.0' somewhere).", code_md))
    if not (f_name and f_ver):
        findings.append(Finding("ERROR", "Cannot extract 软件名称/版本号 from 申请表.md (expect '软件全称 V1.0' somewhere).", form_md))

    if m_ver and not m_ver.startswith("V"):
        findings.append(Finding("ERROR", f"Version in 操作手册.md must start with 'V': got {m_ver!r}", manual_md))
    if c_ver and not c_ver.startswith("V"):
        findings.append(Finding("ERROR", f"Version in 源代码文档.md must start with 'V': got {c_ver!r}", code_md))
    if f_ver and not f_ver.startswith("V"):
        findings.append(Finding("ERROR", f"Version in 申请表.md must start with 'V': got {f_ver!r}", form_md))

    if m_name and c_name and f_name:
        if not (m_name == c_name == f_name):
            findings.append(
                Finding(
                    "ERROR",
                    f"软件名称不一致: 手册={m_name!r}, 源码文档={c_name!r}, 申请表={f_name!r}",
                )
            )
    if m_ver and c_ver and f_ver:
        if not (m_ver == c_ver == f_ver):
            findings.append(
                Finding(
                    "ERROR",
                    f"版本号不一致: 手册={m_ver!r}, 源码文档={c_ver!r}, 申请表={f_ver!r}",
                )
            )

    # 2) Sensitive info leakage checks
    for p, txt in [(manual_md, manual_txt), (code_md, code_txt), (form_md, form_txt)]:
        hits = _detect_sensitive_markers(txt)
        if hits:
            findings.append(Finding("ERROR", f"Sensitive marker(s) detected: {', '.join(hits)}", p))

    # 3) Anti-template / AI-ish talk checks
    for p, txt in [(manual_md, manual_txt), (form_md, form_txt)]:
        hits = _detect_template_talk(txt)
        # Strict by default: treat as ERROR, but allow user to demote via flag in future.
        if hits:
            findings.append(Finding("ERROR", f"Template/AI-ish phrases detected: {', '.join(hits)}", p))

    # 4) Evidence-required checks (anti-hallucination + code correspondence)
    evidence_lines = _extract_evidence_lines(manual_txt)
    if not evidence_lines:
        findings.append(
            Finding(
                "ERROR",
                "操作手册.md missing evidence markers. Add lines like '代码定位证据：<path> <symbol> <route>' for each feature section.",
                manual_md,
            )
        )
        return findings

    # Tokenize evidence and verify tokens appear in codebase.
    all_missing: List[Tuple[int, str, str]] = []
    for ln, ev in evidence_lines:
        toks = _evidence_tokens(ev)
        if not toks:
            findings.append(Finding("ERROR", "Empty/invalid evidence line after '代码定位证据：...'", manual_md, ln))
            continue
        missing = _search_tokens_in_code(code_root, toks)
        for tok in missing:
            all_missing.append((ln, ev, tok))

    if all_missing:
        sample = all_missing[:20]
        for ln, ev, tok in sample:
            findings.append(
                Finding(
                    "ERROR",
                    f"Evidence token not found in codebase: token={tok!r}; evidence_line={ev!r}",
                    manual_md,
                    ln,
                )
            )
        if len(all_missing) > len(sample):
            findings.append(Finding("ERROR", f"... and {len(all_missing) - len(sample)} more missing evidence tokens.", manual_md))

    return findings


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True, help="Root folder that contains the {A}/ materials directory.")
    ap.add_argument("--name", required=True, help="需求名称 {A} (also materials subdirectory name).")
    ap.add_argument("--code-root", required=True, help="Codebase root used for 'locatable in code' checks.")
    ap.add_argument("--require-docx-pdf", action="store_true", help="Also require docx/pdf and images/ existence.")
    ns = ap.parse_args(argv)

    materials_root = Path(ns.project_root)
    a_name = ns.name
    code_root = Path(ns.code_root)
    require_docx_pdf = bool(ns.require_docx_pdf)

    findings = validate(materials_root, a_name, code_root, require_docx_pdf)
    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]

    def fmt(f: Finding) -> str:
        loc = ""
        if f.file:
            loc = str(f.file)
            if f.line:
                loc += f":{f.line}"
            loc += ": "
        return f"[{f.level}] {loc}{f.message}"

    for f in findings:
        print(fmt(f))

    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warns)} warning(s)")
        return 2
    print(f"PASS: {len(warns)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

