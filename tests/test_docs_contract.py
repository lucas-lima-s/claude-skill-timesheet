from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_CONFIG_KEYS = {"repos", "ticket_pattern", "author", "day_cap_hours", "break_gap_hours"}


def _load_example_config() -> dict:
    return json.loads((REPO_ROOT / "data" / "repos.json.example").read_text(encoding="utf-8"))


def _skill_md_text() -> str:
    return (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8")


def _output_format_block() -> str:
    text = _skill_md_text()
    match = re.search(r"## Output Format\s*```markdown(.*?)```", text, re.DOTALL)
    assert match, "SKILL.md must contain a fenced ## Output Format block"
    return match.group(1)


def test_example_config_is_valid_json_with_expected_keys():
    cfg = _load_example_config()
    assert set(cfg) == EXAMPLE_CONFIG_KEYS
    assert cfg["repos"], "repos must be a non-empty list"
    assert all(entry.startswith("~/") for entry in cfg["repos"])


def test_ticket_pattern_compiles_and_matches_placeholder():
    cfg = _load_example_config()
    pattern = re.compile(cfg["ticket_pattern"])
    assert pattern.search("TICKET-482")
    assert not pattern.fullmatch("lowercase-1")


def test_skill_md_declares_the_resolution_order():
    text = _skill_md_text()
    assert "data/repos.json" in text
    assert "SKILLS_REPOS_ROOT" in text
    assert "no repositories configured" in text


def test_sample_output_uses_generic_names():
    block = _output_format_block()
    allowed_components = {"api-service", "web-client", "e2e-tests", "infra-tools"}
    ticket_pattern = re.compile(r"^TICKET-\d+$")

    current_table = None
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Time Block"):
            current_table = "day"
            continue
        if stripped.startswith("| Ticket | Description"):
            current_table = "summary"
            continue
        if not stripped.startswith("|") or current_table is None:
            continue
        if set(stripped.replace("|", "").strip()) <= {"-"}:
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]

        if current_table == "day":
            if len(cells) < 3:
                continue
            ticket, component = cells[1], cells[2]
        else:
            if cells[0].startswith("**Total**") or len(cells) < 3:
                continue
            ticket, component = cells[0], cells[2]

        assert ticket == "—" or ticket_pattern.match(ticket), f"unexpected ticket token: {ticket!r}"
        for token in (part.strip() for part in component.split(",")):
            assert token in allowed_components, f"unexpected component token: {token!r}"


def test_jira_step_is_optional():
    text = _skill_md_text()
    for line in text.splitlines():
        if "issue-tracker MCP server" in line or "tracker" in line.lower():
            if "Optional" in line:
                assert "never block" in line
                return
    raise AssertionError("no optional, never-blocking tracker-enrichment line found in SKILL.md")
