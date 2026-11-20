# Shared by the living-specs SessionStart hooks (living-specs.sh, glossary.sh): sourced, not run.

# Set $root from the hook payload on stdin: git root of the session cwd, else the cwd, else $PWD.
read_root() {
  input=$(cat 2>/dev/null)
  dir=""
  if command -v jq >/dev/null 2>&1; then
    dir=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
  fi
  if [ -z "$dir" ]; then
    # Without jq: the "cwd" string value, with \" \\ \/ escapes decoded.
    dir=$(printf '%s' "$input" \
      | sed -nE 's/.*"cwd"[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p' | head -n 1 \
      | sed -E 's/\\(["\\/])/\1/g')
  fi
  [ -n "$dir" ] && [ -d "$dir" ] || dir=$PWD
  root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || root=$dir
}

# Succeed when the project opted out with "<key>: declined" in one of its CLAUDE files.
declined() {
  for f in CLAUDE.local.md CLAUDE.md .claude/CLAUDE.md; do
    grep -qiE "^[[:space:]]*$1:[[:space:]]*declined" "$root/$f" 2>/dev/null && return 0
  done
  return 1
}

# A project looks like an application when it has a build or dependency manifest, or an HTML
# prototype at its root. Plugin and tooling repositories are left alone.
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
