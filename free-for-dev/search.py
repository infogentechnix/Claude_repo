#!/usr/bin/env python3
"""Search the vendored free-for.dev list of free-tier developer services.

Examples:
    python3 free-for-dev/search.py postgres
    python3 free-for-dev/search.py email api --limit 5
    python3 free-for-dev/search.py --section "web hosting"
    python3 free-for-dev/search.py --sections
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

README = Path(__file__).resolve().parent / "README.md"
ENTRY_RE = re.compile(r"^\s*\*\s+\[(?P<name>[^\]]+)\]\((?P<url>[^)\s]+)\)\s*[-–—:]?\s*(?P<desc>.*)$")
CONTINUATION_RE = re.compile(r"^\s{4,}\*\s+(?P<text>.*)$")
SKIPPED_SECTIONS = {"Table of Contents"}


@dataclass(frozen=True)
class Entry:
    section: str
    name: str
    url: str
    description: str

    def haystack(self) -> str:
        return f"{self.section} {self.name} {self.url} {self.description}".lower()


def parse(text: str) -> list[Entry]:
    """Turn the README Markdown into entries, one per top-level service bullet."""
    entries: list[Entry] = []
    section: str | None = None
    parent = ""  # name of the latest top-level bullet, linked or not
    for line in text.splitlines():
        heading = re.match(r"^#{1,2}\s+(.*)$", line)
        if heading:
            title = heading.group(1).strip()
            section = None if title in SKIPPED_SECTIONS or line.startswith("# ") else title
            parent = ""
            continue
        if section is None:
            continue
        m = ENTRY_RE.match(line)
        nested = CONTINUATION_RE.match(line)
        if m:
            name = m.group("name").strip()
            if nested and parent:
                name = f"{parent} › {name}"
            else:
                parent = name
            entries.append(Entry(section, name, m.group("url"), m.group("desc").strip()))
        elif nested and entries and entries[-1].section == section:
            last = entries[-1]
            entries[-1] = Entry(last.section, last.name, last.url, f"{last.description} {nested.group('text')}".strip())
        else:
            plain = re.match(r"^\s{0,3}\*\s+(.+)$", line)
            if plain:
                parent = plain.group(1).strip()
    return entries


def search(entries: list[Entry], terms: list[str], section: str | None = None) -> list[Entry]:
    """Entries containing every term (case-insensitive), optionally within a section."""
    needles = [t.lower() for t in terms]
    sec = section.lower() if section else None
    return [
        e for e in entries
        if (sec is None or sec in e.section.lower()) and all(n in e.haystack() for n in needles)
    ]


def sections(entries: list[Entry]) -> list[tuple[str, int]]:
    counts = Counter(e.section for e in entries)
    return [(s, counts[s]) for s in dict.fromkeys(e.section for e in entries)]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("terms", nargs="*", help="keywords; every one must match")
    p.add_argument("-s", "--section", help="only sections whose name contains this")
    p.add_argument("-n", "--limit", type=int, default=25, help="max results (0 = all)")
    p.add_argument("--sections", action="store_true", help="list sections and entry counts")
    args = p.parse_args(argv)

    if not README.exists():
        sys.stderr.write(f"missing {README}; run free-for-dev/update.sh\n")
        return 2
    entries = parse(README.read_text(encoding="utf-8"))

    if args.sections:
        for name, count in sections(entries):
            sys.stdout.write(f"{count:4d}  {name}\n")
        return 0
    if not args.terms and not args.section:
        p.error("give search terms, --section, or --sections")

    hits = search(entries, args.terms, args.section)
    shown = hits if args.limit <= 0 else hits[: args.limit]
    for e in shown:
        sys.stdout.write(f"[{e.section}] {e.name} <{e.url}>\n    {e.description}\n")
    sys.stdout.write(f"-- {len(shown)} of {len(hits)} matches\n")
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
