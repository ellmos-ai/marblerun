from pathlib import Path

from llmauto.core.state import ChainState


def test_documented_signals_match_runtime(tmp_path):
    state = ChainState("synthetic", base_dir=tmp_path)
    for name in ("pause.req", "steer.req", "stop.req"):
        (state.state_dir / name).write_text("synthetic", encoding="utf-8")
    assert not state.is_stop_requested()
    assert not state.is_pause_requested()
    assert state.peek_steer_requests() == []
    state.request_pause("synthetic")
    state.request_steer("synthetic")
    state.request_stop("synthetic")
    assert state.pause_file.name == "PAUSE.json"
    assert state.steer_file.name == "steer_queue.json"
    assert state.stop_file.name == "STOP"
    assert state.is_pause_requested()
    assert state.peek_steer_requests()
    assert state.is_stop_requested()


def test_diagrams_use_the_runtime_signal_names():
    root = Path(__file__).resolve().parents[1]
    for name in ("README.md", "README_de.md"):
        text = (root / name).read_text(encoding="utf-8")
        assert "stateDiagram-v2" in text
        for signal in ("PAUSE.json", "steer_queue.json", "STOP"):
            assert signal in text
        for obsolete in ("pause.req", "steer.req", "stop.req"):
            # Only the explicit negation ("... are not control inputs") may name the obsolete files.
            for line in text.splitlines():
                if obsolete in line:
                    assert "not control inputs" in line or "keine Steuereingaben" in line, line
