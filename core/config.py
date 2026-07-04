"""
llmauto.core.config -- Konfigurationsmanagement
=================================================
Laedt, validiert und speichert Chain-Configs und globale Einstellungen.
"""
import json
import os
from pathlib import Path
from copy import deepcopy

BASE_DIR = Path(__file__).parent.parent

# Bekannte User-Home-Pfade fuer Cross-Machine Normalisierung.
# Eigene Pfade hier oder in config.json unter "known_user_homes" eintragen.
_KNOWN_USER_HOMES = [
    "C:\\Users\\User\\",
]
_ACTUAL_HOME = str(Path.home()) + os.sep

# BACH_ROOT: aus Umgebungsvariable oder dynamisch aus Dateipfad ableiten
# Im Module-Kontext ist BACH meist nicht direkt verfuegbar (Fallback: False/None)
_bach_root_candidate = Path(os.environ.get("BACH_ROOT", str(Path(__file__).parents[4])))
BACH_AVAILABLE = _bach_root_candidate.exists() and (_bach_root_candidate / "system").exists()
BACH_ROOT = _bach_root_candidate if BACH_AVAILABLE else None


DEFAULT_GLOBAL_CONFIG = {
    "default_model": "claude-sonnet-4-6",
    "default_permission_mode": "dontAsk",
    "default_allowed_tools": ["Read", "Edit", "Write", "Bash", "Glob", "Grep"],
    "default_timeout_seconds": 7200,
    "telegram": {
        "enabled": False,
        "bot_token_env": "LLMAUTO_TELEGRAM_BOT_TOKEN",
        "chat_id": "",
    }
}


DEFAULT_CHAIN_CONFIG = {
    "chain_name": "",
    "description": "",
    "mode": "loop",
    "max_rounds": 100,
    "runtime_hours": 0,
    "deadline": "",
    "max_consecutive_blocks": 5,
    "links": [],
    "prompts": {},
    "task_pools": {},
}


DEFAULT_LINK = {
    "name": "",
    "role": "worker",
    "model": None,
    "fallback_model": None,
    "prompt": "",
    "task_pool": "",
    "telegram_update": False,
    "until_full": False,
    "description": "",
}


def load_global_config():
    """Laedt die globale Konfiguration.

    Unterstuetzt "known_user_homes" in config.json fuer zusaetzliche
    Pfad-Normalisierung (z.B. ["C:\\\\Users\\\\MeinName\\\\"]).
    """
    global _KNOWN_USER_HOMES
    config_file = BASE_DIR / "config.json"
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        # Zusaetzliche User-Homes aus Config laden
        extra_homes = user_config.pop("known_user_homes", [])
        for home in extra_homes:
            if home not in _KNOWN_USER_HOMES:
                _KNOWN_USER_HOMES.append(home)
        config = deepcopy(DEFAULT_GLOBAL_CONFIG)
        config.update(user_config)
        return config
    return deepcopy(DEFAULT_GLOBAL_CONFIG)


def save_global_config(config):
    """Speichert die globale Konfiguration."""
    config_file = BASE_DIR / "config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def _normalize_paths(obj):
    """Ersetzt bekannte User-Home-Pfade durch den aktuellen.

    Damit funktionieren Chain-Configs auf verschiedenen Rechnern
    ohne manuelle Pfad-Anpassung.
    """
    if isinstance(obj, str):
        for known in _KNOWN_USER_HOMES:
            if known in obj and known != _ACTUAL_HOME:
                obj = obj.replace(known, _ACTUAL_HOME)
        return obj
    elif isinstance(obj, dict):
        return {k: _normalize_paths(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_paths(item) for item in obj]
    return obj


def _chain_dirs():
    """Suchreihenfolge fuer Chain-Configs: oeffentlich, dann _private."""
    return [BASE_DIR / "chains", BASE_DIR / "chains" / "_private"]


def load_chain(name):
    """Laedt eine gespeicherte Chain-Config.

    Sucht erst in chains/, dann in chains/_private/ (_private-Konvention
    fuer persoenliche, nicht veroeffentlichte Ketten).
    """
    candidates = [d / f"{name}.json" for d in _chain_dirs()]
    chain_file = next((c for c in candidates if c.exists()), None)
    if chain_file is None:
        raise FileNotFoundError(
            f"Kette '{name}' nicht gefunden: {' / '.join(str(c) for c in candidates)}"
        )
    with open(chain_file, "r", encoding="utf-8") as f:
        chain = json.load(f)
    # Pfade an aktuelles System anpassen
    chain = _normalize_paths(chain)
    # Defaults anwenden
    config = deepcopy(DEFAULT_CHAIN_CONFIG)
    config.update(chain)
    return config


def save_chain(name, config):
    """Speichert eine Chain-Config."""
    chains_dir = BASE_DIR / "chains"
    chains_dir.mkdir(exist_ok=True)
    chain_file = chains_dir / f"{name}.json"
    with open(chain_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def list_chains():
    """Listet alle gespeicherten Ketten (inkl. chains/_private/)."""
    names = []
    for chains_dir in _chain_dirs():
        if not chains_dir.exists():
            continue
        for f in chains_dir.glob("*.json"):
            if f.stem not in names:
                names.append(f.stem)
    return names


def new_link(**kwargs):
    """Erstellt ein neues Kettenglied mit Defaults."""
    link = deepcopy(DEFAULT_LINK)
    link.update(kwargs)
    return link
