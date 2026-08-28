# Changelog

## [Unreleased]

### Live-Test-Automation Repair (2026-08-28)

- Restored documented link and chain-default precedence for permission mode,
  allowed tools, timeout, and environment in all execution paths.
- Added a lifecycle-safe Roblox Studio MCP wrapper with dated image/JSON evidence
  persistence and verified child-tree cleanup on client disconnect.
- Added a reusable Open Compute GUI live-test template and evidence contract.
- Re-certified the merged upstream changes and this repair with `ruff check .`
  and the full suite: 114 passed, 0 skipped, exit code 0.

### Discoverability, Visual Showcase, Tactical Sequence Diagram & Ecosystem Expansion (2026-08-25)

- Enhanced bilingual README architecture (`README.md` & `README_de.md`) with structured 12-item quick navigation jump marks and 100% German/English parity.
- Embedded tactical Mermaid `sequenceDiagram` with autonumbering to visualize baseline handoff snapshotting, safe commit cycles, and controller completion checks.
- Formalized Core Capabilities & Security Invariants matrix (100% Offline / Zero-Egress, Non-Elevation User Mode, Multi-Provider Fail-Closed, Race-Free Parallel Workers, Skip-Overwrite Guard, Persistent State Machine, Multi-OS CI Matrix, Strict Concurrency Gate) across bilingual READMEs.
- Structured Chain Patterns & Role Matrix table detailing `worker`, `reviewer`, and `controller` responsibilities and context retention strategies.
- Added comprehensive CLI Reference table covering `start`, `status`, `stop`, `log`, `reset`, `create`, and `pipe` commands.
- Expanded Sibling Tools & Ecosystem table to 12 partner repositories across `ellmos-ai`, `dev-bricks`, `file-bricks`, `entertain-and-more`, and `open-bricks` (`COMA`, `policy-registry`, `system-explorer`, `sqlite-transit-sync`, `ellmos-clatcher-mcp`, `automation-master`, `DevCenter`, `CodeBox`, `FileCommander`, `ProFiler`, `CuteStrike`, `open-bricks`).
- Hardened CI workflow (`.github/workflows/tests.yml`) with workflow-level `concurrency` and automatic cancellation of superseded runs (`cancel-in-progress: true`).
- Extended automated contract tests in `tests/test_metadata.py` with 3 new contract test suites (`test_readme_visual_showcase_and_sequence_diagram`, `test_readme_capabilities_and_invariants_matrix`, `test_readme_sibling_ecosystem_matrix`, and CI concurrency check; 103 passed, 3 skipped, 100% green).
- Synchronized `llms.txt` Last-checked timestamp to `2026-08-25` and updated test status metrics.

### Maintenance, CI-Matrix & Security Hardening (2026-08-21)

- Modernized GitHub Actions CI workflow (`.github/workflows/tests.yml`) to multi-OS matrix (`ubuntu-latest`, `windows-latest`, `macos-latest`), Python 3.10-3.13 support, pip caching, automated `ruff check .` linting gate, and pytest test suite.
- Enhanced `pyproject.toml` with PEP 621 Standard Classifiers (`Operating System :: OS Independent`, `Microsoft :: Windows`, `POSIX :: Linux`, `MacOS`, `Environment :: Console`, `Topic :: System :: Monitoring`) and project URLs (`Documentation`, `Changelog`).
- Upgraded `SECURITY.md` to comprehensive bilingual (English & German) security policy including Local-First & Zero-Egress guarantees, Subprocess execution safety, Non-Elevation (User-Mode operation), and direct security contacts (`security@ellmos.ai`, `support@lukasgeiger.com`).
- Extended automated metadata contract test suite in `tests/test_metadata.py` with CI matrix validation, PEP 621 metadata checks, and bilingual security policy validation (100 passed, 3 skipped, 103 total, 100% green).
- Synchronized Shields.io badges in `README.md` and `README_de.md` (CI badge, Pytest 100 passed, Python 3.10-3.13, Platform Linux | Windows | macOS, Privacy 100% Offline | Zero-Egress, Security Local-First).
- Synchronized `llms.txt` Last-checked timestamp to `2026-08-21` and verified test counts.

### Maintenance & Tidy-up (2026-08-21)

- Refreshed the synchronized English/German Pytest badges and `llms.txt` from a
  local full-suite readback: 98 passed, 0 skipped (98 total), exit code 0.
- Rechecked the mandatory P-006 Core documentation pair (`README.md` and
  `README_de.md`); both remain structurally aligned and current.

### Discoverability, README-Design & Pytest Status Check (2026-08-16)

- Synchronized Pytest status badges across `README.md` and `README_de.md` to 98 passed, 3 skipped (101 total) 100% green.
- Added version badge (v0.1.0) and cross-linking matrix for sibling tools (`coma`, `policy-registry`, `system-explorer`, `sqlite-transit-sync`, `automation-master`, `DevCenter`, `CodeBox`).
- Integrated automated metadata & manifest test suite in `tests/test_metadata.py` (verifying `pyproject.toml`, `ellmos-module.v2.json`, documentation files, version consistency, and `llms.txt` ecosystem markers).
- Configured `[tool.ruff]` and `[tool.ruff.lint]` in `pyproject.toml` (target-version = "py310", line-length = 120; ruff check 100% clean).
- Synchronized `llms.txt` Last-checked timestamp to `2026-08-16` and test metrics.

### Fixed (2026-08-13)

- Added race-free skip-overwrite protection for parallel workers: each worker
  receives an isolated handoff seeded from one baseline snapshot, the prompt
  names that file explicitly, short `SKIP` responses stay per-worker, and
  unexpected writes to the shared handoff fail closed. Parallel reports are
  merged deterministically and covered by `tests/test_parallel_handoff.py`.

### Discoverability, README-Design & SEO Check (2026-08-04)

- Added interactive Mermaid system architecture diagrams for chain execution loops in `README.md` and `README_de.md`.
- Synchronized Pytest status badges to 90 passed, 3 skipped (93 total) 100% green.
- Added `ellmos-ai` organization and `open-bricks` ecosystem badges.
- Hardened optional provider import checks in `tests/test_runner.py`.
- Updated `llms.txt` Last-checked timestamp to `2026-08-04`.

### Maintenance & Hygiene (2026-08-01)

- Synchronized the maintained German README with the canonical English
  provider, code-example, project-structure, and liability sections.
- Updated `llms.txt` Last-checked timestamp to `2026-08-01`.
- Synced Pytest badges in `README.md` and `README_de.md` to 87 passed.
- Verified repository hygiene, 100% clean git working tree, and pytest test suite (87 passed, 3 skipped).

### Maintenance & Hygiene (2026-07-29)

- Updated `llms.txt` Last-checked timestamp to `2026-07-29` and test metrics (87 passed, 3 skipped gracefully on missing optional `coma` dependency).
- Hardened `tests/test_runner.py` with `pytest.importorskip("coma")` to handle environment variations where optional provider backends are omitted.
- Verified repository hygiene, clean git working tree, and pytest test suite.

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
