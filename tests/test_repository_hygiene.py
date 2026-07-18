"""Repository hygiene checks for local runtime and credential artifacts."""

from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def _git_check_ignore(*paths: str) -> set[str]:
    result = subprocess.run(
        ["git", "check-ignore", *paths],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines()}


def test_local_secret_and_state_artifacts_are_ignored():
    ignored = _git_check_ignore(
        ".env.local",
        ".npmrc",
        ".pypirc",
        "credentials.json",
        "secrets.json",
        "token.json",
        "github_token.txt",
        "passwords.json",
        "npm_recovery_codes.txt",
        "id_ed25519.key",
        "client.pem",
        "certificates/client.p12",
        "state/chain.sqlite3",
        "state/chain.sqlite-wal",
        "runtime.db-shm",
    )

    assert ignored == {
        ".env.local",
        ".npmrc",
        ".pypirc",
        "credentials.json",
        "secrets.json",
        "token.json",
        "github_token.txt",
        "passwords.json",
        "npm_recovery_codes.txt",
        "id_ed25519.key",
        "client.pem",
        "certificates/client.p12",
        "state/chain.sqlite3",
        "state/chain.sqlite-wal",
        "runtime.db-shm",
    }


def test_shareable_env_examples_remain_trackable():
    ignored = _git_check_ignore(".env.example", ".env.sample")

    assert ".env.example" not in ignored
    assert ".env.sample" not in ignored
