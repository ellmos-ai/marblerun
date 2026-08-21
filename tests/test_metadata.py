"""Metadata, manifest, and discoverability parity tests for MarbleRun / llmauto."""

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
    """Verify pyproject.toml contains mandatory project metadata and ruff settings."""
    pyproject_file = REPO_ROOT / "pyproject.toml"
    assert pyproject_file.exists(), "pyproject.toml must exist"

    data = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
    project = data.get("project", {})

    assert project.get("name") == "llmauto"
    assert "MarbleRun" in project.get("description", "")
    assert project.get("license", {}).get("text") == "MIT"
    assert "urls" in project
    assert project["urls"].get("Homepage") == "https://github.com/ellmos-ai/MarbleRun"
    assert project["urls"].get("Repository") == "https://github.com/ellmos-ai/MarbleRun"

    # Ruff section
    assert "tool" in data and "ruff" in data["tool"], "pyproject.toml must configure [tool.ruff]"


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
    assert manifest.get("source_of_truth", {}).get("repository") == "https://github.com/ellmos-ai/MarbleRun"


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
    ]
    for rel_path in required_files:
        p = REPO_ROOT / rel_path
        assert p.is_file(), f"Missing required file: {rel_path}"


def test_llms_txt_and_badge_discovery_parity():
    """Verify llms.txt and READMEs carry consistent ecosystem anchors."""
    llms_file = REPO_ROOT / "llms.txt"
    assert llms_file.exists()
    llms_text = llms_file.read_text(encoding="utf-8")
    assert "Last-checked: 2026-08-21" in llms_text, "llms.txt must have current Last-checked timestamp"
    assert "https://github.com/ellmos-ai/MarbleRun" in llms_text
    assert "llmauto" in llms_text

    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in [readme_en, readme_de]:
        assert "ellmos--ai-blue.svg" in readme or "ellmos-ai" in readme
        assert "open--bricks-orange.svg" in readme or "open-bricks" in readme
        assert "llms.txt" in readme
