#!/bin/sh
# SessionStart hook of the living-specs plugin: inject the project's business glossary
# (docs/glossary*.md) and the rules to maintain it into Claude's context. On an application
# project with no glossary yet, inject only the rules. Silent elsewhere, or if the project
# declined the glossary.

input=$(cat 2>/dev/null)
dir=""
if command -v jq >/dev/null 2>&1; then
  dir=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
fi
[ -n "$dir" ] || dir=$(printf '%s' "$input" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
[ -n "$dir" ] && [ -d "$dir" ] || dir=$PWD
root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || root=$dir

for f in CLAUDE.local.md CLAUDE.md .claude/CLAUDE.md; do
  grep -qiE '^[[:space:]]*glossary:[[:space:]]*declined' "$root/$f" 2>/dev/null && exit 0
done

# Same detection as living-specs.sh: a build or dependency manifest, or an HTML prototype.
is_app() {
  [ -d "$root/.claude-plugin" ] && return 1
  for m in package.json pom.xml build.gradle build.gradle.kts settings.gradle pyproject.toml \
           setup.py requirements.txt go.mod Cargo.toml composer.json Gemfile mix.exs \
           pubspec.yaml deno.json index.html; do
    [ -f "$root/$m" ] && return 0
  done
  for m in "$root"/*.csproj "$root"/*.sln; do
    [ -f "$m" ] && return 0
  done
  return 1
}

rules() {
  cat <<'MSG'
- Use the glossary terms word for word in specs, screens, tickets, code and answers; never a synonym from its "Not to be confused with" column.
- Without asking (glossary skill): each business term defined, clarified or corrected in the exchange is added or corrected. Validated only if the user dictated the definition, or was shown it and accepted it as is; otherwise Proposed. Never invent a definition: an unknown meaning is a question.
- During a grill-me, write the terms at the end.
- End the answer with one line saying what moved, e.g. "Glossary: Fee added (proposed)", only when the glossary changed.
MSG
}

set -- "$root"/docs/glossary*.md
if [ ! -f "$1" ]; then
  is_app || exit 0
  printf 'Business glossary (living-specs plugin): project %s has no docs/glossary.md yet. Create it at the first business term met in the session (glossary skill, section 2), then:\n' "$root"
  rules
  exit 0
fi

printf 'Business glossary (living-specs plugin) of project %s. Apply these rules for the whole session:\n' "$root"
rules
terms=0
for f in "$@"; do
  printf '\n===== %s =====\n' "${f#"$root"/}"
  cat "$f"
  # data rows: table lines minus header and separator
  n=$(grep -c '^|' "$f")
  if [ "$n" -ge 2 ]; then n=$((n - 2)); fi
  terms=$((terms + n))
done
if [ "$terms" -gt 150 ]; then
  printf '\nNote: the glossary has %s terms (over 150). Offer to prune it or split it by domain (glossary skill, section 6).\n' "$terms"
fi
exit 0
