# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## English

### Security Guarantees & Architecture

MarbleRun (`llmauto`) is an open-source, local-first LLM automation and agent-chain orchestration framework. The codebase is designed around strict privacy and execution safety principles:

1. **Local state & network boundaries (no enforced Zero-Egress):**
   - All chain execution, round scheduling, state persistence (`sqlite3`), and handoff files are processed strictly on the local machine.
   - The Python orchestrator has no analytics reporting. The default Claude CLI backend can transmit prompts and context; provider/tool traffic is not isolated or blocked. The optional Telegram notifier adds a separate outbound path and is disabled by default.
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

### Supported Versions / Unterstützte Versionen

| Version | Supported / Unterstützt | Status |
|---|---|---|
| 0.1.x | :white_check_mark: Yes / Ja | Active Maintenance / Aktive Wartung |
| < 0.1.0 | :x: No / Nein | Deprecated / Veraltet |

### Reporting a Vulnerability

If you discover a security vulnerability or potential privacy leak in MarbleRun, please report it responsibly:

1. **Do NOT open a public issue.**
2. **Preferred:** Submit a confidential advisory via [GitHub Private Vulnerability Reporting](https://github.com/ellmos-ai/MarbleRun/security/advisories/new).
3. **There is currently no e-mail channel.** Earlier revisions of this policy offered
   `security@ellmos.ai`, `security@open-bricks.org`, `lukas@open-bricks.org` and
   `support@lukasgeiger.com`. They are not offered as verified reporting channels.
   A current DNS snapshot cannot establish historical delivery or receipt, and an absent
   MX record alone does not establish non-delivery (RFC 5321 §5.1). Private vulnerability
   reporting is enabled on this repository and is the designated channel. If you cannot use it, open a public issue
   that says only that you have a security finding and asks for a private channel -- do
   not include any details there.

Please include in your report:
- A detailed description of the vulnerability and its potential impact.
- Step-by-step reproduction steps or a minimal proof-of-concept.
- Affected versions, OS environment, and provider configuration.

We aim to acknowledge receipt within 48 hours and provide a triage assessment within 5 business days. These are best-effort targets, not guaranteed response times.

---

<a name="deutsch"></a>
## Deutsch

### Sicherheitsgarantien & Architektur

MarbleRun (`llmauto`) ist ein quelloffenes, Local-First Automatisierungs- und Agentenketten-Framework für LLMs. Die Codebasis folgt strengen Datenschutz- und Ausführungssicherheitsprinzipien:

1. **Lokaler Zustand & Netzwerkgrenzen (kein erzwungenes Zero-Egress):**
   - Alle Chain-Ausführungen, Rundenzähler, Zustandsspeicher (`sqlite3`) und Handoff-Dateien verbleiben vollständig auf dem lokalen System.
   - Der Python-Orchestrator sendet keine Analysedaten. Das Standardbackend Claude-CLI kann Prompts und Kontext übertragen; Provider-/Werkzeugverkehr wird nicht isoliert oder blockiert. Der optionale Telegram-Melder ergänzt einen eigenen ausgehenden Pfad und ist standardmäßig abgeschaltet.
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
3. **Ein E-Mail-Kanal besteht derzeit nicht.** Frühere Fassungen dieser Richtlinie nannten
   `security@ellmos.ai`, `security@open-bricks.org`, `lukas@open-bricks.org` und
   `support@lukasgeiger.com`. Sie werden nicht als bestätigte Meldekanäle angeboten.
   Eine aktuelle DNS-Messung belegt keine historische Zustellung oder Nichtzustellung;
   ein fehlender MX-Eintrag allein beweist keine Unzustellbarkeit (RFC 5321 §5.1).
   Das vertrauliche Meldeverfahren von GitHub ist für dieses Repository aktiviert und
   ist der vorgesehene Kanal. Wer es nicht nutzen kann, eröffnet ein öffentliches Issue, das
   ausschließlich mitteilt, dass ein Sicherheitsfund vorliegt, und um einen vertraulichen
   Kanal bittet -- ohne jede inhaltliche Angabe.

Bitte geben Sie eine genaue Fehlerbeschreibung, Reproduktionsschritte sowie die betroffenen Versionen und Betriebssystemumgebungen an. Wir streben eine Bestätigung innerhalb von 48 Stunden und eine Triage-Bewertung innerhalb von 5 Werktagen an. Das sind Best-Effort-Ziele, keine garantierten Reaktionszeiten.
