"""Tests fuer llmauto.core.runner -- ClaudeRunner."""
import pytest
from llmauto.core.runner import ClaudeRunner, ProviderRunner, build_runner


class TestClaudeRunnerInit:
    def test_default_model(self):
        runner = ClaudeRunner()
        assert "claude-sonnet-4-6" in runner.model

    def test_custom_model(self):
        runner = ClaudeRunner(model="claude-opus-4-6")
        assert runner.model == "claude-opus-4-6"

    def test_default_tools(self):
        runner = ClaudeRunner()
        assert "Read" in runner.allowed_tools
        assert "Bash" in runner.allowed_tools

    def test_custom_tools(self):
        tools = ["Read", "Write"]
        runner = ClaudeRunner(allowed_tools=tools)
        assert runner.allowed_tools == tools

    def test_timeout(self):
        runner = ClaudeRunner(timeout=3600)
        assert runner.timeout == 3600


class TestBuildCmd:
    def test_basic_command(self):
        runner = ClaudeRunner(model="claude-sonnet-4-6")
        cmd = runner._build_cmd("Hallo Welt")
        assert "claude" in cmd
        assert "--model" in cmd
        assert "claude-sonnet-4-6" in cmd
        assert "-p" in cmd
        assert "Hallo Welt" in cmd

    def test_continue_flag(self):
        runner = ClaudeRunner()
        cmd = runner._build_cmd("Test", continue_conversation=True)
        assert "--continue" in cmd

    def test_no_continue_by_default(self):
        runner = ClaudeRunner()
        cmd = runner._build_cmd("Test")
        assert "--continue" not in cmd

    def test_fallback_model(self):
        runner = ClaudeRunner(fallback_model="claude-sonnet-4-6")
        cmd = runner._build_cmd("Test")
        assert "--fallback-model" in cmd

    def test_permission_mode(self):
        runner = ClaudeRunner(permission_mode="dontAsk")
        cmd = runner._build_cmd("Test")
        assert "--permission-mode" in cmd
        assert "dontAsk" in cmd


class TestBuildEnv:
    def test_removes_claudecode(self):
        import os
        os.environ["CLAUDECODE"] = "test"
        try:
            runner = ClaudeRunner()
            env = runner._build_env()
            assert "CLAUDECODE" not in env
        finally:
            os.environ.pop("CLAUDECODE", None)

    def test_sets_encoding(self):
        runner = ClaudeRunner()
        env = runner._build_env()
        assert env.get("PYTHONIOENCODING") == "utf-8"

    def test_merges_chain_environment_without_restoring_claudecode(self):
        runner = ClaudeRunner(env={"MARBLERUN_EVIDENCE_ROOT": "evidence", "CLAUDECODE": "nested"})
        env = runner._build_env()
        assert env["MARBLERUN_EVIDENCE_ROOT"] == "evidence"
        assert env["PYTHONIOENCODING"] == "utf-8"
        assert "CLAUDECODE" not in env


class TestProviderRunner:
    def test_factory_keeps_claude_compatible(self):
        assert isinstance(build_runner("claude"), ClaudeRunner)

    def test_codex_uses_coma_and_workspace_write(self):
        try:
            from coma import Spawner  # noqa: F401
        except (ImportError, RuntimeError):
            pytest.skip("coma.Spawner not available")
        runner = build_runner(
            "codex", model="gpt-test", effort="high", cwd=r"C:\projekt"
        )
        assert isinstance(runner, ProviderRunner)
        cmd = runner.adapter.build_cmd("Hallo")
        assert "exec" in cmd
        assert cmd[cmd.index("--sandbox") + 1] == "workspace-write"
        assert cmd[cmd.index("--model") + 1] == "gpt-test"

    def test_agy_gets_chain_workspace(self):
        try:
            from coma import Spawner  # noqa: F401
        except (ImportError, RuntimeError):
            pytest.skip("coma.Spawner not available")
        runner = build_runner("agy", cwd=r"C:\projekt")
        cmd = runner.adapter.build_cmd("Hallo")
        assert cmd[cmd.index("--add-dir") + 1] == r"C:\projekt"

    def test_kimi_stays_guarded_without_explicit_opt_in(self):
        try:
            from coma import Spawner  # noqa: F401
        except (ImportError, RuntimeError):
            pytest.skip("coma.Spawner not available")
        runner = build_runner("kimi")
        assert runner.spawner.allow_unverified is False

