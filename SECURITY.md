# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## English

### Security Guarantees & Architecture

MarbleRun (`llmauto`) is an open-source, local-first LLM automation and agent-chain orchestration framework. The codebase is designed around strict privacy and execution safety principles:

1. **Local-First & Zero-Egress Architecture:**
   - All chain execution, round scheduling, state persistence (`sqlite3`), and handoff files are processed strictly on the local machine.
   - No telemetry, analytics, tracking, or unexpected third-party network egress is emitted by MarbleRun itself.
   - LLM calls are routed exclusively to the explicitly configured local CLI tools (e.g. `claude`, `codex`, `agy` via COMA adapter) or user-specified endpoints.

2. **Execution Boundaries & Subprocess Safety:**
   - Subprocesses are spawned with controlled arguments and environment sanitization.
   - Handoff files and workspace paths are strictly bound to configured directories to prevent directory traversal outside active project boundaries.
   - Race-free skip-overwrite protection isolates parallel worker states into per-worker baselines.

3. **Non-Elevation & Permission Principles:**
   - MarbleRun operates entirely in user-space (`Non-Elevation`).
   - Root / Administrator privileges are neither required nor recommended.

4. **Deterministic State & Data Integrity:**
   - Local sqlite state databases and handoff files use transactional writes with rollback safeguards on execution aborts.

### Reporting a Vulnerability

If you discover a security vulnerability or potential privacy leak in MarbleRun, please report it responsibly:

1. **Do NOT open a public issue.**
2. **Preferred:** Submit a confidential advisory via [GitHub Private Vulnerability Reporting](https://github.com/ellmos-ai/MarbleRun/security/advisories/new).
3. **Alternative:** Email the security team directly at `security@ellmos.ai` with a CC to `support@lukasgeiger.com`.

Please include in your report:
- A detailed description of the vulnerability and its potential impact.
- Step-by-step reproduction steps or a minimal proof-of-concept.
- Affected versions, OS environment, and provider configuration.

We will acknowledge receipt within 48 hours and provide a timeline for triage, remediation, and coordinated disclosure.

---

<a name="deutsch"></a>
## Deutsch

### Sicherheitsgarantien & Architektur

MarbleRun (`llmauto`) ist ein quelloffenes, Local-First Automatisierungs- und Agentenketten-Framework für LLMs. Die Codebasis folgt strengen Datenschutz- und Ausführungssicherheitsprinzipien:

1. **Local-First & Zero-Egress-Architektur:**
   - Alle Chain-Ausführungen, Rundenzähler, Zustandsspeicher (`sqlite3`) und Handoff-Dateien verbleiben vollständig auf dem lokalen System.
   - MarbleRun selbst überträgt keinerlei Telemetrie, Tracking-Daten oder ungeprüften ausgehenden Netzwerkverkehr.
   - LLM-Aufrufe erfolgen ausschließlich über die vom Nutzer explizit konfigurierten lokalen CLIs (z. B. `claude`, `codex`, `agy` via COMA-Adapter) oder angegebene Schnittstellen.

2. **Ausführungsgrenzen & Subprozess-Sicherheit:**
   - Subprozesse werden mit bereinigten Argumenten und kontrollierten Umgebungsvariablen gestartet.
   - Handoff-Pfade und Projektverzeichnisse sind streng validiert, um Pfad-Traversal außerhalb des aktiven Arbeitsbereichs zu verhindern.
   - Parallele Worker nutzen isolierte Handoff-Baselines mit atomarem Überschreibschutz (Skip-Overwrite Protection).

3. **Non-Elevation (Benutzerrechte-Betrieb):**
   - MarbleRun läuft vollständig im unprivilegierten Benutzerbereich (`User-Mode`).
   - Administrator- oder Root-Rechte sind weder erforderlich noch vorgesehen.

4. **Deterministische Datenintegrität:**
   - Lokale SQLite-Zustandsdatenbanken und Handoff-Dateien nutzen transaktionale Schreiboperationen mit Rollback-Schutz.

### Sicherheitslücke melden

Falls Sie eine Sicherheitslücke oder ein Datenschutzproblem entdecken:

1. **Eröffnen Sie KEIN öffentliches GitHub-Issue.**
2. **Bevorzugt:** Nutzen Sie das vertrauliche [GitHub Private Vulnerability Reporting](https://github.com/ellmos-ai/MarbleRun/security/advisories/new).
3. **Alternativ:** Senden Sie eine E-Mail an `security@ellmos.ai` (CC: `support@lukasgeiger.com`).

Bitte geben Sie eine genaue Fehlerbeschreibung, Reproduktionsschritte sowie die betroffenen Versionen und Betriebssystemumgebungen an. Wir bestätigen den Eingang innerhalb von 48 Stunden.
