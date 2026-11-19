---
format: living-specs
version: 1
---

# Specs: PROJECT_NAME

Living-specs format v1, maintained by the `functional-spec` and `screen-spec` skills of the
living-specs Claude Code plugin. A living spec: kept up to date at every working session on the
project. Any element is found by its identifier.

## Product

What the product does, for whom, in three to five sentences. What is out of scope.

## Roles

| Role | Description | Scope |
|---|---|---|
| Role | what it does in the product | "own files", "own team", everything |

## Features

| Feature | Status | Summary | Screens |
|---|---|---|---|
| [Name](features/slug.md) | draft | one sentence | SC-01 |

## Screens

| Screen | Roles | Features | States covered | Screenshot |
|---|---|---|---|---|
| [SC-01 Name](screens/SC-01-slug.md) | Role | slug | nominal, empty, loading, error, no access | [nominal](screens/screenshots/SC-01-nominal.png) |

## Glossary

In [`docs/glossary.md`](../glossary.md), index of the `docs/glossary-<domain>.md` files if it is
split by domain. Its terms are used word for word in every sheet.
