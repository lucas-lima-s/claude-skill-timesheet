# Setup — timesheet

## What it needs

| Item | Notes |
|---|---|
| Git | Author is auto-detected via `git config user.name` in each scanned repo |
| *(Optional)* Issue-tracker MCP server | Used only to enrich parsed ticket IDs with their title (Jira, Linear, GitHub Issues, …) |

No Python is required to run the skill itself; the `tests/` suite in this repository only validates repository hygiene, it is not a runtime dependency of `/timesheet`.

## Configuring which repositories are scanned

Repos are resolved in this order:

1. `data/repos.json` in the skill directory, if present — an explicit list, and it always wins.
2. Otherwise every immediate child directory of `$SKILLS_REPOS_ROOT` that contains a `.git` entry.
3. Otherwise the current working directory, if it is itself a git repository.

If none of the three resolves, the skill reports `timesheet: no repositories configured — see SETUP.md` and stops instead of guessing a path.

### Option A — `SKILLS_REPOS_ROOT`

Set it in the `env` block of `~/.claude/settings.json` to the parent folder that holds your checkouts. The skill enumerates every immediate child containing `.git`:

```json
{
  "env": {
    "SKILLS_REPOS_ROOT": "<path-to-your-repos-root>"
  }
}
```

### Option B — explicit list in `data/repos.json`

```bash
cp data/repos.json.example data/repos.json
```

Then edit it:

| Key | Meaning |
|---|---|
| `repos` | List of repository paths to scan, `~/`-relative |
| `ticket_pattern` | Regex used to pull a ticket ID out of a commit subject |
| `author` | Override the auto-detected author name; `null` keeps auto-detection |
| `day_cap_hours` | Maximum hours attributed to a single day |
| `break_gap_hours` | Gap between commits, in hours, treated as a break rather than continuous work |

**Precedence:** `data/repos.json` wins over `SKILLS_REPOS_ROOT`, which wins over the current directory.

## Optional ticket titles

If a Jira, Linear, or GitHub Issues MCP server is connected in the session, the skill looks up each parsed ticket ID once and adds its title to the report. With no such server configured, or if the lookup fails, it degrades to the bare ticket ID and notes `titles unavailable`. This skill never reads credentials from disk itself — any tracker access goes through whatever MCP server the session already has configured.

## Validation

```bash
/timesheet
```

The first line of the output is the week heading, `## Week: {start_date} — {end_date}`.

If you see `not a git repository`, one of the configured paths is stale: check the entries in `data/repos.json`, or confirm `SKILLS_REPOS_ROOT` points at a folder that actually contains checkouts.

## Hour estimation

The reported hours are an approximation derived from commit timestamps, not a measurement of actual time worked — see the `## Time Estimation` and `## Caveats` sections in `SKILL.md` for the exact rules and their limits. Always review the numbers before treating them as an official timesheet.

## `[tool.black]` note

`pyproject.toml` carries a `[tool.black]` section purely so external tooling that only reads Black's config agrees with ruff's line length; ruff is this repository's actual lint and format tool, there is no Black invocation anywhere in CI or in the dev dependencies.
