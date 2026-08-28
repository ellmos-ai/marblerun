r"""Lifecycle-safe stdio wrapper for the local Roblox Studio MCP server.

The wrapper forwards JSON-RPC unchanged, persists image responses, and owns
the complete child-process tree.  When the MCP client closes stdin, the
Roblox MCP child is stopped as well instead of remaining as an orphan.

Set ``MARBLERUN_EVIDENCE_ROOT`` to a project's ``docs/playtests`` directory.
Screenshots then land in a dated ``YYYY-MM-DD_marblerun`` subdirectory.  With
no explicit root, the wrapper falls back to
``%LOCALAPPDATA%\Roblox\mcp-screenshots``.
"""

import base64
import json
import os
import re
import subprocess
import sys
import threading
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path

LOCALAPPDATA = os.environ.get(
    "LOCALAPPDATA", str(Path.home() / "AppData" / "Local")
)
MCP_BAT = Path(LOCALAPPDATA) / "Roblox" / "mcp.bat"
VERSIONS_ROOT = Path(LOCALAPPDATA) / "Roblox" / "Versions"
FALLBACK_SCREENSHOT_DIR = Path(LOCALAPPDATA) / "Roblox" / "mcp-screenshots"

pending_calls = {}
pending_lock = threading.Lock()


def resolve_launch_command(mcp_bat=None, versions_root=None):
    """Resolve a current StudioMCP executable despite a stale generated BAT."""
    bat_path = Path(mcp_bat) if mcp_bat is not None else MCP_BAT
    versions_path = (
        Path(versions_root) if versions_root is not None else VERSIONS_ROOT
    )

    if bat_path.exists():
        try:
            bat_text = bat_path.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r'([A-Za-z]:\\[^"\r\n]+\\StudioMCP\.exe)', bat_text)
            if match:
                candidate = Path(match.group(1))
                if candidate.exists():
                    return [str(candidate)]
        except OSError:
            pass

    if versions_path.exists():
        candidates = sorted(
            versions_path.glob("version-*/StudioMCP.exe"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return [str(candidates[0])]

    if bat_path.exists():
        return ["cmd.exe", "/c", str(bat_path)]
    return None


def evidence_dir(now=None):
    """Return and create the persistent screenshot directory for this run."""
    root = os.environ.get("MARBLERUN_EVIDENCE_ROOT")
    if root:
        current = now or datetime.now()
        target = Path(root).expanduser() / f"{current:%Y-%m-%d}_marblerun"
    else:
        target = FALLBACK_SCREENSHOT_DIR
    target.mkdir(parents=True, exist_ok=True)
    return target


def log_debug(message):
    """Write diagnostics to a file; MCP stdout/stderr remain protocol-only."""
    try:
        debug_log = evidence_dir() / "_wrapper.log"
        with debug_log.open("a", encoding="utf-8") as handle:
            handle.write(f"[{datetime.now().isoformat()}] {message}\n")
    except OSError:
        pass


def save_screenshot(
    b64_data,
    request_id,
    tool_call_desc="",
    output_dir=None,
    mime_type="image/png",
):
    """Persist one base64 image and a small provenance sidecar."""
    target = Path(output_dir) if output_dir else evidence_dir()
    target.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(mime_type, ".img")
    image_path = target / f"{stamp}{extension}"
    meta_path = target / f"{stamp}.json"
    raw = base64.b64decode(b64_data, validate=True)
    image_path.write_bytes(raw)
    meta = {
        "timestamp": stamp,
        "request_id": request_id,
        "tool_call_desc": tool_call_desc,
        "size_bytes": len(raw),
        "iso_date": datetime.now().isoformat(),
        "image_path": str(image_path.resolve()),
        "mime_type": mime_type,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log_debug(f"Saved screenshot {image_path} ({len(raw)} bytes)")
    return image_path, meta_path


def extract_screenshots(obj, request_id, tool_call_desc=""):
    """Recursively persist image content contained in an MCP response."""
    count = 0
    if isinstance(obj, dict):
        if obj.get("type") == "image" and isinstance(obj.get("data"), str):
            try:
                save_screenshot(
                    obj["data"],
                    request_id,
                    tool_call_desc,
                    mime_type=obj.get("mimeType", "image/png"),
                )
                count += 1
            except (OSError, ValueError) as error:
                log_debug(f"Failed to save screenshot: {error}")
        for value in obj.values():
            count += extract_screenshots(value, request_id, tool_call_desc)
    elif isinstance(obj, list):
        for item in obj:
            count += extract_screenshots(item, request_id, tool_call_desc)
    return count


def process_stdin_to_child(child_stdin, eof_event):
    """Forward stdin and signal parent EOF so the child tree can be stopped."""
    try:
        for line in sys.stdin.buffer:
            try:
                message = json.loads(line.decode("utf-8", errors="replace").strip())
                if message.get("method") == "tools/call":
                    params = message.get("params", {})
                    tool_name = params.get("name", "")
                    if "screen_capture" in tool_name:
                        request_id = message.get("id")
                        with pending_lock:
                            pending_calls[request_id] = {
                                "desc": json.dumps(params.get("arguments", {}))[:200],
                                "tool": tool_name,
                            }
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                pass
            child_stdin.write(line)
            child_stdin.flush()
    except (BrokenPipeError, OSError) as error:
        log_debug(f"stdin->child closed: {error}")
    finally:
        with suppress(OSError):
            child_stdin.close()
        eof_event.set()


def process_child_to_stdout(child_stdout):
    """Forward child stdout and capture images from matching responses."""
    try:
        for line in child_stdout:
            try:
                message = json.loads(line.decode("utf-8", errors="replace").strip())
                request_id = message.get("id")
                with pending_lock:
                    call_info = pending_calls.pop(request_id, None)
                if call_info and "result" in message:
                    extract_screenshots(
                        message["result"], request_id, call_info.get("desc", "")
                    )
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                pass
            sys.stdout.buffer.write(line)
            sys.stdout.buffer.flush()
    except (BrokenPipeError, OSError) as error:
        log_debug(f"child->stdout closed: {error}")


def terminate_process_tree(child, timeout=5):
    """Stop the owned MCP child and descendants, then verify process exit."""
    if child.poll() is not None:
        return child.returncode

    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.run(
            ["taskkill", "/PID", str(child.pid), "/T", "/F"],
            check=False,
            capture_output=True,
            creationflags=creationflags,
        )
    else:
        child.terminate()

    try:
        return child.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        child.kill()
        return child.wait(timeout=timeout)


def main():
    launch_command = resolve_launch_command()
    if launch_command is None:
        print(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32000,
                        "message": "No installed Roblox Studio MCP server found",
                    },
                }
            ),
            flush=True,
        )
        return 1

    log_debug(f"Wrapper started. command = {launch_command}")
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    child = subprocess.Popen(
        launch_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
        creationflags=creationflags,
    )
    eof_event = threading.Event()
    threads = [
        threading.Thread(
            target=process_stdin_to_child,
            args=(child.stdin, eof_event),
            daemon=True,
        ),
        threading.Thread(
            target=process_child_to_stdout,
            args=(child.stdout,),
            daemon=True,
        ),
    ]

    def pipe_stderr():
        try:
            for line in child.stderr:
                sys.stderr.buffer.write(line)
                sys.stderr.buffer.flush()
        except (BrokenPipeError, OSError):
            pass

    threads.append(threading.Thread(target=pipe_stderr, daemon=True))
    for thread in threads:
        thread.start()

    while child.poll() is None:
        if eof_event.wait(0.1):
            terminate_process_tree(child)
            break
        time.sleep(0.05)

    return_code = child.wait()
    threads[1].join(timeout=2)
    log_debug(f"Child exited with rc={return_code}")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
