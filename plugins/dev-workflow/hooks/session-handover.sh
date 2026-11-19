#!/bin/sh
# SessionStart hook: inject HANDOVER.md from the working directory into
# Claude's context, with the instructions to resume from it and keep it
# current. No HANDOVER.md: no output.
input=$(cat 2>/dev/null)
dir=""
if command -v jq >/dev/null 2>&1; then
  dir=$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)
fi
if [ -z "$dir" ]; then
  # Fallback without jq: plain "cwd":"..." value (no escaped quotes).
  dir=$(printf '%s' "$input" | sed -n 's/.*"cwd"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
fi
[ -n "$dir" ] || dir=$PWD
file="$dir/HANDOVER.md"
[ -f "$file" ] || exit 0

printf 'HANDOVER.md found in %s. Resume from it and briefly say what you pick up.\n\n' "$dir"
cat <<'EOF'
Session handover rules (dev-workflow plugin):
- Keep HANDOVER.md current at all times, not only at the end: after each finished task, after each important decision, and before a long or risky operation. Use the handover skill for its format.
- HANDOVER.md is a local working file: never commit it, and make sure git ignores it (add it to .gitignore, or to .git/info/exclude when nothing may be written in the repo).
EOF
if command -v git >/dev/null 2>&1 \
  && git -C "$dir" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  && ! git -C "$dir" check-ignore -q HANDOVER.md 2>/dev/null; then
  printf -- '- Warning: HANDOVER.md is not ignored by git in this repository yet.\n'
fi
printf '\n--- HANDOVER.md ---\n\n'
cat "$file"
exit 0
