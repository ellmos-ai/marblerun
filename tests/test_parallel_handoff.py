"""Regression tests for race-free parallel worker handoffs."""
from llmauto.core.state import ChainState
from llmauto.modes import chain


def _result():
    return {
        "success": True,
        "output": "",
        "stderr": "",
        "returncode": 0,
        "duration_s": 0,
        "model": "test",
    }


def test_parallel_workers_isolate_handoffs_and_merge_in_link_order(tmp_path, monkeypatch):
    state = ChainState("parallel", tmp_path)
    baseline = "# Baseline\nController assignment\n"
    state.write_handoff(baseline)
    monkeypatch.setattr(chain, "LOG_DIR", tmp_path / "logs")
    prompts = {}

    class FakeRunner:
        def __init__(self, worker_name):
            self.worker_name = worker_name

        def run(self, prompt):
            prompts[self.worker_name] = prompt
            state.get_link_handoff_file(self.worker_name).write_text(
                f"Report {self.worker_name}\n", encoding="utf-8"
            )
            return _result()

    def fake_build_runner(backend, model=None, **kwargs):
        return FakeRunner(model)

    monkeypatch.setattr(chain, "build_runner", fake_build_runner)
    links = [
        {"name": "worker-a", "role": "worker", "prompt": "Do A", "model": "worker-a"},
        {"name": "worker-b", "role": "worker", "prompt": "Do B", "model": "worker-b"},
    ]

    result = chain.run_parallel_workers(
        "parallel",
        links,
        {},
        state,
        {"default_backend": "test"},
        tmp_path,
    )

    assert set(result) == {"worker-a", "worker-b"}
    assert "handoff_worker-a.md" in prompts["worker-a"]
    assert "handoff_worker-b.md" in prompts["worker-b"]
    assert "gemeinsame Handoff-Datei" in prompts["worker-a"]
    assert state.get_link_handoff_file("worker-a").read_text(encoding="utf-8") == "Report worker-a\n"
    assert state.get_link_handoff_file("worker-b").read_text(encoding="utf-8") == "Report worker-b\n"
    merged = state.get_handoff()
    assert "## Parallel Worker: worker-a" in merged
    assert "## Parallel Worker: worker-b" in merged
    assert merged.index("worker-a") < merged.index("worker-b")


def test_parallel_skip_stays_isolated_and_baseline_survives(tmp_path, monkeypatch):
    state = ChainState("parallel", tmp_path)
    baseline = "# Baseline\nController assignment\n"
    state.write_handoff(baseline)
    monkeypatch.setattr(chain, "LOG_DIR", tmp_path / "logs")

    class FakeRunner:
        def __init__(self, worker_name):
            self.worker_name = worker_name

        def run(self, prompt):
            state.get_link_handoff_file(self.worker_name).write_text(
                "SKIPPED - nicht zustaendig\n", encoding="utf-8"
            )
            return _result()

    monkeypatch.setattr(
        chain,
        "build_runner",
        lambda backend, model=None, **kwargs: FakeRunner(model),
    )
    links = [{"name": "worker-a", "role": "worker", "prompt": "Do A", "model": "worker-a"}]

    chain.run_parallel_workers(
        "parallel",
        links,
        {},
        state,
        {"default_backend": "test"},
        tmp_path,
    )

    assert state.get_handoff() == baseline
    assert "SKIPPED" in state.get_link_handoff_file("worker-a").read_text(encoding="utf-8")


def test_parallel_shared_handoff_write_fails_closed(tmp_path, monkeypatch):
    state = ChainState("parallel", tmp_path)
    baseline = "# Baseline\nController assignment\n"
    state.write_handoff(baseline)
    monkeypatch.setattr(chain, "LOG_DIR", tmp_path / "logs")

    class FakeRunner:
        def run(self, prompt):
            # Simulate an old/generic worker that ignored the injected path.
            state.write_handoff("SKIPPED - shared overwrite\n")
            return _result()

    monkeypatch.setattr(chain, "build_runner", lambda *args, **kwargs: FakeRunner())
    links = [{"name": "worker-a", "role": "worker", "prompt": "Do A", "model": "worker-a"}]

    chain.run_parallel_workers(
        "parallel",
        links,
        {},
        state,
        {"default_backend": "test"},
        tmp_path,
    )

    assert state.get_handoff() == baseline
