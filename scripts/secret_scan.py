#!/usr/bin/env python3
"""Scanner local e sem dependências para credenciais acidentalmente versionadas."""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    "",
    ".c",
    ".cpp",
    ".css",
    ".csv",
    ".env",
    ".h",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
ALLOW_MARKER = "pragma: allow-secret"


@dataclass(frozen=True, slots=True)
class Finding:
    path: Path
    line: int
    rule: str


RULES = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github-token": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,255}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    "assigned-secret": re.compile(
        r"(?i)\b(?:api[_-]?key|password|passwd|secret|token)\b\s*[:=]\s*"
        r'''["'](?!(?:|example|placeholder|redacted|unset)["'])[^"']{8,}["']'''
    ),
}


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if ALLOW_MARKER in line:
            continue
        for name, pattern in RULES.items():
            if pattern.search(line):
                findings.append(Finding(path=path, line=line_number, rule=name))
    return findings


def git_paths() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item.decode() for item in completed.stdout.split(b"\0") if item]


def scan_paths(paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(scan_text(path.relative_to(ROOT), text))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracked", action="store_true", help="scan Git files")
    args = parser.parse_args()
    paths = git_paths() if args.tracked else git_paths()
    findings = scan_paths(paths)
    for finding in findings:
        print(f"{finding.path}:{finding.line}: possível segredo ({finding.rule})")
    if findings:
        print(f"[secrets] reprovado: {len(findings)} ocorrência(s)")
        return 1
    print("[secrets] aprovado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
