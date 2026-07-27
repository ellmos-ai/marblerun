"""
llmauto.core.runner -- Multi-Provider CLI Wrapper
=================================================
Zentraler Baustein: Startet Claude direkt und weitere Provider über COMA.
Handhabt Environment, Fallback, Timeout, Output-Capture.
"""
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime


class ClaudeRunner:
    """Wrapper um die Claude CLI fuer automatisierte Aufrufe."""

    def __init__(self, model="claude-sonnet-4-6", fallback_model=None,
                 permission_mode="dontAsk", allowed_tools=None, timeout=7200,
                 cwd=None):
        self.model = model
        self.fallback_model = fallback_model
        self.permission_mode = permission_mode
        self.allowed_tools = allowed_tools or ["Read", "Edit", "Write", "Bash", "Glob", "Grep"]
        self.timeout = timeout
        self.cwd = cwd

    def _build_env(self):
        """Environment vorbereiten: CLAUDECODE entfernen, Encoding setzen."""
        env = os.environ.copy()
        env.pop("CLAUDECODE", None)
        env["PYTHONIOENCODING"] = "utf-8"
        return env

    def _build_cmd(self, prompt, **overrides):
        """Claude CLI Kommando zusammenbauen."""
        model = overrides.get("model", self.model)
        continue_conv = overrides.get("continue_conversation", False)

        cmd = ["claude"]
        if continue_conv:
            cmd.append("--continue")
        cmd.extend([
            "--model", model,
            "-p", prompt,
            "--permission-mode", self.permission_mode,
            "--allowedTools", ",".join(self.allowed_tools),
        ])
        fallback = overrides.get("fallback_model", self.fallback_model)
        if fallback:
            cmd.extend(["--fallback-model", fallback])
        return cmd

    def run(self, prompt, **overrides):
        """
        Fuehrt einen Claude-Aufruf aus.

        Returns:
            dict mit keys: success, output, stderr, returncode, duration_s
        """
        cmd = self._build_cmd(prompt, **overrides)
        env = self._build_env()
        cwd = overrides.get("cwd", self.cwd)
        timeout = overrides.get("timeout", self.timeout)

        start = datetime.now()
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                cwd=str(cwd) if cwd else None
            )
            duration = (datetime.now() - start).total_seconds()
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "stderr": result.stderr.strip() if result.stderr else "",
                "returncode": result.returncode,
                "duration_s": duration,
                "model": overrides.get("model", self.model),
            }

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start).total_seconds()
            return {
                "success": False,
                "output": "",
                "stderr": f"TIMEOUT nach {timeout}s",
                "returncode": -1,
                "duration_s": duration,
                "model": overrides.get("model", self.model),
            }

        except FileNotFoundError:
            return {
                "success": False,
                "output": "",
                "stderr": "claude CLI nicht gefunden. Ist Claude Code installiert?",
                "returncode": -2,
                "duration_s": 0,
                "model": overrides.get("model", self.model),
            }

        except Exception as e:
            duration = (datetime.now() - start).total_seconds()
            return {
                "success": False,
                "output": "",
                "stderr": str(e),
                "returncode": -3,
                "duration_s": duration,
                "model": overrides.get("model", self.model),
            }

    def pipe(self, prompt, **overrides):
        """Kurzform: Prompt rein, Text raus. Wirft Exception bei Fehler."""
        result = self.run(prompt, **overrides)
        if not result["success"]:
            raise RuntimeError(f"Claude Fehler (rc={result['returncode']}): {result['stderr']}")
        return result["output"]


class ProviderRunner:
    """Einheitlicher Runner für Codex, Agy und Kimi über COMA.

    COMA bleibt die einzige Stelle, die provider-spezifische CLI-Flags kennt.
    MarbleRun kümmert sich weiterhin nur um Ketten, Handoffs und Wiederholungen.
    """

    def __init__(
        self,
        backend,
        model=None,
        timeout=7200,
        cwd=None,
        allow_unverified=False,
        **options,
    ):
        if backend == "claude":
            raise ValueError("Für claude ClaudeRunner oder build_runner verwenden")
        try:
            from coma import Spawner
            from coma.adapters import get_adapter
        except ImportError as error:
            raise RuntimeError(
                "Backend benötigt COMA. Installiere die MarbleRun-Option "
                "'providers' oder coma aus https://github.com/dev-bricks/coma."
            ) from error

        adapter_options = {"timeout": timeout, "cwd": cwd}
        if model:
            adapter_options["model"] = model
        if backend == "codex":
            adapter_options["write"] = bool(options.pop("write", True))
            effort = options.pop("effort", None)
            if effort:
                adapter_options["effort"] = effort
        elif backend == "agy" and cwd:
            adapter_options["add_dirs"] = options.pop("add_dirs", [cwd])
        adapter_options.update(options)

        self.backend = backend
        self.model = model or ""
        self.timeout = timeout
        self.cwd = cwd
        self.adapter = get_adapter(backend, **adapter_options)
        self.spawner = Spawner(
            self.adapter, allow_unverified=bool(allow_unverified)
        )

    def run(self, prompt, **overrides):
        return self.spawner.run(prompt, **overrides)

    def pipe(self, prompt, **overrides):
        return self.spawner.pipe(prompt, **overrides)


def build_runner(
    backend="claude",
    *,
    model=None,
    fallback_model=None,
    permission_mode="dontAsk",
    allowed_tools=None,
    timeout=7200,
    cwd=None,
    allow_unverified=False,
    **options,
):
    """Runner-Fabrik; bestehende Claude-Konfiguration bleibt kompatibel."""
    backend = (backend or "claude").lower()
    if backend == "claude":
        return ClaudeRunner(
            model=model or "claude-sonnet-4-6",
            fallback_model=fallback_model,
            permission_mode=permission_mode,
            allowed_tools=allowed_tools,
            timeout=timeout,
            cwd=cwd,
        )
    return ProviderRunner(
        backend,
        model=model,
        timeout=timeout,
        cwd=cwd,
        allow_unverified=allow_unverified,
        **options,
    )
