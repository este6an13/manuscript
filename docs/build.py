#!/usr/bin/env python3
"""
build.py — Manuscript Static Site Generator

Parses Python source files from the manuscript repository and generates static
HTML pages styled as an ancient illuminated manuscript. Uses only the Python
standard library (zero external dependencies).

Usage:
    python docs/build.py

Output:
    docs/
    ├── index.html
    └── pages/
        └── {algorithm-name}.html
"""

from __future__ import annotations

import ast
import html
import io
import re
import tokenize
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent  # docs/
REPO_ROOT = SCRIPT_DIR.parent  # manuscript/

PAGES_DIR = SCRIPT_DIR / "pages"

# Directories to always skip when discovering algorithms
SKIP_DIRS = {"docs", ".git", "__pycache__"}


# ---------------------------------------------------------------------------
# Roman Numerals
# ---------------------------------------------------------------------------

_ROMAN_UPPER = [
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
]
_ROMAN_LOWER = [r.lower() for r in _ROMAN_UPPER]


def to_roman(n: int, *, upper: bool = True) -> str:
    """Return a Roman numeral string for *n* (1-indexed, capped at 20)."""
    idx = max(0, min(n - 1, len(_ROMAN_UPPER) - 1))
    return _ROMAN_UPPER[idx] if upper else _ROMAN_LOWER[idx]


# ---------------------------------------------------------------------------
# 1. DISCOVERY — find algorithm directories
# ---------------------------------------------------------------------------


def discover_algorithms() -> list[Path]:
    """Return sorted list of algorithm directories (subdirs of repo root
    that contain a ``main.py`` and whose name doesn't start with ``.`` or
    ``_`` and is not in *SKIP_DIRS*).
    """
    dirs: list[Path] = []
    for entry in sorted(REPO_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        if name.startswith(".") or name.startswith("_"):
            continue
        if name in SKIP_DIRS:
            continue
        if (entry / "main.py").exists():
            dirs.append(entry)
    return dirs


# ---------------------------------------------------------------------------
# 2. COMMENT EXTRACTION via tokenize
# ---------------------------------------------------------------------------


def extract_comments(source: str) -> dict[int, str]:
    """Use Python's ``tokenize`` module to deterministically extract comments.

    Returns ``{line_number: comment_text}`` with the leading ``#`` stripped.
    """
    comments: dict[int, str] = {}
    source = source.replace("\r\n", "\n")
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for tok_type, tok_string, (srow, _scol), _end, _line in tokens:
            if tok_type == tokenize.COMMENT:
                # Strip the leading '#' and optional space
                text = tok_string.lstrip("#").strip()
                if text:
                    comments[srow] = text
    except tokenize.TokenError:
        pass  # gracefully handle incomplete source
    return comments


# ---------------------------------------------------------------------------
# 3. AST PARSING
# ---------------------------------------------------------------------------


def _get_docstring(node: ast.AST) -> str | None:
    """Return the docstring of a function/class node, or None."""
    return ast.get_docstring(node)


def parse_functions(source: str) -> dict[str, Any]:
    """Parse top-level functions and detect ``if __name__ == "__main__"`` block.

    Returns::

        {
            "functions": [
                {"name": str, "start_line": int, "end_line": int, "docstring": str | None},
                ...
            ],
            "main_block": {"start_line": int, "end_line": int} | None
        }
    """
    tree = ast.parse(source)
    functions: list[dict[str, Any]] = []
    main_block: dict[str, int] | None = None

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno or node.lineno,
                    "docstring": _get_docstring(node),
                }
            )
        elif isinstance(node, ast.If):
            # Detect:  if __name__ == "__main__":
            test = node.test
            if (
                isinstance(test, ast.Compare)
                and len(test.ops) == 1
                and isinstance(test.ops[0], ast.Eq)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"
            ):
                end = node.end_lineno or node.lineno
                main_block = {"start_line": node.lineno, "end_line": end}

    return {"functions": functions, "main_block": main_block}


def parse_test_classes(source: str) -> list[dict[str, Any]]:
    """Extract ``ClassDef`` nodes with their methods from test source.

    Returns::

        [
            {
                "name": str,
                "start_line": int,
                "end_line": int,
                "methods": [
                    {"name": str, "start_line": int, "end_line": int},
                    ...
                ]
            },
            ...
        ]
    """
    tree = ast.parse(source)
    classes: list[dict[str, Any]] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.append(
                        {
                            "name": item.name,
                            "start_line": item.lineno,
                            "end_line": item.end_lineno or item.lineno,
                        }
                    )
            classes.append(
                {
                    "name": node.name,
                    "start_line": node.lineno,
                    "end_line": node.end_lineno or node.lineno,
                    "methods": methods,
                }
            )
    return classes


# ---------------------------------------------------------------------------
# 4. MARKDOWN → HTML (regex-based, no dependencies)
# ---------------------------------------------------------------------------


def _process_inline(text: str) -> str:
    """Convert inline Markdown elements to HTML.

    Processing order matters — escape HTML first, then code, links, bold,
    italic, math.
    """
    # 1) Escape HTML entities
    text = html.escape(text)

    # 2) Inline code (`` `...` ``) — protect from further processing
    code_parts: list[str] = []

    def _stash_code(m: re.Match) -> str:
        placeholder = f"\x00CODE{len(code_parts)}\x00"
        code_parts.append(f"<code>{m.group(1)}</code>")
        return placeholder

    text = re.sub(r"`([^`]+)`", _stash_code, text)

    # 3) Links [text](url)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )

    # 4) Bold **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)

    # 5) Italic *text*  (but not **)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)

    # 6) Math $...$
    text = re.sub(r"\$([^$]+)\$", r'<span class="math">\1</span>', text)

    # Restore stashed code spans
    for i, code_html in enumerate(code_parts):
        text = text.replace(f"\x00CODE{i}\x00", code_html)

    return text


def markdown_to_html(md: str) -> str:
    """Convert a Markdown string to HTML using regex.

    Handles: headers, bold, italic, inline code, fenced code blocks, links,
    unordered/ordered lists, tables, blockquotes, horizontal rules, math,
    and paragraphs.  Uses ``html.escape`` for safety.
    """
    md = md.replace("\r\n", "\n")
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]

        # --- Fenced code blocks ---
        fence_match = re.match(r"^```(\w*)", line)
        if fence_match:
            lang = fence_match.group(1)
            code_lines: list[str] = []
            i += 1
            while i < total and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            lang_attr = f' class="language-{lang}"' if lang else ""
            escaped_code = html.escape("\n".join(code_lines))
            out.append(f"<pre><code{lang_attr}>{escaped_code}</code></pre>")
            continue

        # --- Horizontal rule ---
        if re.match(r"^---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # --- Headers ---
        header_match = re.match(r"^(#{1,6})\s+(.*)", line)
        if header_match:
            level = len(header_match.group(1))
            content = _process_inline(header_match.group(2))
            out.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # --- Blockquote ---
        if line.startswith(">"):
            bq_lines: list[str] = []
            while i < total and lines[i].startswith(">"):
                bq_lines.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            inner = _process_inline(" ".join(bq_lines))
            out.append(f"<blockquote><p>{inner}</p></blockquote>")
            continue

        # --- Unordered list ---
        if re.match(r"^[-*]\s+", line):
            items: list[str] = []
            while i < total and re.match(r"^[-*]\s+", lines[i]):
                items.append(_process_inline(re.sub(r"^[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>")
            for item in items:
                out.append(f"  <li>{item}</li>")
            out.append("</ul>")
            continue

        # --- Ordered list ---
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < total and re.match(r"^\d+\.\s+", lines[i]):
                items.append(_process_inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            out.append("<ol>")
            for item in items:
                out.append(f"  <li>{item}</li>")
            out.append("</ol>")
            continue

        # --- Table ---
        if (
            "|" in line
            and i + 1 < total
            and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])
        ):
            # Header row
            headers = [
                _process_inline(c.strip()) for c in line.strip().strip("|").split("|")
            ]
            i += 2  # skip header + separator
            rows: list[list[str]] = []
            while i < total and "|" in lines[i] and lines[i].strip():
                cells = [
                    _process_inline(c.strip())
                    for c in lines[i].strip().strip("|").split("|")
                ]
                rows.append(cells)
                i += 1
            out.append("<table>")
            out.append("  <thead><tr>")
            for h in headers:
                out.append(f"    <th>{h}</th>")
            out.append("  </tr></thead>")
            out.append("  <tbody>")
            for row in rows:
                out.append("  <tr>")
                for cell in row:
                    out.append(f"    <td>{cell}</td>")
                out.append("  </tr>")
            out.append("  </tbody>")
            out.append("</table>")
            continue

        # --- Empty line ---
        if not line.strip():
            i += 1
            continue

        # --- Paragraph (default) ---
        para_lines: list[str] = []
        while (
            i < total
            and lines[i].strip()
            and not re.match(
                r"^(#{1,6}\s|```|---+\s*$|>\s|[-*]\s|\d+\.\s|\|)", lines[i]
            )
        ):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            inner = _process_inline(" ".join(para_lines))
            out.append(f"<p>{inner}</p>")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# 5. ROOT README PARSING — extract algorithm metadata
# ---------------------------------------------------------------------------

# Pattern: | **Category** | **Algorithm** | Description | [`/dir`](link) |
_TABLE_RE = re.compile(
    r"\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*\[`([^`]+)`\]"
)


def parse_root_readme(readme_path: Path) -> list[dict[str, str]]:
    """Extract algorithm metadata from the table in the root README.md.

    Returns a list of dicts with keys: category, algorithm, description, dir_name.
    """
    text = readme_path.read_text(encoding="utf-8")
    entries: list[dict[str, str]] = []
    for m in _TABLE_RE.finditer(text):
        category = m.group(1).strip()
        algorithm = m.group(2).strip()
        description = m.group(3).strip()
        dir_ref = m.group(4).strip().strip("/")
        entries.append(
            {
                "category": category,
                "algorithm": algorithm,
                "description": description,
                "dir_name": dir_ref,
            }
        )
    return entries


# ---------------------------------------------------------------------------
# 6. HTML GENERATION
# ---------------------------------------------------------------------------


def _strip_emoji(title: str) -> str:
    """Remove emoji / non-word characters from a title string."""
    return re.sub(r"[^\w\s()\-]", "", title).strip()


def _extract_lines(source: str, start: int, end: int) -> str:
    """Return lines [start..end] (1-indexed inclusive) from *source*."""
    all_lines = source.splitlines(True)
    selected = all_lines[start - 1 : end]
    return "".join(selected)


def _build_margin_notes(
    comments: dict[int, str],
    start_line: int,
    end_line: int,
) -> list[dict[str, Any]]:
    """Build margin-note dicts for comments falling within [start_line, end_line]."""
    notes: list[dict[str, Any]] = []
    for abs_line in sorted(comments):
        if start_line <= abs_line <= end_line:
            notes.append(
                {
                    "relative_line": abs_line - start_line + 1,
                    "absolute_line": abs_line,
                    "text": comments[abs_line],
                }
            )
    return notes


def _render_margin_notes_html(notes: list[dict[str, Any]]) -> str:
    """Render the <aside class="margin-notes"> block."""
    if not notes:
        return ""
    parts = []
    for n in notes:
        parts.append(
            f'                        <div class="margin-note" '
            f'data-line="{n["relative_line"]}" '
            f'data-absolute-line="{n["absolute_line"]}">\n'
            f'                            <span class="note-line-ref">l.{n["absolute_line"]}</span>\n'
            f'                            <span class="note-text">{html.escape(n["text"])}</span>\n'
            f"                        </div>"
        )
    return "\n".join(parts)


def _render_code_section(
    section_id: str,
    section_numeral: str,
    section_name: str,
    code_text: str,
    notes: list[dict[str, Any]],
) -> str:
    """Render a single code section (function / main block / test class)."""
    has_notes_class = " has-notes" if notes else ""
    escaped_code = html.escape(code_text)

    notes_html = ""
    if notes:
        notes_inner = _render_margin_notes_html(notes)
        notes_html = (
            f'\n                    <aside class="margin-notes" data-section="{section_id}">\n'
            f"{notes_inner}\n"
            f"                    </aside>"
        )

    return f"""
            <section class="codex-section" id="{section_id}">
                <h3 class="section-heading">
                    <span class="section-numeral">§ {section_numeral}</span>
                    <span class="section-name">{html.escape(section_name)}</span>
                </h3>
                <div class="section-content{has_notes_class}">
                    <pre class="code-block"><code class="language-python" data-section="{section_id}">{escaped_code}</code></pre>{notes_html}
                </div>
            </section>"""


def generate_algorithm_page(
    algo_dir: Path,
    chapter_number: int,
    meta: dict[str, str] | None,
) -> str:
    """Generate the full HTML for a single algorithm page."""

    # --- Read sources ---
    main_source = (algo_dir / "main.py").read_text(encoding="utf-8")
    main_source = main_source.replace("\r\n", "\n")

    tests_source: str | None = None
    tests_path = algo_dir / "tests.py"
    if tests_path.exists():
        tests_source = tests_path.read_text(encoding="utf-8")
        tests_source = tests_source.replace("\r\n", "\n")

    # Omitted reading README.md per user request.

    # --- Parse ---
    comments = extract_comments(main_source)
    parsed = parse_functions(main_source)
    functions = parsed["functions"]
    main_block = parsed["main_block"]

    # --- Title ---
    if meta:
        title = meta["algorithm"]
        category = meta["category"]
    else:
        # Fallback: use directory name
        raw_title = algo_dir.name.replace("-", " ").title()
        title = _strip_emoji(raw_title)
        category = ""

    page_title = _strip_emoji(title)
    roman_chapter = to_roman(chapter_number, upper=True)
    roman_page = to_roman(chapter_number, upper=False)

    # --- Build source sections ---
    source_sections: list[str] = []
    sec_num = 0

    for fn in functions:
        sec_num += 1
        code = _extract_lines(main_source, fn["start_line"], fn["end_line"])
        notes = _build_margin_notes(comments, fn["start_line"], fn["end_line"])
        source_sections.append(
            _render_code_section(
                section_id=f"fn-{fn['name']}",
                section_numeral=to_roman(sec_num, upper=True),
                section_name=fn["name"],
                code_text=code,
                notes=notes,
            )
        )

    # __main__ block → "Demonstration"
    if main_block:
        sec_num += 1
        code = _extract_lines(
            main_source, main_block["start_line"], main_block["end_line"]
        )
        notes = _build_margin_notes(
            comments, main_block["start_line"], main_block["end_line"]
        )
        source_sections.append(
            _render_code_section(
                section_id="fn-__main__",
                section_numeral=to_roman(sec_num, upper=True),
                section_name="Demonstration",
                code_text=code,
                notes=notes,
            )
        )

    source_html = "\n".join(source_sections)

    # --- Build verification sections (tests) ---
    verification_html = ""
    if tests_source:
        test_comments = extract_comments(tests_source)
        test_classes = parse_test_classes(tests_source)

        if test_classes:
            test_sections: list[str] = []
            for tc_num, tc in enumerate(test_classes, 1):
                code = _extract_lines(tests_source, tc["start_line"], tc["end_line"])
                notes = _build_margin_notes(
                    test_comments, tc["start_line"], tc["end_line"]
                )
                test_sections.append(
                    _render_code_section(
                        section_id=f"test-{tc['name']}",
                        section_numeral=to_roman(tc_num, upper=True),
                        section_name=tc["name"],
                        code_text=code,
                        notes=notes,
                    )
                )

            verification_html = f"""
        <div class="ornamental-divider">✦ ✦ ✦</div>
        <section class="codex-chapter" id="verification">
            <h2 class="chapter-heading">Verification Appendix</h2>
{"".join(test_sections)}
        </section>"""

    # --- Introduction section ---
    introduction_html = ""

    # --- Category subtitle ---
    category_html = ""
    if category:
        category_html = (
            f'\n            <div class="codex-subtitle">{html.escape(category)}</div>'
        )

    # --- Assemble page ---
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(page_title)} — Manuscript</title>
    <link rel="icon" type="image/png" href="../img/scroll.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cinzel+Decorative:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=JetBrains+Mono:wght@400;500&family=Caveat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/manuscript.css">
</head>
<body class="manuscript-page">
    <nav class="manuscript-nav">
        <a href="../index.html" class="nav-home">📜 Manuscript</a>
        <div class="nav-controls">
            <button id="theme-toggle" class="theme-toggle" aria-label="Toggle dark mode">
                <span class="theme-icon-light">🕯️</span>
                <span class="theme-icon-dark">🌙</span>
            </button>
        </div>
    </nav>
    <article class="codex">
        <div class="codex-border codex-border-top"></div>
        <header class="codex-header">
            <div class="chapter-numeral">Chapter {roman_chapter}</div>
            <h1 class="codex-title">{html.escape(page_title)}</h1>{category_html}
            <div class="ornamental-rule">❦ ❦ ❦</div>
        </header>
{introduction_html}
        <section class="codex-chapter" id="source">
            <h2 class="chapter-heading">The Source</h2>
{source_html}
        </section>
{verification_html}
        <footer class="codex-footer">
            <div class="ornamental-rule">❦</div>
            <span class="page-number">— {roman_page} —</span>
        </footer>
        <div class="codex-border codex-border-bottom"></div>
    </article>
    <div class="site-copyright">&copy; 2026 Diego Esteban</div>
    <script src="../js/manuscript.js"></script>
</body>
</html>
"""


def generate_index_page(
    algorithm_entries: list[dict[str, str]],
) -> str:
    """Generate the index.html page listing all algorithms."""

    # --- Table of contents ---
    toc_items: list[str] = []
    for i, entry in enumerate(algorithm_entries, 1):
        roman = to_roman(i, upper=True)
        name = entry["dir_name"]
        title = _strip_emoji(entry["algorithm"])
        category = html.escape(entry["category"])
        toc_items.append(f"""                <li class="toc-entry">
                    <a href="pages/{name}.html" class="toc-link">
                        <span class="toc-numeral">{roman}.</span>
                        <span class="toc-title">{html.escape(title)}</span>
                    </a>
                </li>""")

    toc_html = "\n".join(toc_items)

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manuscript</title>
    <link rel="icon" type="image/png" href="img/scroll.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cinzel+Decorative:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&family=JetBrains+Mono:wght@400;500&family=Caveat:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="css/manuscript.css">
</head>
<body class="manuscript-page manuscript-index">
    <nav class="manuscript-nav">
        <a href="index.html" class="nav-home">📜 Manuscript</a>
        <div class="nav-controls">
            <button id="theme-toggle" class="theme-toggle" aria-label="Toggle dark mode">
                <span class="theme-icon-light">☀️</span>
                <span class="theme-icon-dark">🌙</span>
            </button>
        </div>
    </nav>
    <article class="codex">
        <div class="codex-border codex-border-top"></div>
        <header class="codex-header index-header">
            <div class="title-decoration">✦</div>
            <h1 class="codex-title index-title">Manuscript</h1>
            <p class="index-epigraph">&ldquo;These pages were written not to produce machines, but to instruct the mind.&rdquo;</p>
            <div class="ornamental-rule">❦ ❦ ❦</div>
        </header>
        <section class="index-toc">
            <h2 class="chapter-heading">Table of Contents</h2>
            <ol class="toc-list">
{toc_html}
            </ol>
        </section>
        <footer class="codex-footer">
            <div class="ornamental-rule">❦</div>
        </footer>
        <div class="codex-border codex-border-bottom"></div>
    </article>
    <div class="site-copyright">&copy; 2026 Diego Esteban</div>
    <script src="js/manuscript.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main — orchestrate the build
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("  📜  Manuscript — Static Site Builder")
    print("=" * 60)
    print()

    # --- Discover algorithms ---
    print("[1/5] Discovering algorithm directories...")
    algo_dirs = discover_algorithms()
    if not algo_dirs:
        print("  ⚠  No algorithm directories found. Nothing to build.")
        return
    for d in algo_dirs:
        print(f"  ✓  Found: {d.name}/")
    print()

    # --- Parse root README ---
    print("[2/5] Parsing root README.md for metadata...")
    root_readme = REPO_ROOT / "README.md"
    readme_entries = parse_root_readme(root_readme) if root_readme.exists() else []
    meta_lookup: dict[str, dict[str, str]] = {e["dir_name"]: e for e in readme_entries}
    print(f"  ✓  Found {len(readme_entries)} algorithm entries in README table.")
    print()

    # --- Create output directories ---
    print("[3/5] Preparing output directories...")
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"  ✓  {PAGES_DIR.relative_to(REPO_ROOT)}/")
    print()

    # --- Generate algorithm pages ---
    print("[4/5] Generating algorithm pages...")
    # Build ordered list: prefer README table order, then remaining dirs
    ordered_entries: list[dict[str, str]] = []
    processed_dirs: set[str] = set()

    # First, algorithms that appear in the README table (preserves table order)
    for entry in readme_entries:
        dir_name = entry["dir_name"]
        dir_path = REPO_ROOT / dir_name
        if dir_path in algo_dirs:
            ordered_entries.append(entry)
            processed_dirs.add(dir_name)

    # Then, any remaining discovered directories not in the README
    for d in algo_dirs:
        if d.name not in processed_dirs:
            ordered_entries.append(
                {
                    "category": "",
                    "algorithm": d.name.replace("-", " ").title(),
                    "description": "",
                    "dir_name": d.name,
                }
            )

    for chapter_num, entry in enumerate(ordered_entries, 1):
        dir_name = entry["dir_name"]
        algo_dir = REPO_ROOT / dir_name
        meta = meta_lookup.get(dir_name)
        print(f"  → Chapter {to_roman(chapter_num)}: {entry['algorithm']}...")

        page_html = generate_algorithm_page(algo_dir, chapter_num, meta)
        out_path = PAGES_DIR / f"{dir_name}.html"
        out_path.write_text(page_html, encoding="utf-8")
        print(f"    ✓  Written: {out_path.relative_to(REPO_ROOT)}")

    print()

    # --- Generate index page ---
    print("[5/5] Generating index page...")
    index_html = generate_index_page(ordered_entries)
    index_path = SCRIPT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    print(f"  ✓  Written: {index_path.relative_to(REPO_ROOT)}")
    print()

    # --- Summary ---
    print("=" * 60)
    print(f"  ✅  Build complete! Generated {len(ordered_entries)} page(s) + index.")
    print(f"  📁  Output: {SCRIPT_DIR.relative_to(REPO_ROOT)}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
