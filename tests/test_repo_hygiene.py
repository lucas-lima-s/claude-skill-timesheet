from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}

HOME_PATH_PATTERN = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+")
HOME_PATH_ALLOWLIST = (
    "$HOME",
    "$USERPROFILE",
    "%USERPROFILE%",
    "$env:USERPROFILE",
    "$TEMP",
    "%TEMP%",
    "$SKILLS_",
)
SECRET_PATTERN = re.compile(
    r"sk-[A-Za-z0-9]{16,}"
    r"|ghp_[A-Za-z0-9]{20,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|xox[baprs]-"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
)
UUID_PATTERN = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    r"|\b[0-9a-fA-F]{32}\b"
)


def _is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            return b"\0" in handle.read(8192)
    except OSError:
        return True


def walk():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if _is_binary(path):
            continue
        yield path


def test_no_absolute_user_home_paths():
    offenders = []
    for path in walk():
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if not HOME_PATH_PATTERN.search(line):
                continue
            if any(token.lower() in line.lower() for token in HOME_PATH_ALLOWLIST):
                continue
            offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}: {line.strip()}")
    assert not offenders, "hardcoded user-home path(s) found:\n" + "\n".join(offenders)


def test_no_secret_shapes():
    offenders = []
    for path in walk():
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if SECRET_PATTERN.search(line):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}")
    assert not offenders, "secret-shaped token(s) found:\n" + "\n".join(offenders)


def test_no_bare_uuids_outside_examples():
    offenders = []
    for path in walk():
        if path.name.endswith(".example"):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if UUID_PATTERN.search(line):
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{lineno}")
    assert not offenders, "bare UUID/hex token(s) found outside *.example:\n" + "\n".join(offenders)


def test_no_env_or_local_state_committed():
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        import pytest

        pytest.skip("git is unavailable")
        return
    tracked = set(result.stdout.splitlines())
    for forbidden in (".env", "data/repos.json"):
        assert forbidden not in tracked, f"{forbidden} must not be tracked"
    assert "data/repos.json.example" in tracked


def test_skill_md_frontmatter():
    lines = (REPO_ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "---"
    closing = lines.index("---", 1)
    frontmatter = lines[1:closing]
    values = {}
    for line in frontmatter:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        values[key.strip()] = value.strip()
    assert values.get("name")
    assert values.get("description")


def test_baseline_files_present():
    for name in ("README.md", "LICENSE", "SETUP.md", ".gitignore", ".gitattributes", "CHANGELOG.md"):
        assert (REPO_ROOT / name).exists(), f"missing baseline file: {name}"
    assert not (REPO_ROOT / "ROADMAP.md").exists()
