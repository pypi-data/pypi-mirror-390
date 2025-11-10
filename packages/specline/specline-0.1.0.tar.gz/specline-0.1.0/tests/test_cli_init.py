from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_cli(
    tmp_path: Path,
    *cmd: str,
    lang: str | None = None,
    env_extra: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if lang is not None:
        env["LANG"] = lang
    env.setdefault("CODEX_HOME", str(tmp_path / ".codex-home"))
    if env_extra:
        env.update(env_extra)
    src_path = Path(__file__).resolve().parents[1] / "src"
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{src_path}:{existing}" if existing else str(src_path)
    )
    command = [sys.executable, "-m", "spec_line.cli", *cmd]
    return subprocess.run(
        command,
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_palprompt_init_creates_structure(tmp_path: Path) -> None:
    env = {"CODEX_HOME": str(tmp_path / "global-codex")}
    result = run_cli(tmp_path, "init", lang="en_US.UTF-8", env_extra=env)
    assert result.returncode == 0, result.stderr

    state_dir = tmp_path / "specline"
    assert state_dir.exists()
    assert (state_dir / "project.md").exists()
    assert (state_dir / "AGENTS.md").exists()
    assert (state_dir / "specs").is_dir()
    assert (state_dir / "changes").is_dir()
    english_prompt = state_dir / "prompts" / "specline-propose.md"
    concept_prompt = state_dir / "prompts" / "specline-concept.md"
    assert english_prompt.exists()
    assert concept_prompt.exists()

    content = english_prompt.read_text(encoding="utf-8")
    assert "specline-propose (EN)" in content

    codex_prompts = Path(env["CODEX_HOME"]) / "prompts"
    assert (codex_prompts / "specline-propose.md").exists()


def test_palprompt_init_detects_locale_for_prompts(tmp_path: Path) -> None:
    env = {"CODEX_HOME": str(tmp_path / "codex-ja")}
    result = run_cli(tmp_path, "init", lang="ja_JP.UTF-8", env_extra=env)
    assert result.returncode == 0, result.stderr

    prompts_dir = tmp_path / "specline/prompts"
    prompt_path = prompts_dir / "specline-propose.md"
    assert prompt_path.exists()
    assert "specline-propose (JA)" in prompt_path.read_text(encoding="utf-8")

    codex_prompts = Path(env["CODEX_HOME"]) / "prompts"
    assert (codex_prompts / "specline-propose.md").exists()


def test_palprompt_init_migrates_basic_openspec(tmp_path: Path) -> None:
    openspec_dir = tmp_path / "openspec"
    (openspec_dir / "specs/demo").mkdir(parents=True)
    (openspec_dir / "specs/demo/spec.md").write_text("# Demo spec\n", encoding="utf-8")
    (openspec_dir / "AGENTS.md").write_text("Legacy instructions", encoding="utf-8")

    result = run_cli(tmp_path, "init", lang="en_US.UTF-8", env_extra={"CODEX_HOME": str(tmp_path / "codex-migrate")})
    assert result.returncode == 0, result.stderr

    state_dir = tmp_path / "specline"
    assert (state_dir / "AGENTS.md").read_text(encoding="utf-8").startswith("<!-- SPECLINE")
    assert (state_dir / "specs/demo/spec.md").exists()


def test_palprompt_init_copies_prompts_for_assistants(tmp_path: Path) -> None:
    env = {"CODEX_HOME": str(tmp_path / "codex-copies")}
    result = run_cli(tmp_path, "init", lang="en_US.UTF-8", env_extra=env)
    assert result.returncode == 0, result.stderr

    codex_prompts = Path(env["CODEX_HOME"]) / "prompts"
    expected = [
        tmp_path / ".claude/commands/specline/specline-propose.md",
        tmp_path / ".cursor/prompts/specline/specline-propose.md",
        tmp_path / ".github/prompts/specline/specline-propose.md",
        tmp_path / "specline/commands/specline-propose.md",
        codex_prompts / "specline-propose.md",
    ]
    for path in expected:
        assert path.exists(), f"{path} was not created"


def test_palprompt_update_refreshes_prompts(tmp_path: Path) -> None:
    env = {"CODEX_HOME": str(tmp_path / "codex-update")}
    result = run_cli(tmp_path, "init", lang="en_US.UTF-8", env_extra=env)
    assert result.returncode == 0, result.stderr

    prompts_dir = tmp_path / "specline/prompts"
    propose_prompt = prompts_dir / "specline-propose.md"
    propose_prompt.write_text("outdated", encoding="utf-8")

    claude_prompt = tmp_path / ".claude/commands/specline/specline-propose.md"
    claude_prompt.unlink()

    update_result = run_cli(tmp_path, "update", lang="en_US.UTF-8", env_extra=env)
    assert update_result.returncode == 0, update_result.stderr

    refreshed = propose_prompt.read_text(encoding="utf-8")
    assert "specline-propose (EN)" in refreshed
    assert claude_prompt.exists()


def test_palprompt_init_respects_assistant_selection(tmp_path: Path) -> None:
    env = {"CODEX_HOME": str(tmp_path / "codex-only")}
    result = run_cli(
        tmp_path,
        "init",
        "--assistants",
        "codex",
        lang="en_US.UTF-8",
        env_extra=env,
    )
    assert result.returncode == 0, result.stderr

    # Codex prompts created
    codex_prompts = Path(env["CODEX_HOME"]) / "prompts"
    assert (codex_prompts / "specline-archive.md").exists()
    # Other assistants skipped
    assert not (tmp_path / ".claude/commands/specline").exists()
    assert not (tmp_path / ".cursor/prompts/specline").exists()


def test_palprompt_init_updates_root_agents_when_requested(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("legacy instructions", encoding="utf-8")
    env = {"CODEX_HOME": str(tmp_path / "codex-root")}

    result = run_cli(
        tmp_path,
        "init",
        "--assistants",
        "claude",
        "--update-root-agents",
        lang="en_US.UTF-8",
        env_extra=env,
    )
    assert result.returncode == 0, result.stderr

    content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "specline/AGENTS.md" in content
