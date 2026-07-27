#!/usr/bin/env python3
"""
llmauto -- LLM Automatisierung
================================
Universelles Automatisierungstool fuer LLM-Agenten.
Ketten-Ausfuehrung, Einzelaufrufe, Prompt-Management.

Verwendung (aus system/tools/ heraus):
    python -m llmauto chain start <name>         Kette starten
    python -m llmauto chain start <name> --bg    Im Hintergrund
    python -m llmauto chain list                 Alle Ketten anzeigen
    python -m llmauto chain status [name]        Status anzeigen
    python -m llmauto chain stop <name> [grund]  Kette stoppen
    python -m llmauto chain pause <name> [grund] Kette an Checkpoint pausieren
    python -m llmauto chain resume <name>        Pause aufheben
    python -m llmauto chain steer <name> <text>  Operator-Hinweis vormerken
    python -m llmauto chain log <name> [N]       Log anzeigen
    python -m llmauto chain reset <name>         State zuruecksetzen
    python -m llmauto chain create               Neue Kette interaktiv anlegen

    python -m llmauto pipe "prompt"              Einzelner Claude-Aufruf
    python -m llmauto pipe -f prompt.txt         Prompt aus Datei

    python -m llmauto status                     Globaler Status
    python -m llmauto version                    Version anzeigen
"""
import argparse
import importlib.util
import sys
from pathlib import Path

# Sicherstellen, dass das Paket importierbar ist, auch als direktes Script
# oder via ``python -m llmauto`` aus dem Repo-Root. Dort verdeckt diese Datei
# wegen des historischen CLI-/Paket-Gleichnamens sonst das gemappte Paket.
PACKAGE_DIR = Path(__file__).resolve().parent


def _ensure_source_package():
    package = sys.modules.get("llmauto")
    if package is not None and hasattr(package, "__path__"):
        return

    spec = importlib.util.spec_from_file_location(
        "llmauto",
        PACKAGE_DIR / "__init__.py",
        submodule_search_locations=[str(PACKAGE_DIR)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"llmauto-Paket kann nicht aus {PACKAGE_DIR} geladen werden")
    package = importlib.util.module_from_spec(spec)
    sys.modules["llmauto"] = package
    spec.loader.exec_module(package)


_ensure_source_package()

from llmauto import __version__ as VERSION  # Single Source: __init__.py


def cmd_chain(args):
    """Chain-Modus Subkommandos."""
    from llmauto.modes.chain import (
        run_chain, show_status, stop_chain, pause_chain, resume_chain,
        steer_chain, show_log, reset_chain
    )
    from llmauto.core.config import list_chains

    action = args.chain_action

    if action == "start":
        if not args.name:
            print("Fehler: Ketten-Name erforderlich.")
            print("Verfuegbar:", ", ".join(list_chains()) or "(keine)")
            return 1
        return run_chain(args.name, background=args.bg)

    elif action == "list":
        chains = list_chains()
        if not chains:
            print("Keine gespeicherten Ketten gefunden.")
            print(f"Ketten-Verzeichnis: {PACKAGE_DIR / 'chains'}")
            return 0
        print("Gespeicherte Ketten:")
        for name in sorted(chains):
            try:
                from llmauto.core.config import load_chain
                config = load_chain(name)
                desc = config.get("description", "")
                links = len(config.get("links", []))
                mode = config.get("mode", "loop")
                print(f"  {name:25s}  {links} Glieder, {mode:8s}  {desc}")
            except Exception:
                print(f"  {name:25s}  (Fehler beim Laden)")
        return 0

    elif action == "status":
        return show_status(args.name)

    elif action == "stop":
        if not args.name:
            print("Fehler: Ketten-Name erforderlich.")
            return 1
        reason = " ".join(args.extra) if args.extra else None
        return stop_chain(args.name, reason)

    elif action == "pause":
        if not args.name:
            print("Fehler: Ketten-Name erforderlich.")
            return 1
        reason = " ".join(args.extra) if args.extra else None
        return pause_chain(args.name, reason)

    elif action == "resume":
        if not args.name:
            print("Fehler: Ketten-Name erforderlich.")
            return 1
        return resume_chain(args.name)

    elif action == "steer":
        if not args.name:
            print("Fehler: Ketten-Name erforderlich.")
            return 1
        if not args.extra:
            print("Fehler: Steering-Nachricht erforderlich.")
            return 1
        return steer_chain(args.name, " ".join(args.extra))

    elif action == "log":
        if not args.name:
            print("Fehler: Ketten-Name erforderlich.")
            return 1
        lines = int(args.extra[0]) if args.extra else 20
        return show_log(args.name, lines)

    elif action == "reset":
        if not args.name:
            print("Fehler: Ketten-Name erforderlich.")
            return 1
        return reset_chain(args.name)

    elif action == "create":
        from llmauto.core.chain_creator import create_chain
        result = create_chain()
        return 0 if result is not None else 1

    else:
        print(f"Unbekannte Chain-Aktion: {action}")
        return 1


def cmd_pipe(args):
    """Pipe-Modus: Einzelner Claude-Aufruf."""
    from llmauto.core.runner import ClaudeRunner
    from llmauto.core.config import load_global_config

    global_config = load_global_config()

    # Prompt ermitteln
    if args.file:
        prompt_path = Path(args.file)
        if not prompt_path.exists():
            print(f"Fehler: Datei nicht gefunden: {args.file}")
            return 1
        prompt = prompt_path.read_text(encoding="utf-8")
    elif args.prompt:
        prompt = " ".join(args.prompt)
    else:
        # Stdin lesen
        if sys.stdin.isatty():
            print("Fehler: Kein Prompt angegeben. Verwende: python -m llmauto pipe \"prompt\" oder -f datei.txt")
            return 1
        prompt = sys.stdin.read()

    if not prompt.strip():
        print("Fehler: Leerer Prompt.")
        return 1

    model = args.model or global_config.get("default_model", "claude-sonnet-4-6")
    runner = ClaudeRunner(
        model=model,
        fallback_model=args.fallback,
        permission_mode=global_config.get("default_permission_mode", "dontAsk"),
        allowed_tools=global_config.get("default_allowed_tools"),
        timeout=args.timeout or global_config.get("default_timeout_seconds", 7200),
    )

    if not args.quiet:
        print(f"[llmauto pipe] Modell: {model}", file=sys.stderr)

    result = runner.run(prompt)

    if result["success"]:
        print(result["output"])
        return 0
    else:
        print(result["output"], file=sys.stdout)
        print(f"\n[FEHLER] rc={result['returncode']}: {result['stderr']}", file=sys.stderr)
        return 1


def cmd_status(args):
    """Globaler Status ueber alle Modi."""
    from llmauto.modes.chain import show_status
    print(f"llmauto v{VERSION}")
    print()
    return show_status()


def cmd_version(args):
    """Version anzeigen."""
    print(f"llmauto v{VERSION}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="llmauto",
        description="LLM Automatisierung -- Ketten, Pipes, Prompts",
    )
    parser.add_argument("--version", "-V", action="store_true", help="Version anzeigen")
    subparsers = parser.add_subparsers(dest="command")

    # --- chain ---
    chain_parser = subparsers.add_parser("chain", help="Ketten-Modus (Marble-Run)")
    chain_parser.add_argument("chain_action", choices=["start", "list", "status", "stop", "pause", "resume", "steer", "log", "reset", "create"],
                              help="Aktion")
    chain_parser.add_argument("name", nargs="?", default=None, help="Ketten-Name")
    chain_parser.add_argument("extra", nargs="*", help="Zusaetzliche Argumente (Grund bei stop, Zeilenanzahl bei log)")
    chain_parser.add_argument("--bg", action="store_true", help="Im Hintergrund starten")
    chain_parser.set_defaults(func=cmd_chain)

    # --- pipe ---
    pipe_parser = subparsers.add_parser("pipe", help="Einzelner Claude-Aufruf")
    pipe_parser.add_argument("prompt", nargs="*", help="Prompt-Text")
    pipe_parser.add_argument("-f", "--file", help="Prompt aus Datei lesen")
    pipe_parser.add_argument("--model", "-m", help="Modell (default: Sonnet)")
    pipe_parser.add_argument("--fallback", help="Fallback-Modell")
    pipe_parser.add_argument("--timeout", type=int, help="Timeout in Sekunden")
    pipe_parser.add_argument("--quiet", "-q", action="store_true", help="Keine Status-Meldungen")
    pipe_parser.set_defaults(func=cmd_pipe)

    # --- status ---
    status_parser = subparsers.add_parser("status", help="Globaler Status")
    status_parser.set_defaults(func=cmd_status)

    # --- version ---
    version_parser = subparsers.add_parser("version", help="Version anzeigen")
    version_parser.set_defaults(func=cmd_version)

    # Parsen
    args = parser.parse_args()

    if args.version:
        print(f"llmauto v{VERSION}")
        return 0

    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
