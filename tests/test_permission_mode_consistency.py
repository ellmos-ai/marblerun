"""Regression tests for the canonical Claude permission mode."""

import json
from pathlib import Path

from llmauto.core.config import DEFAULT_GLOBAL_CONFIG
from llmauto.core.runner import ClaudeRunner


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL_PERMISSION_MODE = "dontAsk"


def test_runtime_and_configs_use_canonical_permission_mode():
    config = json.loads((REPO_ROOT / "config.json").read_text(encoding="utf-8"))

    assert ClaudeRunner().permission_mode == CANONICAL_PERMISSION_MODE
    assert (
        DEFAULT_GLOBAL_CONFIG["default_permission_mode"]
        == CANONICAL_PERMISSION_MODE
    )
    assert (
        config["default_permission_mode"]
        == CANONICAL_PERMISSION_MODE
    )


def test_consistency_script_uses_canonical_permission_mode():
    script = (
        REPO_ROOT / "scripts" / "poll_and_start_consistency.sh"
    ).read_text(encoding="utf-8")

    assert (
        f"--permission-mode {CANONICAL_PERMISSION_MODE}" in script
    )
    assert "--permission-mode bypassPermissions" not in script
