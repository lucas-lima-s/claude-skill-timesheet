# claude-skill-timesheet

A Claude Code skill that reconstructs a weekly timesheet from git history across every repository you configure, estimating hours from the gaps between commit timestamps.

## Why

Timesheets usually get reconstructed from memory, days after the work happened. The git log already holds the ground truth of when you worked and on what: every commit carries a precise timestamp and a subject line. This skill turns that log into a reviewable table instead of asking you to remember your week.

## How it works

1. **Detect the author** — `git config user.name` in each scanned repo (or an explicit `author` in `data/repos.json`).
2. **Collect commits** — `git log --since --until --author --format="%aI|%s"` run per repo, using ISO timestamps so gaps can be measured precisely.
3. **Split into work blocks** — every commit from every repo on a given day is merged into one timeline and sorted, then cut into blocks wherever the gap between two consecutive commits crosses the break threshold.
4. **Aggregate** — blocks are grouped first by day, then by ticket ID and component, into a weekly summary.

## The estimation heuristic

- Gaps under 2h between commits count as continuous work; a gap over 2h starts a new block (assumed break).
- The first commit of the day gets 30 minutes of assumed setup/context time before it.
- A day with a single commit and no other data is estimated at 1h.
- Commits on the same ticket within 30 minutes collapse into one block.
- Each block rounds to the nearest 0.5h, and each day caps at 8h, normalized proportionally if the raw estimate runs over.

It is only ever an approximation. What it cannot see: any work that produced no commit — code review, meetings, design discussion, debugging that ended in a revert. Always review the numbers before treating them as an official timesheet.

## Install

Copy this skill's contents into `~/.claude/skills/timesheet/`, then configure which repositories it scans (see below).

## Usage

```
/timesheet
/timesheet since="2 weeks ago"
```

It also triggers on natural-language requests: "generate my timesheet", "how many hours did I work this week", "weekly summary".

## Sample output

```markdown
## Week: 2026-08-17 — 2026-08-23

### Monday (2026-08-17) — ~6.5h estimated
| Time Block | Ticket | Component | Description | Est. Hours |
|---|---|---|---|---|
| 09:15–11:45 | TICKET-482 | api-service | Order state machine fix | 2.5h |
| 13:30–16:00 | TICKET-482 | e2e-tests | End-to-end coverage for the order fix | 2.5h |
| 16:15–17:45 | — | infra-tools | Tooling maintenance | 1.5h |

### Weekly Summary
| Ticket | Description | Components | Total Hours | Days |
|---|---|---|---|---|
| TICKET-482 | Order state machine | api-service, e2e-tests | 8.0h | Mon, Tue |
| — | Internal tooling | infra-tools | 3.5h | Mon, Thu |
| **Total** | | | **18.5h** | |
```

## Configuration

See [`SETUP.md`](SETUP.md) for the full repository-resolution order and the `SKILLS_REPOS_ROOT` environment variable. The explicit-list alternative is `data/repos.json`, copied from [`data/repos.json.example`](data/repos.json.example):

| Key | Meaning |
|---|---|
| `repos` | List of repository paths to scan, `~/`-relative |
| `ticket_pattern` | Regex used to pull a ticket ID out of a commit subject |
| `author` | Override the auto-detected author name; `null` keeps auto-detection |
| `day_cap_hours` | Maximum hours attributed to a single day |
| `break_gap_hours` | Gap between commits, in hours, treated as a break rather than continuous work |

## License

MIT — see [LICENSE](LICENSE).
