# v9 — Motivation and OpenCode

Added the owner-approved personal introduction and an optional OpenCode/LM Studio Development worker section. Added version-scoped analysis configuration, trial checklist and manual worker-selection policy. Original six diagrams retained. No live runtime change.

# v8 — User-supplied overview diagram

Replaced only the article overview figure with Hermes_Fig_Overview.png supplied by the owner. Other diagrams, article text, and runtime configuration are unchanged.

# v7 — practical model combinations

Adds concrete idea, feature, bug, article, video, daily planning and provider-failure
examples, with explicit handoffs and configured versus planned capabilities.
Original-style diagrams and runtime configurations are unchanged.

# v6 — original visual style restored

Restores rounded workflow cards, colored numbered steps and pill labels, while
retaining the v5 architecture and configuration corrections. Adds an editable SVG
renderer for the original style without Chromium; updates the standalone article.

# Changelog

What changed in the setup, newest first. When a dashed step in a diagram goes live, note it here and flip its `status` in `diagrams/departments.yaml`.

## 2026-10-02 revision 5

- Clarified task-centered coordination with specialist execution and multiple boards.
- Corrected starter-kit scope: manual examples, no bundled installer or runtime router.
- Separated capability status from approval requirements and made stage labels explicit.
- Added task, handoff, approval and documented stage-policy templates.
- Strengthened spec/repository readiness, one-writer and separate-review instructions.
- Made approvals artifact-specific and invalidated by revision or destination changes.
- Moved default dispatcher pause before board creation; preserve existing env settings.
- Removed screenshot and version placeholders; recorded inspected source and check limits.
- Regenerated article and diagrams from the revised sources.

## 2026-10-02 original configuration

- Work is assigned by task instead of role. Added the roles vs. tasks figure.
- Rebuilt the setup around departments. The 4 role profiles (planner, developer, QA, reviewer) were exported and removed.
- Development, Writing, and Media profiles configured. Development runs on Codex with a local Qwen fallback. Writing and Media run on local Qwen.
- Dream Department instructions and configuration prepared for manual setup. The `#ideas` channel exists. Not live yet.
- Discord `#tennis` routes to Development through one shared bot. A read-only board check returned all 5 Tennis cards.
- Local model passed a small simulated tool-call check. End-to-end failover not tested yet.
- Not connected yet: Claude Code and Codex workers through Orca, video tools, publishing.
