# Setup: timesheet

## What it needs

| Item | Notes |
|---|---|
| Git | Author is auto-detected per scanned repo via `git config user.email` (falling back to `user.name`), unless `author` is set in `data/repos.json` |
| *(Optional)* Issue-tracker MCP server | Used only to enrich parsed ticket IDs with their title (Jira, Linear, GitHub Issues) |

No Python is required to run the skill itself; the `tests/` suite in this repository only validates repository hygiene, it is not a runtime dependency of `/timesheet`.

## Configuring which repositories are scanned

Repos are resolved in this order:

1. `data/repos.json` in the skill directory, if present: an explicit list, and it always wins.
2. Otherwise every immediate child directory of `$SKILLS_REPOS_ROOT` whose `.git` is a directory. Linked worktrees (`.git` is a file) are skipped because they share another clone's history.
3. Otherwise the current working directory, if it is itself a git repository.

If none of the three resolves, the skill reports `timesheet: no repositories configured, see SETUP.md` and stops instead of guessing a path.

### Option A: `SKILLS_REPOS_ROOT`

Set `SKILLS_REPOS_ROOT` as an environment variable visible to your agent (Claude Code, Codex, Gemini/agy or Cursor) pointing at the parent folder that holds your checkouts. A user-level environment variable works for every agent:

```powershell
[Environment]::SetEnvironmentVariable("SKILLS_REPOS_ROOT", "<path-to-your-repos-root>", "User")
```

If you manage agent settings from a central configuration repository, define the value there and let it render each agent's settings instead of editing one agent's settings file by hand. Claude Code also accepts the variable in the `env` block of `~/.claude/settings.json`.

### Option B: explicit list in `data/repos.json`

```bash
cp data/repos.json.example data/repos.json
```

Then edit it:

| Key | Meaning |
|---|---|
| `repos` | List of repository paths to scan, `~/`-relative |
| `ticket_pattern` | Regex used to pull a ticket ID out of a commit subject |
| `author` | Override the auto-detected author (name or email, matched by `git log --author`); `null` keeps per-repo detection |
| `day_cap_hours` | Maximum hours attributed to a single day (default `8`) |
| `break_gap_hours` | Gap between commits, in hours, above which work counts as a break (default `2`; a gap exactly equal to it is still continuous) |

**Precedence:** `data/repos.json` wins over `SKILLS_REPOS_ROOT`, which wins over the current directory. Initialized submodules of every resolved repo are scanned too, and commits are read from all local and remote-tracking branches, deduplicated by hash.

## Optional ticket titles

If a Jira, Linear, or GitHub Issues MCP server is connected in the session, the skill looks up each parsed ticket ID once and adds its title to the report. With no such server configured, or if the lookup fails, it degrades to the bare ticket ID and notes `titles unavailable`. This skill never reads credentials from disk itself; any tracker access goes through whatever MCP server the session already has configured.

## Validation

```bash
/timesheet
```

The first line of the output is the week heading, `## Semana: {data_inicio} a {data_fim}`.

If you see `not a git repository`, one of the configured paths is stale: check the entries in `data/repos.json`, or confirm `SKILLS_REPOS_ROOT` points at a folder that actually contains checkouts.

## Hour estimation

The reported hours are an approximation derived from commit timestamps, not a measurement of actual time worked; see the `## Time estimation` and `## Caveats` sections in `SKILL.md` for the exact rules and their limits. Always review the numbers before treating them as an official timesheet.

## `[tool.black]` note

`pyproject.toml` carries a `[tool.black]` section purely so external tooling that only reads Black's config agrees with ruff's line length; ruff is this repository's actual lint and format tool, there is no Black invocation anywhere in CI or in the dev dependencies.
