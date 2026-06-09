#!/usr/bin/env python3
"""Check common PPTX package issues that can trigger repair prompts."""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile


REL_RE = re.compile(r"<Relationship\b[^>]*/>", re.DOTALL)
ATTR_RE = re.compile(r'\b([A-Za-z_:][\w:.-]*)="([^"]*)"')


def attrs(element: str) -> dict[str, str]:
    return {key: value for key, value in ATTR_RE.findall(element)}


def rels_base(rels_path: str) -> str:
    parts = rels_path.split("/")
    if parts == ["_rels", ".rels"]:
        return ""
    if len(parts) >= 2 and parts[-2] == "_rels":
        return "/".join(parts[:-2])
    return posixpath.dirname(rels_path)


def resolve_target(rels_path: str, target: str) -> str:
    base = rels_base(rels_path)
    if target.startswith("/"):
        return posixpath.normpath(target.lstrip("/"))
    return posixpath.normpath(posixpath.join(base, target)) if base else posixpath.normpath(target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check PPTX package compatibility.")
    parser.add_argument("pptx", type=Path)
    args = parser.parse_args()

    pptx_path = args.pptx.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    with ZipFile(pptx_path, "r") as zf:
        names = set(zf.namelist())

        required = {"[Content_Types].xml", "_rels/.rels", "ppt/presentation.xml"}
        for name in sorted(required - names):
            errors.append(f"Missing required part: {name}")

        for name in sorted(n for n in names if n.endswith(".xml") or n.endswith(".rels")):
            data = zf.read(name)
            if data.startswith(b"\xef\xbb\xbf"):
                warnings.append(f"XML has UTF-8 BOM: {name}")
            try:
                ET.fromstring(data)
            except ET.ParseError as exc:
                errors.append(f"Invalid XML: {name}: {exc}")

        if "[Content_Types].xml" in names:
            root = ET.fromstring(zf.read("[Content_Types].xml"))
            for override in root.findall("{http://schemas.openxmlformats.org/package/2006/content-types}Override"):
                part = (override.get("PartName") or "").lstrip("/")
                if part and part not in names:
                    errors.append(f"Content_Types override points to missing part: {part}")

        for rels in sorted(n for n in names if n.endswith(".rels")):
            text = zf.read(rels).decode("utf-8", errors="replace")
            for match in REL_RE.finditer(text):
                rel = attrs(match.group(0))
                target = rel.get("Target")
                if not target or rel.get("TargetMode") == "External":
                    continue
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target.startswith("/"):
                    warnings.append(f"Absolute internal relationship target: {rels} -> {target}")
                resolved = resolve_target(rels, target)
                if resolved not in names:
                    errors.append(f"Dangling relationship target: {rels} -> {resolved}")

        for rels in sorted(n for n in names if n.startswith("ppt/slides/_rels/slide") and n.endswith(".xml.rels")):
            text = zf.read(rels).decode("utf-8", errors="replace")
            first = REL_RE.search(text)
            if first and "slideLayout" not in first.group(0):
                warnings.append(f"Slide layout relationship is not first: {rels}")

    for item in errors:
        print(f"ERROR: {item}", file=sys.stderr)
    for item in warnings:
        print(f"WARN: {item}", file=sys.stderr)

    if errors:
        return 1
    print(f"PPTX package check passed: {pptx_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
