"""Tests fuer llmauto.modes.chain -- Hilfsfunktionen."""
import pytest

from llmauto.modes.chain import _home_placeholders, resolve_prompt


class TestHomePlaceholders:
    """Tests fuer die plattformuebergreifende {HOME}/{BASH_HOME}-Ersetzung."""

    def test_windows_home(self):
        home_native, home_bash = _home_placeholders("C:\\Users\\YourName\\")
        assert home_native == "C:\\Users\\YourName"
        assert home_bash == "/c/Users/YourName"

    def test_windows_home_without_trailing_sep(self):
        home_native, home_bash = _home_placeholders("D:\\Homes\\abc")
        assert home_native == "D:\\Homes\\abc"
        assert home_bash == "/d/Homes/abc"

    def test_posix_home_no_valueerror(self):
        # Auf macOS/Linux enthaelt der Home-Pfad keinen ':' --
        # darf NICHT crashen (frueher: ValueError bei split(":", 1))
        home_native, home_bash = _home_placeholders("/home/user/")
        assert home_native == "/home/user"
        assert home_bash == "/home/user"

    def test_macos_home(self):
        home_native, home_bash = _home_placeholders("/Users/lukas")
        assert home_native == "/Users/lukas"
        assert home_bash == "/Users/lukas"

    def test_default_uses_actual_home(self):
        # Ohne Argument: aktuelles User-Home, kein Crash auf irgendeiner Plattform
        home_native, home_bash = _home_placeholders()
        assert home_native
        assert home_bash.startswith("/") or ":" not in home_bash


class TestResolvePromptPrivate:
    """Tests fuer die _private-Konvention: prompts/_private/ als Fallback."""

    @pytest.fixture
    def prompt_base(self, tmp_path):
        (tmp_path / "prompts" / "_private").mkdir(parents=True)
        return tmp_path

    def test_private_prompt_found(self, prompt_base):
        (prompt_base / "prompts" / "_private" / "geheim.txt").write_text(
            "PRIVATER PROMPT", encoding="utf-8")
        result = resolve_prompt({"prompt": "geheim"}, {}, base_dir=prompt_base)
        assert result == "PRIVATER PROMPT"

    def test_private_prompt_exact_filename(self, prompt_base):
        (prompt_base / "prompts" / "_private" / "geheim.txt").write_text(
            "PRIVATER PROMPT", encoding="utf-8")
        result = resolve_prompt({"prompt": "geheim.txt"}, {}, base_dir=prompt_base)
        assert result == "PRIVATER PROMPT"

    def test_public_prompt_wins_over_private(self, prompt_base):
        (prompt_base / "prompts" / "doppelt.txt").write_text(
            "OEFFENTLICH", encoding="utf-8")
        (prompt_base / "prompts" / "_private" / "doppelt.txt").write_text(
            "PRIVAT", encoding="utf-8")
        result = resolve_prompt({"prompt": "doppelt"}, {}, base_dir=prompt_base)
        assert result == "OEFFENTLICH"

    def test_unknown_prompt_falls_back_to_inline(self, prompt_base):
        result = resolve_prompt({"prompt": "Mach Aufgabe X"}, {}, base_dir=prompt_base)
        assert result == "Mach Aufgabe X"
