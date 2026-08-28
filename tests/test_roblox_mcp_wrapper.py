"""Regression tests for the lifecycle-safe Roblox Studio MCP wrapper."""

import base64
import json
import subprocess
import sys
from datetime import datetime

from scripts import roblox_mcp_wrapper as wrapper


def test_evidence_dir_uses_dated_project_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("MARBLERUN_EVIDENCE_ROOT", str(tmp_path))
    target = wrapper.evidence_dir(datetime(2026, 8, 28, 6, 0))
    assert target == tmp_path / "2026-08-28_marblerun"
    assert target.is_dir()


def test_save_screenshot_writes_png_and_provenance(tmp_path):
    png_bytes = b"\x89PNG\r\n\x1a\nfixture"
    png_path, meta_path = wrapper.save_screenshot(
        base64.b64encode(png_bytes).decode("ascii"),
        request_id=17,
        tool_call_desc='{"view": "game"}',
        output_dir=tmp_path,
    )

    assert png_path.read_bytes() == png_bytes
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    assert metadata["request_id"] == 17
    assert metadata["size_bytes"] == len(png_bytes)
    assert metadata["image_path"] == str(png_path.resolve())
    assert metadata["mime_type"] == "image/png"


def test_save_screenshot_uses_mime_appropriate_extension(tmp_path):
    image_path, metadata_path = wrapper.save_screenshot(
        base64.b64encode(b"jpeg-fixture").decode("ascii"),
        request_id=18,
        output_dir=tmp_path,
        mime_type="image/jpeg",
    )
    assert image_path.suffix == ".jpg"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["mime_type"] == "image/jpeg"


def test_launch_resolution_falls_back_to_latest_installed_mcp(tmp_path):
    older = tmp_path / "version-old" / "StudioMCP.exe"
    latest = tmp_path / "version-new" / "StudioMCP.exe"
    older.parent.mkdir()
    latest.parent.mkdir()
    older.write_bytes(b"old")
    latest.write_bytes(b"new")
    older.touch()
    latest.touch()
    older_mtime = older.stat().st_mtime - 10
    older_mtime_ns = int(older_mtime * 1_000_000_000)
    import os

    os.utime(older, ns=(older_mtime_ns, older_mtime_ns))

    command = wrapper.resolve_launch_command(
        mcp_bat=tmp_path / "missing.bat", versions_root=tmp_path
    )
    assert command == [str(latest)]


def test_terminate_process_tree_stops_owned_child():
    child = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wrapper.terminate_process_tree(child)
        assert child.poll() is not None
    finally:
        if child.poll() is None:
            child.kill()
