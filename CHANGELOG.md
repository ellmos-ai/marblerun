# Changelog

## [Unreleased]

### Maintenance & Hygiene (2026-07-26)

- Added `[tool.pytest.ini_options]` in `pyproject.toml` targeting `tests/` and excluding `_archive/` (83/83 unit tests passing 100% green).
- Created GitHub Actions CI workflow (`.github/workflows/tests.yml`) testing Python 3.10-3.13 on Ubuntu and Windows; `fail-fast: false` retains independent platform findings.
- Updated `ellmos-module.v2.json` visibility to `public`.
- Updated `llms.txt` header to `2026-07-26` with verified test status.
- Added Shields.io badges and GFM AI callout notes to `README.md` and `README_de.md`.

### Fixed

- `python -m llmauto ...` now boots correctly from the repository root after
  the source directory rename to `marblerun`; the CLI no longer imports the
  sibling `llmauto.py` as a partially initialized package.
- Repository hygiene now ignores common local credential, recovery-code,
  private-key, certificate, and SQLite runtime artifacts while keeping
  `.env.example` and `.env.sample` trackable; guarded by
  `tests/test_repository_hygiene.py`.
- **Skip-overwrite protection is now actually wired in** (module review
  2026-07-04): `state.protect_handoff_from_skip()` existed but was never
  called — a worker replying only "SKIPPED" could replace the main handoff
  and starve every following link of context. Both sequential link paths in
  `modes/chain.py` now snapshot the handoff before each run and restore it
  when a skip-overwrite is detected (the skip text goes to the per-link
  handoff file instead). Wiring guarded by `tests/test_wiring.py`.
- `python -m llmauto chain create` now exists — `core/chain_creator.py`
  advertised the command, but the CLI did not register the action.
- `scripts/chain_creator.py` standalone invocation fixed (sys.path pointed
  at the package directory itself instead of its parent —
  `ModuleNotFoundError` on every direct call).
- Timeout default unified to 7200 s (code literals said 1800 while
  `config.json` and the READMEs said 7200; the literals only applied when
  `config.json` was absent).
- `SECURITY.md` advisory links pointed at a non-existent third repo variant
  (`lukisch/MarbleRun`) — corrected to the canonical `ellmos-ai/MarbleRun`.
- Version is single-sourced from `llmauto.__version__` (CLI imports it,
  `pyproject.toml` uses a dynamic version attr; previously three copies).
- Removed the dead `telegram_interval` counter (incremented, never read).
- `.gitignore`: ignore local `LOCK*.txt` coordination files.
- Clarified that `core/chain_creator.py`'s `prompts/templates/` holds
  PROMPT templates (.txt) while repo-root `templates/` holds CHAIN
  templates (.json) — the 2026-06-12 audit had flagged this as a wrong
  path, which turned out to be a misdiagnosis.
- Local housekeeping (not tracked): stale `logs/`, `state/`, `_debris/` and
  root `handoff.md` moved to `_archive/`, generated PDFs and egg-info
  removed from the working tree.

- Allow source-tree imports such as `llmauto.core` and `llmauto.modes` when
  running tests directly from a checkout.

### Documentation

- Added 2026-06-12 discovery context for `llmauto`, Claude Code agent-chain
  runners, local-first multi-agent orchestration, and MarbleRun name
  disambiguation.
- Added `llms.txt` Audience, Search Phrases, and External Discovery Notes
  sections for LLM crawlers and search indexes.
