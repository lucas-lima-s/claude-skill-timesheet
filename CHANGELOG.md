# Changelog

## [Unreleased]

- Commits are read from every local and remote-tracking branch (`--branches --remotes`) and deduplicated by hash, so unmerged ticket branches count once.
- Linked worktrees are skipped during discovery and initialized submodules are scanned.
- `author`, `day_cap_hours` and `break_gap_hours` from `data/repos.json` are now read; the author defaults to each repo's `user.email`.
- Gap boundaries are explicit (`<=` continuous, `>` break) and the overlapping 30-minute rule was folded into the per-ticket row rule.
- The summary template is in Brazilian Portuguese, uses `sem ticket` instead of a dash, and tracker titles are treated as data.
- SETUP documents `SKILLS_REPOS_ROOT` as a plain environment variable for any agent.

## [1.0.0] - 2026-08-25

- Initial public release.
- Configurable repository discovery: explicit `data/repos.json` list, `SKILLS_REPOS_ROOT` enumeration, or current-directory fallback.
- Vendor-neutral optional ticket enrichment via any issue-tracker MCP server available in the session.
