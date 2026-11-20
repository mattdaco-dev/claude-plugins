# claude-plugins

A Claude Code plugin marketplace with three plugins I use every day on application projects, plus
a small interface mod.

| Plugin | What it does |
|---|---|
| [`living-specs`](plugins/living-specs) | Grill a feature until it is settled, then write and maintain functional specs, screen specs, a business glossary and tickets that stay in sync with the project. |
| [`code-audits`](plugins/code-audits) | Security, performance, maintainability, GDPR and SEO audits with dated, prioritised reports; quarterly maintenance passes; legacy takeover; C4 architecture diagrams. |
| [`dev-workflow`](plugins/dev-workflow) | Session handover file, architecture decision records, role-named subagents and a configurable git guard. |
| [`quiet-diffs`](https://github.com/mattdaco-dev/claude-quiet-diffs) (mod) | Collapse file-edit diffs to one line. Lives in its own repository, listed here for convenience and pinned to a reviewed commit: a new version reaches you only once its commit is bumped here. |

## Install

```
/plugin marketplace add mattdaco-dev/claude-plugins
/plugin install living-specs@mattdaco
/plugin install code-audits@mattdaco
/plugin install dev-workflow@mattdaco
```

Each plugin works on its own. When two are installed together, they refer to each other: for
example, `code-audits:security-audit` checks the abuse controls promised in the specs written by
`living-specs`.

## Acknowledgments

- `living-specs:grill-me` started from the `grill-me` skill in
  [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock (MIT, see
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- The abuse and limits grid in `living-specs` is adapted from
  [geoffreycrofte/saas-launch-skillset](https://github.com/geoffreycrofte/saas-launch-skillset) by
  Geoffrey Crofte (CC BY 4.0, see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
- The repository checks (`scripts/validate.py`, `scripts/typo-lint.py`) were inspired by the
  `validate.sh` and `typography-lint.sh` scripts of the same saas-launch-skillset repository.
  Thanks to Geoffrey Crofte for publishing them.

## License

MIT, see [LICENSE](LICENSE). Third-party material keeps its own license, listed in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
