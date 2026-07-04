# -*- coding: utf-8 -*-
"""Verdrahtungs-Regressionstests (Quelltext-Ebene).

Hintergrund: Der Skip-Overwrite-Schutz (state.protect_handoff_from_skip)
existierte monatelang als toter Code, weil modes/chain.py ihn nie aufrief
(Audit 2026-06-12, gefixt 2026-07-04). Diese Tests verhindern, dass die
Verdrahtung still wieder verschwindet — die Chain-Loop selbst ist ohne
laufende claude-CLI nicht sinnvoll unit-testbar.
"""
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT.parent))


class TestSkipProtectionWiring(unittest.TestCase):
    def test_chain_calls_protect_handoff_from_skip(self):
        src = (REPO_ROOT / "modes" / "chain.py").read_text(encoding="utf-8")
        calls = src.count("state.protect_handoff_from_skip(")
        self.assertGreaterEqual(
            calls, 2,
            "Skip-Overwrite-Schutz muss in beiden sequentiellen "
            "Link-Pfaden von modes/chain.py verdrahtet bleiben",
        )
        self.assertGreaterEqual(src.count("handoff_before = state.get_handoff()"), 2)


class TestCliActions(unittest.TestCase):
    def test_chain_create_registered(self):
        src = (REPO_ROOT / "llmauto.py").read_text(encoding="utf-8")
        self.assertIn('"create"', src.split("chain_action")[1].split("help=")[0],
                      "chain-Aktion 'create' muss in den argparse-choices stehen")

    def test_version_single_source(self):
        from llmauto import __version__
        import llmauto.llmauto as cli
        self.assertEqual(cli.VERSION, __version__)


if __name__ == "__main__":
    unittest.main()
