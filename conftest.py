"""Pytest-Vorlauf: sichert, dass "llmauto" das Paket meint, nicht llmauto.py.

Hintergrund: Das Repo-Root IST das Paket (siehe pyproject.toml, package-dir
llmauto = "."). Im Root liegt zusaetzlich das CLI-Modul llmauto.py. Solange der
Ordner selbst "llmauto" hiess, loeste pytest den Import ueber das
Elternverzeichnis auf und fand das Paket. Seit der Ordner "marblerun" heisst
(Repo-Name = Modulname, Paket = Importname), greift diese Aufloesung nicht mehr:
liegt der Repo-Root in sys.path -- etwa weil pytest aus dem Repo-Root heraus
gestartet wird -- verdeckt llmauto.py das gleichnamige Paket, und die Tests
brechen beim Import von llmauto.core.* ab.

Dieser Vorlauf laedt das Paket explizit ueber seinen Dateipfad und traegt es
unter dem Namen "llmauto" in sys.modules ein, bevor ein Test importiert. Damit
laufen die Tests unabhaengig vom Arbeitsverzeichnis und unabhaengig davon, ob
ein Editable-Install vorhanden ist.
"""

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


def _load_package_as_llmauto():
    vorhanden = sys.modules.get("llmauto")
    if vorhanden is not None and hasattr(vorhanden, "__path__"):
        return  # bereits als Paket geladen -- nichts zu tun

    spec = importlib.util.spec_from_file_location(
        "llmauto",
        _ROOT / "__init__.py",
        submodule_search_locations=[str(_ROOT)],
    )
    modul = importlib.util.module_from_spec(spec)
    sys.modules["llmauto"] = modul
    spec.loader.exec_module(modul)


_load_package_as_llmauto()
