#!/usr/bin/env python3
"""
Embed Python rule sources into the package README.md.

Usage:
    python embed_rules_into_readme.py \
        --rules-dir ../motor_tributario_py/rules \
        --readme ../README.md

The script will back up the README to `README.md.bak` and then insert
or replace the section between the markers:

<!-- RULES-START -->
...generated content...
<!-- RULES-END -->

If no markers are present the script appends the generated section at the end.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import Optional


START_MARKER = "<!-- RULES-START -->"
END_MARKER = "<!-- RULES-END -->"


def extract_docstring(source: str) -> Optional[str]:
    try:
        module = ast.parse(source)
        doc = ast.get_docstring(module)
        return doc
    except Exception:
        return None


def extract_top_comment(source: str) -> Optional[str]:
    lines = source.splitlines()
    comment_lines = []
    # Skip shebang and encoding lines
    i = 0
    while i < len(lines) and lines[i].startswith("#!"):
        i += 1
    while i < len(lines) and lines[i].strip().startswith("#"):
        comment_lines.append(lines[i].lstrip("# "))
        i += 1
    return "\n".join(comment_lines).strip() if comment_lines else None


def collect_rules(rules_dir: Path):
    md_parts = []
    md_parts.append("## Embedded rule sources")
    files = sorted([p for p in rules_dir.iterdir() if p.suffix == ".py" and p.name != "__init__.py"])
    for p in files:
        src = p.read_text(encoding="utf-8")
        doc = extract_docstring(src) or extract_top_comment(src) or "(no docstring)"

        # Try to parse a top-level dict assignment that looks like a DMN rule
        rules = []
        try:
            module = ast.parse(src)
            for node in module.body:
                if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Dict,)):
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        continue
                    # Heuristic: dicts that contain 'title' and 'inputs'/'outputs'
                    if isinstance(value, dict) and ('title' in value and 'inputs' in value and 'outputs' in value):
                        rules.append(value)
        except Exception:
            rules = []

        md_parts.append(f"### {p.name}")

        # Prefer rule titles as the Summary when rule dicts are found
        if rules:
            titles = [r.get('title') or r.get('name') or p.name for r in rules]
            summary_doc = "; ".join(titles)
        else:
            summary_doc = doc

        md_parts.append(f"**Summary:** {summary_doc}")
        md_parts.append("")
        md_parts.append(f"Source file: {p}")
        md_parts.append("")

        if not rules:
            md_parts.append("_(no DMN-style rule dict found in file)_")
            md_parts.append("")
            continue

        for rule in rules:
            title = rule.get('title') or rule.get('name') or p.name
            hit_policy = rule.get('hit_policy', '')
            # Separate blocks with a blank line
            md_parts.append("")
            md_parts.append(f"**Rule:** {title}")
            if hit_policy:
                md_parts.append(f"**Hit policy:** {hit_policy}")

            # Inputs and outputs
            inputs = rule.get('inputs', {})
            outputs = rule.get('outputs', {})
            in_cols = [c.get('id') if isinstance(c, dict) else str(c) for c in inputs.get('cols', [])]
            out_cols = [c.get('id') if isinstance(c, dict) else str(c) for c in outputs.get('cols', [])]

            # Build header
            headers = []
            headers.extend([f"Input: {h}" for h in in_cols])
            headers.extend([f"Output: {h}" for h in out_cols])

            # Rows
            in_rows = inputs.get('rows', []) or []
            out_rows = outputs.get('rows', []) or []
            max_rows = max(len(in_rows), len(out_rows)) if max(len(in_rows), len(out_rows)) > 0 else 0

            # Render a markdown table
            if headers:
                # blank line before table for readability
                md_parts.append("")
                md_parts.append('|' + '|'.join(headers) + '|')
                md_parts.append('|' + '|'.join(['---' for _ in headers]) + '|')

                for i in range(max_rows):
                    in_cells = []
                    out_cells = []
                    if i < len(in_rows):
                        row = in_rows[i]
                        # ensure row is a list
                        if not isinstance(row, (list, tuple)):
                            row = [row]
                        in_cells = [str(c) for c in row]
                    else:
                        in_cells = ['' for _ in in_cols]

                    if i < len(out_rows):
                        row = out_rows[i]
                        if not isinstance(row, (list, tuple)):
                            row = [row]
                        out_cells = [str(c) for c in row]
                    else:
                        out_cells = ['' for _ in out_cols]

                    # Normalize lengths
                    while len(in_cells) < len(in_cols):
                        in_cells.append('')
                    while len(out_cells) < len(out_cols):
                        out_cells.append('')

                    md_parts.append('|' + '|'.join(in_cells + out_cells) + '|')

                # spacer after table
                md_parts.append("")

            # Small spacer between multiple rules in the same file
            md_parts.append('\n')

    return "\n".join(md_parts)


def replace_between_markers(readme_text: str, generated: str) -> str:
    if START_MARKER in readme_text and END_MARKER in readme_text:
        before, rest = readme_text.split(START_MARKER, 1)
        _, after = rest.split(END_MARKER, 1)
        return before + START_MARKER + "\n\n" + generated + "\n" + END_MARKER + after
    else:
        # Append markers and generated content
        return readme_text.rstrip() + "\n\n" + START_MARKER + "\n\n" + generated + "\n" + END_MARKER + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules-dir", required=True, help="Path to the rules directory")
    parser.add_argument("--readme", required=True, help="Path to README.md to update")
    parser.add_argument("--backup", default=None, help="Backup path for README (default: README.md.bak)")
    args = parser.parse_args()

    rules_dir = Path(args.rules_dir).resolve()
    readme_path = Path(args.readme).resolve()

    if not rules_dir.exists() or not rules_dir.is_dir():
        print(f"Rules directory not found: {rules_dir}")
        return 2
    if not readme_path.exists():
        print(f"README not found: {readme_path}")
        return 2

    generated = collect_rules(rules_dir)

    backup_path = Path(args.backup) if args.backup else readme_path.with_suffix(readme_path.suffix + ".bak")
    readme_text = readme_path.read_text(encoding="utf-8")
    backup_path.write_text(readme_text, encoding="utf-8")
    new_text = replace_between_markers(readme_text, generated)
    readme_path.write_text(new_text, encoding="utf-8")
    print(f"Updated {readme_path} (backup: {backup_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
