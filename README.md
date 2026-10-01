# claude-skill-timesheet

An agent skill (Claude Code, Codex, Gemini/agy, Cursor) that reconstructs a weekly timesheet from git history across every repository you configure, estimating hours from the gaps between commit timestamps.

## Why

Timesheets usually get reconstructed from memory, days after the work happened. The git log already holds the ground truth of when you worked and on what: every commit carries a precise timestamp and a subject line. This skill turns that log into a reviewable table instead of asking you to remember your week.

## How it works

1. **Resolve repositories**: `data/repos.json`, else every clone under `$SKILLS_REPOS_ROOT` (linked worktrees skipped), else the current directory; initialized submodules are added.
2. **Detect the author**: `git config user.email` in each scanned repo, or an explicit `author` in `data/repos.json`.
3. **Collect commits**: `git log --branches --remotes --since --until --author --format="%H|%aI|%s"` per repo, so work on unmerged ticket branches counts, deduplicated by commit hash.
4. **Split into work blocks**: every commit of a day is merged into one timeline and cut wherever the gap between two consecutive commits exceeds the break threshold.
5. **Aggregate**: blocks are grouped by day, then by ticket ID and component, into a weekly summary.

## The estimation heuristic

- A gap up to `break_gap_hours` (default 2h) is continuous work; a longer gap starts a new block.
- Each block gets 30 minutes of assumed setup time before its first commit.
- A day with a single commit is estimated at 1h.
- Consecutive commits on the same ticket inside a block form one row.
- Each row rounds to the nearest 0.5h, and each day caps at `day_cap_hours` (default 8h), scaled proportionally if the raw estimate runs over.

It is only ever an approximation. What it cannot see: any work that produced no commit (code review, meetings, design discussion, debugging that ended in a revert). Always review the numbers before treating them as an official timesheet.

## Install

Clone this repository and link it into your agent's skills directory (for example `~/.claude/skills/timesheet/` or `~/.agents/skills/timesheet/`), then configure which repositories it scans (see below).

## Usage

```
/timesheet
/timesheet since="2 weeks ago"
```

It also triggers on natural-language requests: "generate my timesheet", "how many hours did I work this week", "weekly summary".

## Sample output

The summary is written in Brazilian Portuguese:

```markdown
## Semana: 2026-08-17 a 2026-08-23

### Segunda-feira (2026-08-17): ~6,5h estimadas
| Horário | Ticket | Componente | Descrição | Horas est. |
|---|---|---|---|---|
| 09:15-11:45 | TICKET-482 | api-service | Correção da máquina de estados do pedido | 2,5h |
| 13:30-16:00 | TICKET-482 | e2e-tests | Cobertura de ponta a ponta da correção | 2,5h |
| 16:15-17:45 | sem ticket | infra-tools | Manutenção de ferramentas | 1,5h |

### Resumo da semana
| Ticket | Descrição | Componentes | Total de horas | Dias |
|---|---|---|---|---|
| TICKET-482 | Máquina de estados do pedido | api-service, e2e-tests | 8,0h | seg, ter |
| sem ticket | Ferramentas internas | infra-tools | 3,5h | seg, qui |
| **Total** | | | **18,5h** | |
```

## Configuration

See [`SETUP.md`](SETUP.md) for the full repository-resolution order and the `SKILLS_REPOS_ROOT` environment variable. The explicit-list alternative is `data/repos.json`, copied from [`data/repos.json.example`](data/repos.json.example):

| Key | Meaning |
|---|---|
| `repos` | List of repository paths to scan, `~/`-relative |
| `ticket_pattern` | Regex used to pull a ticket ID out of a commit subject |
| `author` | Override the auto-detected author (name or email); `null` keeps per-repo detection |
| `day_cap_hours` | Maximum hours attributed to a single day (default `8`) |
| `break_gap_hours` | Gap above which work counts as a break (default `2`) |

## License

MIT, see [LICENSE](LICENSE).
