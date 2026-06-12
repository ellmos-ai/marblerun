"""Tests fuer llmauto.modes.chain -- Hilfsfunktionen."""
import pytest

from llmauto.modes.chain import _home_placeholders


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
