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
    assert project.get("license-files") == ["LICENSE"]
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
    assert "Last-checked: 2026-09-08" in llms_text, "llms.txt must have current Last-checked timestamp"
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
    assert "Sichere Prozess-Scoping" in readme_de
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
    """Verify both English and German READMEs define 14-point quick navigation."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "## Quick Navigation" in readme_en
    assert "## Schnellnavigation" in readme_de

    anchors_en = [
        "#what-is-llmauto",
        "#visual-showcase--execution-flow",
        "#tactical-round-execution--sequence-flow",
        "#core-capabilities--security-invariants",
        "#chain-patterns--role-matrix",
        "#installation",
        "SECURITY.md",
        "#license",
    ]
    for anchor in anchors_en:
        assert anchor in readme_en, f"Missing anchor '{anchor}' in README.md"

    anchors_de = [
        "#was-ist-llmauto",
        "#visuelle-galerie--ausfuehrungsfluss",
        "#taktischer-rundenablauf--sequenzdiagramm",
        "#kernfaehigkeiten--sicherheitsinvarianten",
        "#chain-muster--rollenmatrix",
        "#installation",
        "SECURITY.md",
        "#lizenz",
    ]
    for anchor in anchors_de:
        assert anchor in readme_de, f"Missing anchor '{anchor}' in README_de.md"


def test_security_policy_slas_and_contacts():
    """Verify SECURITY.md includes supported versions, SLAs, and security@open-bricks.org."""
    sec_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "security@open-bricks.org" in sec_text
    assert "48 hours" in sec_text or "48 Stunden" in sec_text
    assert "5 business days" in sec_text or "5 Werktagen" in sec_text
    assert "Supported Versions" in sec_text
    assert "0.1.x" in sec_text


def test_marketing_log_and_changelog_recency():
    """Verify MARKETING-LOG.txt exists and CHANGELOG.md has 2026-09-08 entry."""
    m_log = REPO_ROOT / "MARKETING-LOG.txt"
    assert m_log.is_file(), "MARKETING-LOG.txt must exist in repo root"
    m_text = m_log.read_text(encoding="utf-8")
    assert "2026-09-08" in m_text
    assert "ellmos-ai/marblerun" in m_text

    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "2026-09-08" in changelog_text


def test_ci_workflow_compileall_and_caching():
    """Verify .github/workflows/tests.yml contains compileall bytecode check and pip caching."""
    wf_text = (REPO_ROOT / ".github" / "workflows" / "tests.yml").read_text(encoding="utf-8")
    assert "cache: 'pip'" in wf_text
    assert "compileall" in wf_text


def test_pyproject_ecosystem_urls():
    """Verify pyproject.toml declares Security, Parent Organization, and Umbrella Ecosystem."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    urls = data.get("project", {}).get("urls", {})
    assert "Security" in urls
    assert "Parent Organization" in urls
    assert "Umbrella Ecosystem" in urls
