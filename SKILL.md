---
name: timesheet
description: Generate a weekly work summary from git history across all your repositories, with hour estimates derived from commit timestamps. Use when the user asks for a timesheet, hours worked, a weekly summary, or triggers /timesheet.
---

# Timesheet — Weekly Work Summary

Generates a summary of work done during the current week (or specified period) by reading git logs across all repos.

## Parameters

| Parameter | Default | Description |
|---|---|---|
| `{since}` | `last monday` | Start date (git log format) |
| `{until}` | `now` | End date |
| `{author}` | Auto-detected from `git config user.name` | Filter by author |

## Execution

1. Detect author name: `git config user.name`
2. For each repo, run:
   ```bash
   git log --since="{since}" --until="{until}" --author="{author}" --format="%aI|%s" --date=short
   ```
   Use ISO timestamps (`%aI`) to calculate time spans between commits.
3. Repos to scan, resolved in this order:
   1. `data/repos.json` in the skill directory, if present (explicit list — always wins);
   2. otherwise every directory containing a `.git` entry directly under `$SKILLS_REPOS_ROOT`;
   3. otherwise the current working directory, if it is a git repository.
   If none of the three resolves, report `timesheet: no repositories configured — see SETUP.md` and stop. There is no built-in default path.

   See `SETUP.md` for `data/repos.json` format and how to override.
4. Parse ticket IDs from commit subjects using `ticket_pattern` from `data/repos.json` (default `[A-Z][A-Z0-9]+-[0-9]+`). Commits with no match are grouped under `—`.
5. *(Optional)* Enrich each ticket ID with its title if an issue-tracker MCP server is available in the session (Jira, Linear, GitHub Issues, …). Probe once; if no such server is configured or the lookup fails, continue with the bare ticket ID and note `titles unavailable` in the report — never block the timesheet on the tracker.
6. Group by day, then by ticket/component

## Time Estimation

Estimate hours spent per activity using commit timestamps:

1. **Sort all commits chronologically per day** (across all repos)
2. **Calculate gaps:** time between consecutive commits on the same day
3. **Rules:**
   - Gap < 2h between commits → count as continuous work
   - Gap > 2h → assume break, start new work block
   - First commit of the day: assume 30min of setup/context before it
   - Single commit day with no other data: estimate 1h
   - Multiple commits on same ticket within 30min: count as single block
4. **Round to nearest 0.5h** per activity block
5. **Cap at 8h per day** — if estimates exceed, normalize proportionally

This is an approximation. Present estimates with a disclaimer and let the user adjust.

## Output Format

```markdown
## Week: {start_date} — {end_date}

### Monday (YYYY-MM-DD) — ~6.5h estimated
| Time Block | Ticket | Component | Description | Est. Hours |
|---|---|---|---|---|
| 09:15–11:45 | TICKET-482 | api-service | Order state machine fix | 2.5h |
| 13:30–16:00 | TICKET-482 | e2e-tests | End-to-end coverage for the order fix | 2.5h |
| 16:15–17:45 | — | infra-tools | Tooling maintenance | 1.5h |

### Tuesday (YYYY-MM-DD) — ~4h estimated
| ...

### Weekly Summary
| Ticket | Description | Components | Total Hours | Days |
|---|---|---|---|---|
| TICKET-482 | Order state machine | api-service, e2e-tests | 8.0h | Mon, Tue |
| — | Internal tooling | infra-tools | 3.5h | Mon, Thu |
| **Total** | | | **18.5h** | |
```

Present the output and ask: "Want me to adjust any estimates or save to a file?"

## Caveats

- The estimate is derived from commit cadence and systematically under-counts work that produced no commit (code review, meetings, debugging without a resulting commit).
- It caps at 8h per day by design, which can compress a genuinely longer day into an understated total.
- Always review the numbers before submitting the report as an official timesheet.
