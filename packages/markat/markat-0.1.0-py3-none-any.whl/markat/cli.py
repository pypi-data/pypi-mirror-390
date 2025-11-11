"""CLI utility for slicing Markdown sections by hierarchical index."""

from __future__ import annotations

import argparse
import importlib.metadata
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional

from . import __version__

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
DEFAULT_BASE_LEVEL = 2
COLOR_CODES = {
    "label": "1;35",
    "path": "1;33",
    "breadcrumb": "1;36",
    "muted": "2;37",
}


@dataclass
class HeadingNode:
    """Represents a Markdown heading and its section span."""

    level: int
    title: str
    start_line: int
    parent: Optional["HeadingNode"] = None
    children: List["HeadingNode"] = field(default_factory=list)
    end_line: int = -1


def parse_markdown_headings(lines: List[str]) -> List[HeadingNode]:
    nodes: List[HeadingNode] = []
    stack: List[HeadingNode] = []

    for idx, line in enumerate(lines):
        match = HEADING_PATTERN.match(line)
        if not match:
            continue

        level = len(match.group(1))
        title = match.group(2).strip()

        while stack and level <= stack[-1].level:
            stack.pop()

        parent = stack[-1] if stack else None
        node = HeadingNode(level=level, title=title, start_line=idx, parent=parent)
        if parent:
            parent.children.append(node)

        stack.append(node)
        nodes.append(node)

    total_lines = len(lines)
    for i, node in enumerate(nodes):
        end = total_lines - 1
        for other in nodes[i + 1 :]:
            if other.level <= node.level:
                end = other.start_line - 1
                break
        node.end_line = end

    return nodes


def parse_path_spec(spec: str) -> List[int]:
    if not spec:
        raise ValueError("Section path cannot be empty.")

    try:
        parts = [int(part) for part in spec.split(".")]
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ValueError(f"Invalid section path '{spec}'.") from exc

    if any(part <= 0 for part in parts):
        raise ValueError("Section indexes must be positive integers.")

    return parts


def resolve_section(
    nodes: List[HeadingNode],
    path_segments: Iterable[int],
    base_level: int,
) -> HeadingNode:
    current: Optional[HeadingNode] = None

    for depth, index in enumerate(path_segments):
        target_level = base_level + depth
        if depth == 0:
            candidates = [node for node in nodes if node.level == target_level]
        else:
            candidates = [
                node
                for node in nodes
                if node.level == target_level and node.parent is current
            ]

        if not candidates:
            raise LookupError(
                f"No headings found for level {target_level} in the selected branch."
            )

        if index > len(candidates):
            raise LookupError(
                f"Requested index {index} exceeds available headings ({len(candidates)})."
            )

        current = candidates[index - 1]

    if current is None:
        raise LookupError("Unable to resolve section path.")

    return current


def select_section(
    path: Path, spec: str, base_level: int
) -> tuple[HeadingNode, str]:
    if not path.exists():
        raise FileNotFoundError(f"Markdown file '{path}' does not exist.")

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    nodes = parse_markdown_headings(lines)
    if not nodes:
        raise LookupError("No headings found in the provided Markdown file.")

    path_segments = parse_path_spec(spec)
    target = resolve_section(nodes, path_segments, base_level)
    end_idx = max(target.end_line, target.start_line)
    section_text = "".join(lines[target.start_line : end_idx + 1])
    return target, section_text


def extract_section_text(path: Path, spec: str, base_level: int) -> str:
    _, text = select_section(path, spec, base_level)
    return text


def heading_chain(node: HeadingNode) -> List[HeadingNode]:
    chain: List[HeadingNode] = []
    current: Optional[HeadingNode] = node
    while current is not None:
        chain.append(current)
        current = current.parent
    return list(reversed(chain))


def supports_color(stream) -> bool:
    return hasattr(stream, "isatty") and stream.isatty()


def colorize(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"\033[{code}m{text}\033[0m"


def format_section_output(
    *,
    section_text: str,
    target: HeadingNode,
    spec: str,
    color_enabled: bool,
    plain: bool,
) -> str:
    if plain:
        return section_text

    breadcrumbs = " > ".join(node.title for node in heading_chain(target))
    label = colorize("Section", COLOR_CODES["label"], color_enabled)
    spec_colored = colorize(spec, COLOR_CODES["path"], color_enabled)
    crumbs_colored = colorize(breadcrumbs, COLOR_CODES["breadcrumb"], color_enabled)

    header_line = f"{label} {spec_colored}"
    info_line = crumbs_colored
    separator_length = max(len(breadcrumbs), len(f"Section {spec}"))
    separator = colorize("-" * separator_length, COLOR_CODES["muted"], color_enabled)

    body = section_text.rstrip("\n")
    return "\n".join([header_line, info_line, separator, body]) + "\n"


def project_version() -> str:
    try:
        return importlib.metadata.version("markat")
    except importlib.metadata.PackageNotFoundError:
        return __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mkat",
        description=(
            "Print a Markdown subsection using dotted heading indexes, e.g.\n"
            "2.3.2 => second ##, third ### within it, second #### next."
        ),
        epilog="Example: mkat docs/spec.md 2.3.2 --base-level 2",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("markdown_file", type=Path, help="Path to the Markdown file")
    parser.add_argument(
        "section_path",
        help="Dotted list of section indexes (e.g. 2.3.2 for ##/###/####).",
    )
    parser.add_argument(
        "--base-level",
        type=int,
        default=DEFAULT_BASE_LEVEL,
        help="Heading level that corresponds to the first index (default: 2 for '##').",
    )
    parser.add_argument(
        "-p",
        "--plain",
        action="store_true",
        help="Output raw section text only (suppresses headers and colors).",
    )
    parser.add_argument(
        "--color",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Force enable/disable ANSI colors (auto-detect when omitted).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"mkat {project_version()}",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        target, section_text = select_section(
            args.markdown_file, args.section_path, args.base_level
        )
    except (ValueError, FileNotFoundError, LookupError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")

    if args.color is None:
        color_enabled = not args.plain and supports_color(sys.stdout)
    else:
        color_enabled = not args.plain and args.color

    output = format_section_output(
        section_text=section_text,
        target=target,
        spec=args.section_path,
        color_enabled=color_enabled,
        plain=args.plain,
    )

    sys.stdout.write(output)
    if not output.endswith("\n"):
        sys.stdout.write("\n")
    return 0


__all__ = [
    "HeadingNode",
    "build_parser",
    "colorize",
    "extract_section_text",
    "format_section_output",
    "main",
    "parse_markdown_headings",
    "parse_path_spec",
    "resolve_section",
    "select_section",
]
