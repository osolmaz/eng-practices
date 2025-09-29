#!/usr/bin/env python3
"""
Merge the repository's code review Markdown files into a single document.

Simplified model:
- A static section list defines: (anchor id, candidate file paths, fixed heading shift).
- For each section, shift all ATX headings by the fixed integer (cap at ######).
- Ensure the first heading in each section has an explicit {#anchor} matching the section id.
- Rewrite links to other repo .md files to in-document anchors for those sections.
- Preserve code fences; do not alter content inside fenced blocks.

Usage:
  uv run scripts/merge_docs.py [--out combined.md] [--title "..."]
  python3 scripts/merge_docs.py [--out combined.md] [--title "..."]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


RE_HEADING = re.compile(r"^(?P<hash>#{1,6})\s+(?P<text>.*?)(?P<anchor>\s*\{#[-A-Za-z0-9_]+\})?\s*$")
RE_CODE_FENCE = re.compile(r"^\s*(```|~~~)")
RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def ensure_top_anchor_on_first_heading(lines: List[str], top_anchor: str) -> Tuple[List[str], bool]:
    """Ensure the first heading has an explicit {#anchor}. Returns (lines, added_flag)."""
    in_code = False
    out: List[str] = []
    added = False
    found_first = False
    for line in lines:
        if RE_CODE_FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if not in_code and not found_first:
            m = RE_HEADING.match(line)
            if m:
                level = len(m.group("hash"))
                text = m.group("text")
                anchor = m.group("anchor") or ""
                if not anchor:
                    anchor = f" {{#{top_anchor}}}"
                    added = True
                    out.append(f"{'#' * level} {text}{anchor}\n")
                else:
                    # If there is already a different anchor, insert an HTML anchor line above
                    if top_anchor not in anchor:
                        out.append(f"<a id=\"{top_anchor}\"></a>\n")
                        added = True
                    out.append(line)
                found_first = True
                continue
        out.append(line)
    return out, added


def shift_headings(lines: List[str], shift: int) -> List[str]:
    if shift <= 0:
        return lines
    out: List[str] = []
    in_code = False
    for line in lines:
        if RE_CODE_FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        m = RE_HEADING.match(line)
        if not m:
            out.append(line)
            continue
        level = len(m.group("hash"))
        new_level = min(level + shift, 6)
        text = m.group("text")
        anchor = m.group("anchor") or ""
        out.append(f"{'#' * new_level} {text}{anchor}\n")
    return out


def build_abs_map(chosen: Dict[str, Tuple[Path, str, int]]) -> Dict[Path, str]:
    abs_map: Dict[Path, str] = {}
    for _anchor, (path, anchor, _shift) in chosen.items():
        abs_map[path.resolve()] = anchor
    return abs_map


def rewrite_links(lines: List[str], current_file: Path, abs_anchor_map: Dict[Path, str]) -> List[str]:
    out: List[str] = []
    in_code = False

    def repl(match: re.Match) -> str:
        text = match.group(1)
        target = match.group(2).strip()
        # Skip external links, mailto, and in-page anchors
        if target.startswith("#") or "://" in target or target.startswith("mailto:"):
            return match.group(0)

        # Separate fragment if present
        base, frag = (target.split("#", 1) + [None])[:2] if "#" in target else (target, None)

        # Only rewrite .md links
        if not base.endswith(".md"):
            return match.group(0)

        # Resolve path against current file's directory
        try:
            resolved = (current_file.parent / base).resolve()
        except Exception:
            return match.group(0)

        if resolved in abs_anchor_map:
            if frag:
                return f"[{text}](#{frag})"
            return f"[{text}](#{abs_anchor_map[resolved]})"
        return match.group(0)

    for line in lines:
        if RE_CODE_FENCE.match(line):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue
        out.append(RE_LINK.sub(repl, line))
    return out


def process_file(path: Path, top_anchor: str, fixed_shift: int = 0) -> List[str]:
    text = read_text(path)
    lines = text.splitlines(keepends=True)
    lines = shift_headings(lines, fixed_shift)
    lines, _ = ensure_top_anchor_on_first_heading(lines, top_anchor)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="combined.md", help="Output Markdown file path")
    parser.add_argument("--title", default="Google's Code Review Guidelines", help="Top-level document title (H1)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]

    # Section list: (anchor id, candidate files in priority order, fixed heading shift)
    sections: List[Tuple[str, List[str], int]] = [
        ("overview", ["review/index.md"], 0),
        # Reviewer guide first — keep index as H1 (shift 0), subpages as H2 (shift +1)
        ("reviewer-index", ["review/reviewer/index.md"], 0),
        ("standard-of-code-review", ["review/reviewer/standard.md"], 1),
        ("what-to-look-for", ["review/reviewer/looking-for.md", "review/reviewer/what-to-look-for.md"], 1),
        ("navigating-a-pr", ["review/reviewer/navigate.md", "review/reviewer/navigating-a-pr.md"], 1),
        ("speed-of-reviews", ["review/reviewer/speed.md", "review/reviewer/speed-of-reviews.md"], 1),
        ("writing-review-comments", ["review/reviewer/comments.md", "review/reviewer/writing-review-comments.md"], 1),
        ("handling-pushback", ["review/reviewer/pushback.md"], 1),
        # Author guide — make H2 sections (shift +1)
        ("pr-author-index", ["review/developer/index.md"], 1),
        ("pr-descriptions", ["review/developer/pr-descriptions.md", "review/developer/cl-descriptions.md"], 1),
        ("small-prs", ["review/developer/small-prs.md", "review/developer/small-cls.md"], 1),
        ("handling-review-feedback", ["review/developer/handling-comments.md", "review/developer/handling-review-feedback.md"], 1),
        # Policy — H2
        ("emergencies", ["review/emergencies.md", "docs/policy/emergencies-hotfixes.md"], 1),
    ]

    # Resolve actual files to use and their top anchors
    chosen: Dict[str, Tuple[Path, str, int]] = {}
    files_in_order: List[Path] = []
    for anchor, candidates, shift in sections:
        found: Path | None = None
        for rel in candidates:
            p = (root / rel)
            if p.exists():
                found = p
                break
        if not found:
            raise FileNotFoundError(f"Missing expected file (any of): {', '.join(candidates)}")
        chosen[anchor] = (found, anchor, shift)
        files_in_order.append(found)

    abs_anchor_map = build_abs_map(chosen)

    merged: List[str] = []
    # Document title
    merged.append(f"# {args.title} (GitHub Adaptation)\n\n")
    # Optional editor's note right after the title
    editors_note = root / "EDITORS_NOTE.md"
    if editors_note.exists():
        try:
            note = editors_note.read_text(encoding="utf-8")
        except Exception:
            note = ""
        if note:
            # Include as-is, followed by a blank line
            merged.append(note)
            if not note.endswith("\n"):
                merged.append("\n")
            merged.append("\n")

    for i, src in enumerate(files_in_order):
        # Resolve section details
        entry = next((e for e in chosen.values() if e[0].resolve() == src.resolve()), None)
        assert entry is not None
        _path, top_anchor, fixed_shift = entry
        # Process file with fixed heading shift and top anchor
        lines = process_file(src, top_anchor, fixed_shift=fixed_shift)
        # Rewrite links for this file
        lines = rewrite_links(lines, src.resolve(), abs_anchor_map)
        # Separator between files
        if i > 0:
            merged.append("\n---\n\n")
        merged.extend(lines)

    out_path = (root / args.out)
    out_path.write_text("".join(merged), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
