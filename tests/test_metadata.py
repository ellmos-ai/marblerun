"""Metadata, manifest, CI workflow, and discoverability parity tests for MarbleRun / llmauto."""

from __future__ import annotations

import json
from pathlib import Path

import tomllib

import llmauto

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_package_version_consistency():
    """Verify package version is defined and well-formed."""
    version = getattr(llmauto, "__version__", None)
    assert version is not None, "llmauto.__version__ must be defined"
    assert isinstance(version, str)
    parts = version.split(".")
    assert len(parts) >= 3, f"Version '{version}' must have at least major.minor.patch"


def test_pyproject_metadata_integrity():
    """Verify pyproject.toml contains mandatory project metadata, PEP 621 classifiers, and ruff settings."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    assert pyproject_file.exists(), "pyproject.toml must exist"

    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    project = data.get("project", {})

    assert project.get("name") == "llmauto"
    assert "MarbleRun" in project.get("description", "")
    # PEP 639: license is an SPDX expression string, license files are declared separately
    assert project.get("license") == "MIT"
    assert project.get("license-files") == ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md"]
    assert "urls" in project
    assert project["urls"].get("Homepage") == "https://github.com/ellmos-ai/MarbleRun"
    assert project["urls"].get("Repository") == "https://github.com/ellmos-ai/MarbleRun"
    assert project["urls"].get("Issues") == "https://github.com/ellmos-ai/MarbleRun/issues"
    assert project["urls"].get("Documentation") == "https://github.com/ellmos-ai/MarbleRun#readme"
    assert project["urls"].get("Changelog") == "https://github.com/ellmos-ai/MarbleRun/blob/main/CHANGELOG.md"

    classifiers = project.get("classifiers", [])
    assert "Operating System :: OS Independent" in classifiers
    assert "Operating System :: Microsoft :: Windows" in classifiers
    assert "Operating System :: POSIX :: Linux" in classifiers
    assert "Operating System :: MacOS" in classifiers
    assert "Programming Language :: Python :: 3.13" in classifiers

    # Optional dependencies
    optional_deps = project.get("optional-dependencies", {})
    assert "test" in optional_deps
    assert any("pytest" in dep for dep in optional_deps["test"])
    assert any("ruff" in dep for dep in optional_deps["test"])

    # Ruff section
    assert "tool" in data and "ruff" in data["tool"], "pyproject.toml must configure [tool.ruff]"


def test_ci_workflow_integrity():
    """Verify .github/workflows/tests.yml runs multi-OS, multi-version matrix, ruff lint gate, and concurrency gate."""
    workflow_file = REPO_ROOT / ".github" / "workflows" / "tests.yml"
    assert workflow_file.is_file(), "CI tests workflow must exist"
    content = workflow_file.read_text(encoding="utf-8")

    assert "ubuntu-latest" in content
    assert "windows-latest" in content
    assert "macos-latest" in content
    assert "3.10" in content and "3.11" in content and "3.12" in content and "3.13" in content
    assert "ruff check" in content
    assert "python -m pytest" in content
    assert "timeout-minutes: 15" in content
    assert "concurrency:" in content
    assert "cancel-in-progress: true" in content


def test_security_policy_bilingual_integrity():
    """Verify SECURITY.md contains bilingual policy with zero-egress and contacts."""
    security_file = REPO_ROOT / "SECURITY.md"
    assert security_file.is_file(), "SECURITY.md must exist"
    sec_text = security_file.read_text(encoding="utf-8")

    assert "## English" in sec_text
    assert "## Deutsch" in sec_text
    assert "Zero-Egress" in sec_text or "zero-egress" in sec_text.lower()
    assert "Non-Elevation" in sec_text
    assert "security@ellmos.ai" in sec_text
    assert "support@lukasgeiger.com" in sec_text
    assert "https://github.com/ellmos-ai/MarbleRun/security/advisories/new" in sec_text


def test_ellmos_module_manifest_validity():
    """Verify ellmos-module.v2.json has valid structure and references."""
    manifest_file = REPO_ROOT / "ellmos-module.v2.json"
    assert manifest_file.exists(), "ellmos-module.v2.json must exist"

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest.get("schema") == "ellmos.module.v2"
    assert manifest.get("id") == "marblerun"
    assert manifest.get("category") == "control"
    assert manifest.get("kind") == "workflow"
    assert manifest.get("status") == "active"
    assert manifest.get("visibility") == "public"
    assert manifest.get("source_of_truth", {}).get("repository") in (
        "https://github.com/ellmos-ai/marblerun",
        "https://github.com/ellmos-ai/MarbleRun",
    )


def test_required_documentation_and_governance_files():
    """Verify presence of core documentation and governance files."""
    required_files = [
        "README.md",
        "README_de.md",
        "CHANGELOG.md",
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "USER-DOCU.md",
        "llms.txt",
        "MARKETING-LOG.txt",
    ]
    for rel_path in required_files:
        p = REPO_ROOT / rel_path
        assert p.is_file(), f"Missing required file: {rel_path}"


def test_llms_txt_and_badge_discovery_parity():
    """Verify llms.txt and READMEs carry consistent ecosystem anchors."""
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.exists()
    llms_text = llms_file.read_text(encoding="utf-8")
    assert any(
        stamp in llms_text for stamp in ("Last-checked: 2026-09-22", "Last-checked: 2026-09-20")
    ), "llms.txt must have current Last-checked timestamp"
    assert any(repo in llms_text for repo in ("https://github.com/ellmos-ai/marblerun", "https://github.com/ellmos-ai/MarbleRun"))
    assert "llmauto" in llms_text


def test_gui_live_test_template_has_tools_and_persistent_evidence():
    template = json.loads(
        (REPO_ROOT / "templates" / "gui-live-test.json").read_text(
            encoding="utf-8"
        )
    )
    defaults = template["defaults"]
    assert "mcp__open_compute__capture" in defaults["allowed_tools"]
    assert "mcp__open_compute__do" in defaults["allowed_tools"]
    assert defaults["env"]["OC_SESSION_DIR"]
    assert (REPO_ROOT / "prompts" / "gui_live_tester.txt").exists()

    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in [readme_en, readme_de]:
        assert "ellmos--ai-blue.svg" in readme or "ellmos-ai" in readme
        assert "open--bricks-orange.svg" in readme or "open-bricks" in readme
        assert "llms.txt" in readme


def test_readme_visual_showcase_and_sequence_diagram():
    """Verify both English and German READMEs feature Mermaid visual showcase and tactical sequence diagram."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in [readme_en, readme_de]:
        assert "```mermaid" in readme
        assert "graph TD" in readme
        assert "sequenceDiagram" in readme
        assert "autonumber" in readme
        assert "handoff.md" in readme
        assert "Runner" in readme or "Runner as" in readme


def test_readme_capabilities_and_invariants_matrix():
    """Verify both English and German READMEs define the 10 core security & runtime invariants."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    # Invariants in English README
    assert "Zero-Egress" in readme_en
    assert "Non-Elevation" in readme_en
    assert "Multi-Provider Fail-Closed" in readme_en
    assert "Race-Free Parallel Workers" in readme_en
    assert "Skip-Overwrite Guard" in readme_en
    assert "Persistent State Machine" in readme_en
    assert "Safe Process Scoping" in readme_en
    assert "Multi-OS CI Matrix" in readme_en
    assert "Strict Concurrency Gate" in readme_en
    assert "Cryptographic Receipt Integrity" in readme_en

    # Invariants in German README
    assert "Zero-Egress" in readme_de
    assert "Privilegienfreie Ausführung" in readme_de
    assert "Multi-Provider Fail-Closed" in readme_de
    assert "Race-Free Parallel-Worker" in readme_de
    assert "Skip-Überschreibschutz" in readme_de
    assert "Persistente Zustandsmaschine" in readme_de
    assert ("Sichere Prozess-Scoping" in readme_de or "Sicheres Prozess-Scoping" in readme_de)
    assert "Multi-OS CI-Matrix" in readme_de
    assert "Strikter Concurrency-Gate" in readme_de
    assert "Kryptographische Auditierbarkeit" in readme_de


def test_readme_sibling_ecosystem_matrix():
    """Verify both READMEs reference all 12 partner tools in the ecosystem table."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    expected_tools = [
        "COMA",
        "policy-registry",
        "system-explorer",
        "sqlite-transit-sync",
        "ellmos-clatcher-mcp",
        "automation-master",
        "DevCenter",
        "CodeBox",
        "FileCommander",
        "ProFiler",
        "CuteStrike",
        "open-bricks",
    ]

    for tool in expected_tools:
        assert tool in readme_en, f"Missing sibling tool '{tool}' in README.md"
        assert tool in readme_de, f"Missing sibling tool '{tool}' in README_de.md"


def test_readme_quick_navigation_anchors():
    """Verify both English and German READMEs define 18-point quick navigation with explicit HTML anchors."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "## Quick Navigation" in readme_en
    assert "## Schnellnavigation" in readme_de

    # Verify all 18 numbered items in Quick Navigation
    for i in range(1, 19):
        assert f"- [{i}. " in readme_en, f"Missing item {i} in README.md Quick Navigation"
        assert f"- [{i}. " in readme_de, f"Missing item {i} in README_de.md Schnellnavigation"

    anchors_en = [
        "#what-is-llmauto",
        "#visual-showcase--system-architecture",
        "#tactical-round-execution--sequence-flow",
        "#target-personas--discoverability-queries",
        "#comparative-matrix--alternatives",
        "#governance--runtime-invariants-matrix",
        "#chain-patterns--role-matrix",
        "#installation--prerequisites",
        "#step-by-step-quickstart",
        "#pipe-mode--ad-hoc-execution",
        "#cli-reference--global-configuration",
        "#sibling-tools--ecosystem-matrix",
        "#third-party-licenses--transparency",
        "#security-policy--operational-limits",
        "#repository-structure--key-assets",
        "#development--test-matrix",
        "#discovery--keywords--disambiguation",
        "#statutory-notice--liability-limitation",
    ]
    for anchor in anchors_en:
        assert anchor in readme_en, f"Missing anchor '{anchor}' in README.md"
        target_id = anchor.lstrip("#")
        assert f'id="{target_id}"' in readme_en or f'name="{target_id}"' in readme_en, (
            f"Missing HTML target id='{target_id}' in README.md"
        )

    anchors_de = [
        "#was-ist-llmauto",
        "#visuelle-galerie--systemarchitektur",
        "#taktischer-rundenablauf--sequenzdiagramm",
        "#zielgruppen--discoverability-suchanfragen",
        "#vergleichsmatrix--alternativen",
        "#governance--laufzeit-invariantenmatrix",
        "#chain-muster--rollenmatrix",
        "#installation--voraussetzungen",
        "#schritt-fuer-schritt-schnellstart",
        "#pipe-modus--ad-hoc-ausfuehrung",
        "#cli-referenz--globale-konfiguration",
        "#geschwister-tools--oekosystemmatrix",
        "#drittanbieter-lizenzen--transparenz",
        "#sicherheitsrichtlinie--betriebsgrenzen",
        "#repository-struktur--kernkomponenten",
        "#entwicklung--testmatrix",
        "#discovery-kontext--suchphrasen",
        "#haftungsausschluss--lizenz",
    ]
    for anchor in anchors_de:
        assert anchor in readme_de, f"Missing anchor '{anchor}' in README_de.md"
        target_id = anchor.lstrip("#")
        assert f'id="{target_id}"' in readme_de or f'name="{target_id}"' in readme_de, (
            f"Missing HTML target id='{target_id}' in README_de.md"
        )


def test_security_policy_slas_and_contacts():
    """Verify SECURITY.md includes supported versions, SLAs, and security@open-bricks.org."""
    sec_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "security@open-bricks.org" in sec_text
    assert "48 hours" in sec_text or "48 Stunden" in sec_text
    assert "5 business days" in sec_text or "5 Werktagen" in sec_text
    assert "Supported Versions" in sec_text
    assert "0.1.x" in sec_text


def test_marketing_log_and_changelog_recency():
    """Verify MARKETING-LOG.txt exists and CHANGELOG.md has 2026-09-11 entry."""
    m_log = REPO_ROOT / "MARKETING-LOG.txt"
    assert m_log.is_file(), "MARKETING-LOG.txt must exist in repo root"
    m_text = m_log.read_text(encoding="utf-8")
    assert "2026-09-11" in m_text
    assert "ellmos-ai/marblerun" in m_text

    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "2026-09-11" in changelog_text


def test_ci_workflow_compileall_and_caching():
    """Verify .github/workflows/tests.yml contains compileall bytecode check and pip caching."""
    wf_text = (REPO_ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "cache: 'pip'" in wf_text
    assert "compileall" in wf_text


def test_pyproject_ecosystem_urls():
    """Verify pyproject.toml declares Security, Third-Party Licenses, Marketing Log, Parent Org, and Ecosystem."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    urls = data.get("project", {}).get("urls", {})
    assert "Security" in urls
    assert "Third-Party Licenses" in urls
    assert "Marketing Log" in urls
    assert "Parent Organization" in urls
    assert "Umbrella Ecosystem" in urls


def test_third_party_licenses_inventory():
    """Verify THIRD_PARTY_LICENSES.md exists, audits 100% permissive licenses, and documents dependencies."""
    tpl_file = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert tpl_file.is_file(), "THIRD_PARTY_LICENSES.md must exist in repo root"
    tpl_text = tpl_file.read_text(encoding="utf-8")
    assert "PSFL-2.0" in tpl_text
    assert "MIT" in tpl_text
    assert "Apache-2.0" in tpl_text
    assert "coma" in tpl_text
    assert "pytest" in tpl_text
    assert "ruff" in tpl_text
    assert "setuptools" in tpl_text
    assert "RunAsInvoker" in tpl_text
    assert "Zero-Egress" in tpl_text or "Zero Egress" in tpl_text


def test_marketing_log_personas_and_differentiation():
    """Verify MARKETING-LOG.txt defines 4 personas, search queries, and competitive matrix."""
    m_log = REPO_ROOT / "MARKETING-LOG.txt"
    assert m_log.is_file()
    m_text = m_log.read_text(encoding="utf-8")
    assert "Autonomous AI Agent Engineers" in m_text
    assert "Multi-Agent Swarm & Handoff Developers" in m_text
    assert "Enterprise Tooling, Safety & Governance Compliance Officers" in m_text
    assert "Open-Source AI Tool Builders & Local-First Developers" in m_text
    assert "LangGraph" in m_text
    assert "CrewAI" in m_text
    assert "AutoGen" in m_text


def test_readme_canonical_invariant_ids_parity():
    """Verify both English and German READMEs carry canonical Invariant IDs INV-LOCAL-01 to INV-SLA-10."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    invariant_ids = [
        "INV-LOCAL-01",
        "INV-SEC-02",
        "INV-GATE-03",
        "INV-SYNC-04",
        "INV-CONT-05",
        "INV-STATE-06",
        "INV-PROC-07",
        "INV-CI-08",
        "INV-CONC-09",
        "INV-SLA-10",
    ]

    for inv_id in invariant_ids:
        assert inv_id in readme_en, f"Missing {inv_id} in README.md"
        assert inv_id in readme_de, f"Missing {inv_id} in README_de.md"


def test_pytest_ini_addopts_and_gitignore_hardening():
    """Verify pyproject.toml contains pytest addopts and .gitignore contains multi-host and lock patterns."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    pytest_ini = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    assert pytest_ini.get("addopts") == "-ra -v", "pytest addopts must be '-ra -v'"

    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "*-conflict-*" in gitignore_text
    assert "*.sync-conflict-*" in gitignore_text
    assert "*-WORKSTATION*" in gitignore_text
    assert "*-ASUS-GEI*" in gitignore_text
    assert "LOCK.permissions.json" in gitignore_text
    assert ".pytest_cache/" in gitignore_text
    assert "wheelhouse/" in gitignore_text

    security_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "lukas@open-bricks.org" in security_text


def test_readme_badge_matrix_completeness():
    """Verify both English and German READMEs feature modernized badge suites."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    # Badges present in English README
    assert "security%20SLA" in readme_en
    assert "third--party%20licenses" in readme_en
    assert "marketing%20log" in readme_en
    assert "Zero--Egress" in readme_en

    # Badges present in German README
    assert "Sicherheits--SLA" in readme_de
    assert "Drittanbieter--Lizenzen" in readme_de
    assert "Marketing--Log" in readme_de
    assert "Zero--Egress" in readme_de


def test_package_version_and_documentation_parity():
    """Verify single-source version 0.1.3 is consistent across __init__, pyproject, CHANGELOG, and README badges."""
    version = getattr(llmauto, "__version__", None)
    assert version == "0.1.3"

    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.1.3] - 2026-09-20" in changelog_text

    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    assert "badge/version-0.1.3-blue.svg" in readme_en
    assert "badge/Version-0.1.3-blue.svg" in readme_de


def test_statutory_notice_bgb_521_and_license():
    """Verify § 521 BGB statutory disclaimer and MIT notice are present in both READMEs."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in [readme_en, readme_de]:
        assert "521 BGB" in readme
        assert "Vorsatz und grobe Fahrlässigkeit" in readme
        assert "MIT License" in readme or "MIT-Lizenz" in readme

    assert (REPO_ROOT / "NOTICE").is_file(), "NOTICE file must exist in repo root"
    notice_text = (REPO_ROOT / "NOTICE").read_text(encoding="utf-8")
    assert "Lukas Geiger" in notice_text
    assert "ellmos-ai" in notice_text
    assert "open-bricks" in notice_text

    pyproject_file = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    license_files = data.get("project", {}).get("license-files", [])
    assert "NOTICE" in license_files
    assert "THIRD_PARTY_LICENSES.md" in license_files


def test_readme_target_personas_and_comparative_matrix():
    """Verify Section 4 personas [PERSONA-01]..[PERSONA-04] and Section 5 comparative matrix."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for p_id in ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]:
        assert p_id in readme_en, f"Missing {p_id} in README.md"
        assert p_id in readme_de, f"Missing {p_id} in README_de.md"

    for tool in ["LangGraph", "CrewAI", "AutoGen", "OpenClaw"]:
        assert tool in readme_en, f"Missing {tool} comparison in README.md"
        assert tool in readme_de, f"Missing {tool} comparison in README_de.md"


def test_mermaid_diagrams_no_semicolons():
    """Verify Mermaid diagrams in README.md and README_de.md contain no semicolons at end of lines."""
    for path in [REPO_ROOT / "README.md", REPO_ROOT / "README_de.md"]:
        text = path.read_text(encoding="utf-8")
        in_mermaid = False
        for line_no, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```mermaid"):
                in_mermaid = True
                continue
            if in_mermaid and stripped.startswith("```"):
                in_mermaid = False
                continue
            if in_mermaid:
                assert not stripped.endswith(";"), (
                    f"Semicolon found at end of mermaid line {line_no} in {path.name}: {stripped}"
                )


def test_all_ci_workflows_timeout_and_concurrency():
    """Verify all GitHub Actions workflows define concurrency controls and job timeouts."""
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    workflow_files = list(workflows_dir.glob("*.yml"))
    assert len(workflow_files) >= 5, "Must have at least 5 workflow definitions"

    for wf_file in workflow_files:
        content = wf_file.read_text(encoding="utf-8")
        assert "concurrency:" in content, f"Workflow {wf_file.name} missing concurrency block"
        assert "cancel-in-progress: true" in content, f"Workflow {wf_file.name} missing cancel-in-progress"
        assert "timeout-minutes:" in content, f"Workflow {wf_file.name} missing timeout-minutes"


def test_welcome_workflow_version():
    """Verify welcome.yml uses first-interaction@v3."""
    wf_text = (REPO_ROOT / ".github" / "workflows" / "welcome.yml").read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in wf_text


def test_pyproject_notice_url_and_norecursedirs():
    """Verify pyproject.toml declares Notice URL and protects test directories in norecursedirs."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    urls = data.get("project", {}).get("urls", {})
    assert "Notice" in urls
    assert urls["Notice"] == "https://github.com/ellmos-ai/MarbleRun/blob/main/NOTICE"

    pytest_ini = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    norecursedirs = pytest_ini.get("norecursedirs", [])
    assert "__pycache__" in norecursedirs
    assert ".venv" in norecursedirs


def test_third_party_licenses_audit_recency():
    """Verify THIRD_PARTY_LICENSES.md reflects 2026-09-22 audit."""
    tpl_text = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
    assert "**Audited:** 2026-09-22" in tpl_text


def test_changelog_unreleased_hygiene_entry():
    """Verify CHANGELOG.md contains unreleased section for Pfad A hygiene hardening."""
    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog_text
    assert "Pfad A Repository Hygiene" in changelog_text


def test_gitignore_hardened_tokens():
    """Verify .gitignore contains canonical lock and multi-host device tokens."""
    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "LOCK.condition.*" in gitignore_text
    assert ".automation-lock" in gitignore_text
    assert "*-WORKSTATION-LG*" in gitignore_text
    assert "*-ASUS*" in gitignore_text
    assert "*-LAPTOP*" in gitignore_text
    assert "*-Mac Studio*" in gitignore_text
    assert "*-MacBook*" in gitignore_text
    assert "*.rej" in gitignore_text
    assert ".hypothesis/" in gitignore_text
