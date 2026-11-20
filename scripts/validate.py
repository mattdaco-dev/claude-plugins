#!/usr/bin/env python3
"""Consistency checks for the claude-plugins marketplace.

Errors (exit 1):
  1. Marketplace: .claude-plugin/marketplace.json parses, plugin names are
     unique, every local source folder exists and holds a
     .claude-plugin/plugin.json whose name matches, with a semver version;
     every external source (github, git, url) is pinned by a 40-character sha.
  2. Skills: plugins/<p>/skills/<dir>/SKILL.md exists, frontmatter parses,
     name equals the folder, kebab-case (64 chars max), description present
     and at most 1024 characters.
  3. Agents: plugins/<p>/agents/<name>.md, name equals the file name,
     description present.
  4. Hooks: hooks/hooks.json parses and every ${CLAUDE_PLUGIN_ROOT}/<path> it
     cites exists. Same for .mcp.json.
  5. References in Markdown files:
       - `plugin:name` for a plugin of this marketplace names an existing
         skill or agent of that plugin,
       - "skill `x`" / "agent `x`" names a skill or agent of the same plugin,
         or a known external one,
       - paths inside a skill whose first segment is a folder of that skill,
         and ../ paths that lead to a sibling skill, exist,
       - repository paths (plugins/..., scripts/..., Markdown links) exist.
  6. Shell scripts pass sh -n (bash -n for a bash shebang), Python files compile, JSON files parse.
  7. Optional denylist: if .denylist.local exists (one word or phrase per
     line, not versioned), no versioned text file may contain those words.

Warnings (no failure): an unquoted ": " in a one-line frontmatter value.

Usage: validate.py        (checks the repository it lives in)
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
EXTERNAL = {
    "general-purpose", "Explore", "Plan", "claude-code-guide", "statusline-setup",
    "skill-creator", "docx", "xlsx", "pptx", "pdf", "simplify", "code-review",
    "security-review", "init", "run", "loop", "schedule", "update-config",
}

errors, warnings = [], []


def rel(path):
    return os.path.relpath(path, ROOT)


def err(path, msg):
    errors.append(f"{rel(path)}: {msg}")


def warn(path, msg):
    warnings.append(f"{rel(path)}: {msg}")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_json(path):
    try:
        return json.loads(read(path))
    except (OSError, ValueError) as e:
        err(path, f"invalid JSON: {e}")
        return None


def frontmatter(path):
    """Return (dict, error) for a minimal YAML frontmatter, or (None, None)."""
    text = read(path)
    if not text.startswith("---\n"):
        return None, None
    end = text.find("\n---", 4)
    if end < 0:
        return None, "frontmatter is not closed"
    data, key = {}, None
    for n, line in enumerate(text[4:end].split("\n"), 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if m and not line.startswith((" ", "\t")):
            key, value = m.group(1), m.group(2)
            if not value.startswith(("'", '"')):
                value = re.sub(r"\s+#.*$", "", value)
            if value in (">", "|", ">-", "|-", ""):
                data[key] = ""
                continue
            if not value.startswith(("'", '"', "[", "{")) and re.search(r":\s", value):
                warn(path, f"line {n}: unquoted ': ' in '{key}' (strict YAML parsers reject it)")
            data[key] = value.strip("'\"")
        elif key and line.startswith((" ", "\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
        else:
            return None, f"line {n}: cannot parse '{line.strip()}'"
    return data, None


def walk_files(base, exts=None):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if exts is None or os.path.splitext(name)[1] in exts:
                yield os.path.join(dirpath, name)


# 1. Marketplace -----------------------------------------------------------------
plugins = {}  # name -> folder
market_path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
market = load_json(market_path) or {}
seen = set()
for entry in market.get("plugins", []):
    name = entry.get("name")
    if name in seen:
        err(market_path, f"plugin '{name}' listed twice")
    seen.add(name)
    source = entry.get("source")
    if not isinstance(source, str):
        # External plugin (github, git, url): its code is not checked here, so
        # it must be pinned to a reviewed commit.
        sha = source.get("sha", "") if isinstance(source, dict) else ""
        if not re.fullmatch(r"[0-9a-f]{40}", str(sha)):
            err(market_path, f"plugin '{name}': external source without a full 40-character "
                "sha; pin it to a reviewed commit")
        continue
    folder = os.path.normpath(os.path.join(ROOT, source))
    manifest = os.path.join(folder, ".claude-plugin", "plugin.json")
    if not os.path.isfile(manifest):
        err(market_path, f"plugin '{name}': {source}/.claude-plugin/plugin.json not found")
        continue
    data = load_json(manifest) or {}
    if data.get("name") != name:
        err(manifest, f"name '{data.get('name')}' does not match marketplace entry '{name}'")
    if not re.fullmatch(r"\d+\.\d+\.\d+([-+][\w.]+)?", str(data.get("version", ""))):
        err(manifest, "version missing or not semver")
    plugins[name] = folder

# 2-3. Skills and agents ---------------------------------------------------------
skills, agents = {}, {}  # plugin -> set of names
for plugin, folder in plugins.items():
    skills[plugin], agents[plugin] = set(), set()
    skills_dir = os.path.join(folder, "skills")
    if os.path.isdir(skills_dir):
        for name in sorted(os.listdir(skills_dir)):
            sdir = os.path.join(skills_dir, name)
            if not os.path.isdir(sdir) or name.startswith("."):
                continue
            skills[plugin].add(name)
            skill = os.path.join(sdir, "SKILL.md")
            if not os.path.isfile(skill):
                err(sdir, "no SKILL.md")
                continue
            fm, problem = frontmatter(skill)
            if problem or fm is None:
                err(skill, problem or "no frontmatter")
                continue
            if fm.get("name") != name:
                err(skill, f"name '{fm.get('name')}' does not match folder '{name}'")
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
                err(skill, "name must be kebab-case, 64 characters max")
            desc = fm.get("description", "")
            if not desc:
                err(skill, "no description")
            elif len(desc) > 1024:
                err(skill, f"description is {len(desc)} characters (max 1024)")
    for path in walk_files(os.path.join(folder, "agents"), {".md"}):
        stem = os.path.splitext(os.path.basename(path))[0]
        agents[plugin].add(stem)
        fm, problem = frontmatter(path)
        if problem or fm is None:
            err(path, problem or "no frontmatter")
            continue
        if fm.get("name") != stem:
            err(path, f"name '{fm.get('name')}' does not match file name '{stem}'")
        if not fm.get("description"):
            err(path, "no description")

# 4. Hooks and MCP ---------------------------------------------------------------
ROOT_VAR = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)")
for plugin, folder in plugins.items():
    for cfg in (os.path.join(folder, "hooks", "hooks.json"), os.path.join(folder, ".mcp.json")):
        if not os.path.isfile(cfg):
            continue
        if load_json(cfg) is None:
            continue
        for target in ROOT_VAR.findall(read(cfg)):
            if not os.path.exists(os.path.join(folder, target)):
                err(cfg, f"cites missing file ${{CLAUDE_PLUGIN_ROOT}}/{target}")

# 5. References ------------------------------------------------------------------
CODE_REF = re.compile(r"`([^`\s]+)`")
LINK_REF = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
NAMED_REF = re.compile(r"\b(skills?|agents?)\s+`([a-z][a-z0-9:-]*)`", re.I)
NS_REF = re.compile(r"`([a-z][a-z0-9-]*):([a-z][a-z0-9-]*)`")


def owner(path):
    """Return (plugin, skill folder or None) for a file under plugins/."""
    for plugin, folder in plugins.items():
        if path.startswith(folder + os.sep):
            parts = os.path.relpath(path, folder).split(os.sep)
            if parts[0] == "skills" and len(parts) > 2:
                return plugin, os.path.join(folder, "skills", parts[1])
            return plugin, None
    return None, None


def check_path(path, ref):
    ref = ref.rstrip(".,;:)")
    if re.search(r"[<>*{}$~]|^https?:|^mailto:|^/|^#|\.\.\.$|…", ref):
        return
    plugin, skill = owner(path)
    base = os.path.dirname(path)
    if ref.startswith("../"):
        target = os.path.normpath(os.path.join(base, ref))
        # Only paths whose folder exists in this repository are checked; other
        # ../ paths in templates and examples point into the user's project.
        # Templates are copied into the project, so their ../ paths are project paths.
        if "template" in rel(path):
            return
        if plugin and skill and os.path.isdir(os.path.dirname(target)):
            if not os.path.exists(target):
                err(path, f"cites missing file {ref}")
        return
    if skill and "/" in ref and os.path.isdir(os.path.join(skill, ref.split("/")[0])):
        if not os.path.exists(os.path.join(skill, ref.rstrip("/"))):
            err(path, f"cites missing file {ref}")
        return
    if ref.startswith(("plugins/", "scripts/", ".claude-plugin/")):
        if not os.path.exists(os.path.join(ROOT, ref.rstrip("/"))):
            err(path, f"cites missing file {ref}")


md_files = [p for p in walk_files(ROOT, {".md"})]
for path in md_files:
    text = read(path)
    plugin, skill_dir = owner(path)
    for m in CODE_REF.finditer(text):
        check_path(path, m.group(1))
    for m in LINK_REF.finditer(text):
        target = m.group(1)
        if skill_dir:
            # Links inside a skill may be examples pointing into the user's project.
            check_path(path, target)
        elif not re.match(r"^(https?:|mailto:|#)", target):
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), target))):
                err(path, f"links to missing file {target}")
    for m in NS_REF.finditer(text):
        ns, name = m.groups()
        if ns in plugins and name not in skills[ns] | agents[ns]:
            err(path, f"cites unknown {ns}:{name}")
    for m in NAMED_REF.finditer(text):
        name = m.group(2)
        if ":" in name or name in EXTERNAL:
            continue
        local = (skills.get(plugin, set()) | agents.get(plugin, set())) if plugin else set()
        everywhere = set().union(*skills.values(), *agents.values()) if plugins else set()
        if name not in (local or everywhere):
            err(path, f"cites unknown {m.group(1).lower()} `{name}`"
                + (" (in another plugin: use the plugin:name form)" if name in everywhere else ""))

# 6. Scripts and JSON -------------------------------------------------------------
for path in walk_files(ROOT, {".sh"}):
    with open(path, encoding="utf-8", errors="replace") as f:
        shebang = f.readline()
    shell = "bash" if re.match(r"#!.*\bbash\b", shebang) else "sh"
    result = subprocess.run([shell, "-n", path], capture_output=True, text=True)
    if result.returncode:
        err(path, f"{shell} -n failed: " + (result.stderr.strip().splitlines() or ["?"])[-1])
for path in walk_files(ROOT, {".py"}):
    try:
        compile(read(path), path, "exec")
    except SyntaxError as e:
        err(path, f"does not compile: {e.msg} (line {e.lineno})")
for path in walk_files(ROOT, {".json"}):
    load_json(path)

# 7. Denylist ---------------------------------------------------------------------
deny_path = os.path.join(ROOT, ".denylist.local")
if os.path.isfile(deny_path):
    words = [w.strip() for w in read(deny_path).splitlines() if w.strip() and not w.startswith("#")]
    if words:
        pattern = re.compile("|".join(re.escape(w) for w in words), re.I)
        try:
            tracked = subprocess.run(["git", "-C", ROOT, "ls-files", "-co", "--exclude-standard"],
                                     capture_output=True, text=True, check=True).stdout.split("\n")
        except (OSError, subprocess.CalledProcessError):
            tracked = [rel(p) for p in walk_files(ROOT)]
        for name in filter(None, tracked):
            path = os.path.join(ROOT, name)
            if name == ".denylist.local" or not os.path.isfile(path):
                continue
            try:
                lines = read(path).splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for n, line in enumerate(lines, 1):
                hit = pattern.search(line)
                if hit:
                    err(path, f"line {n}: denylisted term '{hit.group(0)}'")

# Report ------------------------------------------------------------------------
for w in warnings:
    print(f"  ! {w}")
for e in errors:
    print(f"  x {e}")
n_skills = sum(len(s) for s in skills.values())
n_agents = sum(len(a) for a in agents.values())
print(f"\n{len(plugins)} plugins, {n_skills} skills, {n_agents} agents checked: "
      + ("FAIL" if errors else "PASS") + f" ({len(errors)} error(s), {len(warnings)} warning(s))")
sys.exit(1 if errors else 0)
