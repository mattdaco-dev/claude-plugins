#!/usr/bin/env python3
"""Typography lint for natural-language text.

Checks:
  1. Em dash (U+2014) and spaced en dash used as an aside (spaced U+2013), in every
     text file. Markdown inline code and fenced code blocks are skipped, so a
     rule can still quote the character in backticks.
  2. French UI text only: a non-breaking space (U+00A0 or narrow U+202F, or
     the HTML entities &nbsp; &#160; &#8239; &#x202f;) is required before
     ; ? ! and », after «, and a regular space before : is flagged.
     UI files are HTML, Vue, Svelte, JS/TS, JSON, PO. Only the text that is
     displayed is read: HTML text nodes and attribute values, string
     literals in scripts, string values in JSON. Markdown is never checked
     for spacing (sources read by people and agents, not rendered copy).
     A UI file counts as French when an HTML file declares lang="fr", when
     its path has a French marker (/fr/, fr.json, .fr., _fr., -fr.), or when
     --fr is given.

Silence one line with the marker  typo-lint-ignore  on it.

Usage: typo-lint.py [--fr] [path ...]   (default: current directory)
Exit 1 when a violation is found, 0 otherwise.
"""
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "dist", "build", "vendor", "coverage",
             ".next", ".nuxt", ".venv", "__pycache__", "synced", ".trash"}
TEXT_EXT = {".md", ".mdx", ".txt", ".html", ".htm", ".vue", ".svelte", ".js",
            ".jsx", ".mjs", ".ts", ".tsx", ".json", ".po", ".yml", ".yaml",
            ".py", ".sh", ".dsl"}
UI_EXT = {".html", ".htm", ".vue", ".svelte", ".js", ".jsx", ".mjs", ".ts",
          ".tsx", ".json", ".po"}
FR_PATH = re.compile(r"(^|[/._-])fr([/._-]|$)", re.I)
IGNORE = "typo-lint-ignore"

EM_DASH = re.compile("\u2014")
EN_DASH_ASIDE = re.compile("\\s\u2013\\s")
NBSP = "\u00a0"
ENTITIES = re.compile(r"&nbsp;|&#160;|&#xa0;|&#8239;|&#x202f;", re.I)
# Regular space before ; ? ! » or :, regular space after «, and no space at
# all before ; ? ! » or after «. A missing space before ":" is not flagged
# (times, ratios, URLs).
FR_RULES = [
    (re.compile(r"(?<=[\w)\]»\"'…]) [:;?!»]"), "regular space before {c}: use a non-breaking space"),
    (re.compile(r"« "), "regular space after «: use a non-breaking space"),
    (re.compile(r"(?<=\w)[;?!](?=\s|$|[\"'`<])"), "no space before {c}: add a non-breaking space"),
    (re.compile(r"(?<=\w)»"), "no space before »: add a non-breaking space"),
    (re.compile(r"«(?=\w)"), "no space after «: add a non-breaking space"),
]

# Displayed-text extractors for UI files: each yields (line_offset_in_file, text).
STRING_LIT = re.compile(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"|`(?:\\.|[^`\\])*`", re.S)
HTML_SKIP = re.compile(r"<(script|style)\b[^>]*>.*?</\1\s*>|<!--.*?-->", re.S | re.I)
HTML_TAG = re.compile(r"<[^>]+>", re.S)
HTML_ATTR = re.compile(r"\b(?:title|alt|placeholder|aria-label|aria-description|value|content|label)\s*=\s*(\"[^\"]*\"|'[^']*')", re.I)
SCRIPT_BODY = re.compile(r"<script\b[^>]*>(.*?)</script\s*>", re.S | re.I)


def blank(text, start, end):
    """Replace a span by spaces, keeping newlines so line numbers hold."""
    return text[:start] + re.sub(r"[^\n]", " ", text[start:end]) + text[end:]


def strip_markdown_code(text):
    for m in reversed(list(re.finditer(r"^(```|~~~).*?^\1[^\n]*$", text, re.S | re.M))):
        text = blank(text, m.start(), m.end())
    for m in reversed(list(re.finditer(r"(`+)(?!`).+?(?<!`)\1(?!`)", text))):
        text = blank(text, m.start(), m.end())
    return text


def keep_spans(text, spans):
    """Blank everything outside the given (start, end) spans."""
    out, pos = [], 0
    for start, end in sorted(spans):
        if start < pos:
            continue
        out.append(re.sub(r"[^\n]", " ", text[pos:start]))
        out.append(text[start:end])
        pos = end
    out.append(re.sub(r"[^\n]", " ", text[pos:]))
    return "".join(out)


def displayed_text(path, text):
    ext = os.path.splitext(path)[1].lower()
    if ext in {".js", ".jsx", ".mjs", ".ts", ".tsx", ".json"}:
        return keep_spans(text, [(m.start() + 1, m.end() - 1) for m in STRING_LIT.finditer(text)])
    if ext == ".po":
        return keep_spans(text, [(m.start() + 1, m.end() - 1) for m in re.finditer(r'(?m)^msgstr\s+"(?:\\.|[^"\\])*"', text)])
    # HTML, Vue, Svelte: text nodes, displayed attributes, and string literals
    # inside <script> blocks.
    spans = [(m.start(1) + 1, m.end(1) - 1) for m in HTML_ATTR.finditer(text)]
    for m in SCRIPT_BODY.finditer(text):
        spans += [(m.start(1) + s.start() + 1, m.start(1) + s.end() - 1) for s in STRING_LIT.finditer(m.group(1))]
    markup = text
    for m in reversed(list(HTML_SKIP.finditer(markup))):
        markup = blank(markup, m.start(), m.end())
    for m in reversed(list(HTML_TAG.finditer(markup))):
        markup = blank(markup, m.start(), m.end())
    attrs = keep_spans(text, spans)
    # Merge: a character is kept if either view kept it.
    return "".join(a if a != " " else b for a, b in zip(markup, attrs))


def is_french(path, text, force):
    if force or FR_PATH.search(path.replace(os.sep, "/")):
        return True
    if os.path.splitext(path)[1].lower() in {".html", ".htm"}:
        return re.search(r"<html\b[^>]*\blang\s*=\s*[\"']fr", text, re.I) is not None
    return False


def lint(path, force_fr):
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (UnicodeDecodeError, OSError):
        return []
    raw_lines = text.split("\n")
    issues = []
    ext = os.path.splitext(path)[1].lower()

    prose = strip_markdown_code(text) if ext in {".md", ".mdx"} else text
    for n, line in enumerate(prose.split("\n"), 1):
        if IGNORE in raw_lines[n - 1]:
            continue
        if EM_DASH.search(line):
            issues.append((n, "em dash: rephrase with a comma, a colon, parentheses or two sentences"))
        if EN_DASH_ASIDE.search(line):
            issues.append((n, "en dash used as an aside: rephrase"))

    if ext in UI_EXT and is_french(path, text, force_fr):
        shown = ENTITIES.sub(lambda m: NBSP.ljust(len(m.group(0))), displayed_text(path, text))
        for n, line in enumerate(shown.split("\n"), 1):
            if IGNORE in raw_lines[n - 1]:
                continue
            for rule, message in FR_RULES:
                m = rule.search(line)
                if m:
                    issues.append((n, message.format(c=m.group(0).strip())))
    return issues


def walk(paths):
    for root in paths:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for name in sorted(filenames):
                if os.path.splitext(name)[1].lower() in TEXT_EXT:
                    yield os.path.join(dirpath, name)


def main(argv):
    force_fr = "--fr" in argv
    paths = [a for a in argv if a != "--fr"] or ["."]
    found = 0
    for path in walk(paths):
        for n, message in lint(path, force_fr):
            print(f"{os.path.normpath(path)}:{n}: {message}")
            found += 1
    if found:
        print(f"\n{found} typography issue(s). Silence a line on purpose with '{IGNORE}'.")
        return 1
    print("Typography lint: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
