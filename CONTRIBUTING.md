# Contributing to MarbleRun (llmauto) / Mitwirken an MarbleRun (llmauto)

Welcome! We welcome contributions to `MarbleRun` (`llmauto` - Local-first multi-agent orchestration and chain-execution framework from [ellmos-ai](https://github.com/ellmos-ai)). To maintain deterministic agent execution loops, air-gapped process isolation, single-writer filesystem safety, and compliance across multi-host environments, all contributions must adhere to the quality standards and operational invariants defined below.

---

## English

### 1. General Principles & Quality Gates
1. **Local-First & Zero-Egress (`INV-LOCAL-01`)**: Core agent execution loop, chain runner, handoff snapshotting, and process lifecycle operate strictly offline using the Python standard library. Zero outbound network sockets, zero telemetry, and zero phone-home tracking. External CLI agent invocation (e.g. `claude`) occurs only upon explicit user command vector.
2. **Unprivileged User-Mode Execution (`INV-SEC-02` / `RunAsInvoker`)**: All CLI runners, worker links, controller loops, and background processes execute strictly in unprivileged user space. Administrative elevation (UAC/root/sudo) is strictly forbidden.
3. **Multi-Provider Fail-Closed (`INV-GATE-03`)**: Multi-provider adapters (via `coma`) fail closed immediately if an unconfigured or unauthorized provider model is requested.
4. **Race-Free Parallel Workspaces (`INV-SYNC-04`)**: Parallel workers utilize isolated per-link sub-workspaces (`link_N/handoff.md`), preventing concurrent filesystem write collisions and race conditions.
5. **Anti-Starvation Skip Guard (`INV-CONT-05`)**: The core engine monitors agent outputs. If an agent produces empty or degenerate content, the previous verified handoff is restored automatically to prevent chain degradation.
6. **Transparent State Machine & WAL (`INV-STATE-06`)**: Execution state is maintained in human-readable Markdown and structured plain-text files (`status.txt`, `handoff.md`, `state/`), ensuring auditability and safe process interruption/resumption.
7. **Safe Process Scoping (`INV-PROC-07`)**: All external process invocations execute strictly through parameterized argument vectors (`subprocess.Popen` / `subprocess.run` with `shell=False`), preventing shell injection.
8. **Multi-OS CI Matrix (`INV-CI-08`)**: All features and fixes must pass automated GitHub Actions testing across Linux, Windows, macOS, and Python 3.10 through 3.13.
9. **Strict Concurrency Gate (`INV-CONC-09`)**: All CI workflows enforce `concurrency: cancel-in-progress: true` to prevent conflicting concurrent builds or race conditions.
10. **Cryptographic Auditability & Dual SLAs (`INV-SLA-10`)**: We commit to a 48h acknowledgment and 5-business-day triage SLA for security disclosures pursuant to [SECURITY.md](SECURITY.md).
11. **Version Freeze Discipline (`T-20260920-167562623`)**: Package version `0.1.3` is strictly frozen across `__init__.py`, `pyproject.toml`, and all manifests. Do not bump the version string. Document all advancements under `## [Unreleased]` in `CHANGELOG.md`.
12. **Clean Code & Regression Testing**: Every feature or fix must include regression tests in `tests/`. Keep test coverage at a 100% pass rate.
13. **Bilingual Parity**: Maintain synchronized structural and navigational parity across `README.md` and `README_de.md` (18-point dual anchors `sec-01` through `sec-18`).

### 2. Local Development Workflow (Plan D)
```bash
# Clone the repository (canonical Plan D location)
git clone https://github.com/ellmos-ai/MarbleRun.git "C:\_Local_DEV\repos\marblerun"
cd "C:\_Local_DEV\repos\marblerun"

# Install package in editable mode with test dependencies
pip install -e ".[test]"

# Run comprehensive test suite
pytest -ra -v

# Run fast static code analysis
ruff check .

# Check bytecode compilation
python -m compileall -q .

# Check whitespace and git diff cleanliness
git diff --check

# Verify version freeze compliance (must return 0 matches)
git diff -G"version = "
```

### 3. Submission Protocol
- Open an issue for architectural discussions before large refactoring.
- Keep provider API keys, tokens, and private credentials strictly outside the repository.
- Ensure all 10 governance invariants (`INV-LOCAL-01` to `INV-SLA-10`) remain VERIFIED.
- Pull requests must target the `main` branch.

### 4. License
By contributing to `MarbleRun`, you agree that your contributions will be licensed under the [MIT License](LICENSE).

---

## Deutsch

### 1. Grundsätze & Qualitäts-Tore
1. **Local-First & Zero-Egress (`INV-LOCAL-01`)**: Der Kern der Agenten-Schleife, der Chain-Runner, Handoff-Snapshots und der Prozess-Lebenszyklus arbeiten standardmäßig zu 100% offline ausschließlich mit Python-Standardbibliothek-Modulen. Keine Telemetrie, keine externen Sockets, kein Phone-Home. Externe LLM-CLI-Aufrufe erfolgen nur auf expliziten Befehl des Nutzers.
2. **Unprivilegierte Benutzer-Ausführung (`INV-SEC-02` / `RunAsInvoker`)**: Sämtliche Runner, Worker, Controller-Schleifen und Hintergrundprozesse laufen strikt im unprivilegierten Standard-Benutzerkontext. Administrative Rechte oder UAC-Elevationen sind verboten.
3. **Multi-Provider Fail-Closed (`INV-GATE-03`)**: Multi-Provider-Adapter (via `coma`) schließen sofort fehl (Fail-Closed), falls ein unkonfiguriertes oder nicht freigegebenes Provider-Modell angefordert wird.
4. **Race-Free Parallel-Workspaces (`INV-SYNC-04`)**: Parallele Worker arbeiten in isolierten Sub-Workspaces (`link_N/handoff.md`), um konkurrierende Schreibkonflikte auf Dateisystemebene auszuschließen.
5. **Anti-Starvation Skip-Schutz (`INV-CONT-05`)**: Die Core-Engine überwacht Agenten-Ausgaben. Bei leerem oder degeneriertem Output wird der letzte verifizierte Handoff automatisch wiederhergestellt.
6. **Persistente Zustandsmaschine & WAL (`INV-STATE-06`)**: Zustände werden in menschenlesbaren Markdown- und Textdateien (`status.txt`, `handoff.md`, `state/`) transparent protokolliert und erlauben sicheres Anhalten und Fortsetzen.
7. **Sicheres Prozess-Scoping (`INV-PROC-07`)**: Subprozesse werden ausschließlich über strukturierte Argumentvektoren (`shell=False`) gestartet, um Shell-Injektionen auszuschließen.
8. **Multi-OS CI-Matrix (`INV-CI-08`)**: Sämtliche Änderungen müssen die automatisierte GitHub Actions Matrix unter Linux, Windows, macOS und Python 3.10 bis 3.13 fehlerfrei durchlaufen.
9. **Strikter Concurrency-Gate (`INV-CONC-09`)**: Alle Workflows erzwingen `concurrency: cancel-in-progress: true` zur Vermeidung überlappender CI-Läufe.
10. **Kryptographische Auditierbarkeit & Duale SLAs (`INV-SLA-10`)**: Verbindliche Zusage von 48h Reaktionszeit und 5 Werktagen Triage-Bewertung gemäß [SECURITY.md](SECURITY.md).
11. **Version-Freeze-Disziplin (`T-20260920-167562623`)**: Paketversion `0.1.3` ist über alle Manifeste, Quelltexte und Badges hinweg strikt eingefroren. Kein Versions-Bump. Alle Weiterentwicklungen werden unter `## [Unreleased]` in `CHANGELOG.md` dokumentiert.
12. **Sauberer Code & Regressionstests**: Jede Änderung erfordert begleitende Tests in `tests/`. Die Testsuite muss zu 100% grün bleiben.
13. **Bilinguale Parität**: Strukturelle und navigatorische Parität zwischen `README.md` und `README_de.md` (18-Punkte Dual-Anker `sec-01` bis `sec-18`) ist zwingend einzuhalten.

### 2. Lokaler Entwicklungs-Workflow (Plan D)
```bash
# Klonen des Repositories (kanonischer Plan D Pfad)
git clone https://github.com/ellmos-ai/MarbleRun.git "C:\_Local_DEV\repos\marblerun"
cd "C:\_Local_DEV\repos\marblerun"

# Paket im Entwicklungsmodus mit Testabhängigkeiten installieren
pip install -e ".[test]"

# Testsuite ausführen
pytest -ra -v

# Schnelle statische Code-Prüfung ausführen
ruff check .

# Bytecode-Kompilierung validieren
python -m compileall -q .

# Whitespace- und Diff-Sauberkeit prüfen
git diff --check

# Versions-Freeze prüfen (darf keine Treffer liefern)
git diff -G"version = "
```

### 3. Einreichungs-Protokoll
- Vor umfangreichen Architektur-Refactorings bitte ein Issue zur Abstimmung eröffnen.
- Niemals API-Schlüssel, Passwörter oder persönliche Tokens im Repository committen.
- Sicherstellen, dass alle 10 Invarianten (`INV-LOCAL-01` bis `INV-SLA-10`) unverletzt bleiben.
- Pull Requests richten sich stets an den Branch `main`.

### 4. Lizenz
Mit dem Einreichen von Beiträgen erklärst du dich damit einverstanden, dass deine Beiträge unter der [MIT-Lizenz](LICENSE) veröffentlicht werden.
