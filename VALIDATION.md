# Validation record

## Reference-pack validation

- Configuration YAML and Python syntax pass `python3 scripts/check_consistency.py`.
- Checks cover diagram status labels, approval markers, dispatch defaults, local-only fallback policy, route examples and article image references.
- The article has two embedded figures: role/task comparison and complete tool map. The other diagrams remain reference assets.
- Tool-map PNG and SVG were rendered and visually inspected.
- Public configuration examples use placeholders. No bot tokens, private account credentials or project-vault notes are included.

## Observed setup evidence

The owner demonstrated Development board reading and Discovery board reading, idea creation and read-back through Discord. Local inference is configured and Orca Mobile access is reported working. These are observations about the owner’s setup, not a clean-install certification of this repository.

## Remaining work

A fresh installation, end-to-end fallback, idea evaluation and transfer, worker dispatch, complete development verification, research, media production and automated publishing still need separate tests. Obsidian document handoffs are manual; automatic vault access is unverified.

Stage policies and approval templates describe intended operation. This kit contains no executor enforcing them and no automatic stage/model router. The inspected source version is recorded in COMPATIBILITY.md; verify CLI commands and provider support against your installed version.
