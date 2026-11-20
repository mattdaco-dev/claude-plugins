#!/bin/sh
# SessionStart hook of the living-specs plugin: tell Claude whether the project keeps living
# specs (docs/specs/README.md with "format: living-specs") and, when it does, how to maintain them.
# Silent when the project declined the format, or when it does not look like an application.

. "$(dirname "$0")/lib.sh"
read_root
declined living-specs && exit 0

readme="$root/docs/specs/README.md"

if [ -f "$readme" ] && grep -q '^format:[[:space:]]*living-specs' "$readme"; then
  cat <<MSG
Living specs (living-specs plugin): project $root keeps its functional and screen specs in docs/specs/ (format: living-specs). Apply these rules for the whole session:
- Without asking, each functional decision made in the exchange (rule, edge case, permission, message, calculation, business object) and each screen changed in the prototype update their sheet, following the functional-spec skill (section 4) and the screen-spec skill (section 3). Read docs/specs/README.md and the format.md of functional-spec before writing.
- Statuses: a statement is Validated only if the user dictated it, or was shown it and accepted it as is. A decision settled by the user but worded by Claude is Proposed, shown for acceptance. Anything mentioned without being settled, or recommended by Claude, is a question Q-xxx in docs/specs/questions.md, never a rule. A Validated rule is rewritten only with the user's words; a dropped rule becomes Obsolete, never deleted.
- End the answer with one line saying what moved, e.g. "Specs: BR-12 added (proposed), BR-04 obsolete". No line if nothing moved.
- During a grill-me, write nothing: the spec is formalized in one block at the end (functional-spec section 3).
- On the default branch, offer to create a branch before committing spec changes. Never push.
MSG
elif [ -f "$readme" ] && grep -q '^moved_to:' "$readme"; then
  target=$(sed -n 's/^moved_to:[[:space:]]*//p' "$readme" | head -n 1)
  printf 'Living specs (living-specs plugin): the specs of project %s moved to %s (docs/specs/README.md, moved_to). Do not write specs here.\n' "$root" "$target"
elif [ -d "$root/docs/specs" ]; then
  printf 'Living specs (living-specs plugin): project %s has a docs/specs/ outside the living-specs format. When the session touches functional work (behavior, rules, screens), offer the migration once in the session (functional-spec skill, section 5: migrate, not now, never). After a grill-me on a feature, offer to formalize it with functional-spec.\n' "$root"
elif is_app; then
  printf 'Living specs (living-specs plugin): project %s has no docs/specs/. When the session touches functional work, offer the living-specs format once in the session (functional-spec skill, section 5).\n' "$root"
fi
exit 0
