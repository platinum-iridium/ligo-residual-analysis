"""
Mechanical tests for Platinum-Iridium archival guarantees.

These tests prove:
- Import safety (no enforcement at import time)
- Strict dependency enforcement
- Whitening path determinism
- Stable forensic artifact generation
- Bit-for-bit reproducibility of LATEST artifact
"""
import os
import sys
import json
import importlib.util
from unittest.mock import MagicMock
import pytest


def load_pipeline(path="ligo_residual_analysis_v1_2_6.py"):
    spec = importlib.util.spec_from_file_location("pipeline", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["pipeline"] = module
    spec.loader.exec_module(module)
    return module


pipeline = load_pipeline()


class TestPlatinumIridiumControls:
    def setup_method(self):
        # reset mutable globals
        pipeline.STRICT_ARCHIVAL = True
        pipeline._WHITEN_MODES_SEEN = set()
        pipeline._WHITEN_FALLBACK_REASON = None
        pipeline._WHITEN_FALLBACK_LOGGED = False

        # avoid environment dependence for most tests:
        pipeline.CODE_SOURCE_MODE = "file"
        pipeline.CODE_SHA256 = "test_sha"

    def test_01_import_is_safe(self):
        # passes if module import didn't raise
        assert pipeline is not None

    def test_02_strict_mode_refuses_version_mismatch(self):
        orig = dict(pipeline.PINNED_VERSIONS)
        try:
            pipeline.PINNED_VERSIONS["gwpy"] = "999.0.0"
            with pytest.raises(RuntimeError, match="Dependency version mismatch"):
                pipeline.enforce_dependency_versions()
        finally:
            pipeline.PINNED_VERSIONS = orig

    def test_03_strict_mode_refuses_whitening_fallback(self):
        mock_ts = MagicMock()
        mock_ts.whiten.side_effect = TypeError("Bad kwarg")
        with pytest.raises(RuntimeError, match="Whitening fallback not allowed"):
            pipeline.whiten_pinned(mock_ts, MagicMock())

    def test_04_sorted_whitening_modes(self):
        mock_ts = MagicMock()
        mock_ts.whiten.return_value = "ok"
        pipeline.whiten_pinned(mock_ts, MagicMock())
        assert sorted(list(pipeline._WHITEN_MODES_SEEN)) == ["pinned_kwargs"]

    def test_05_file_based_execution_enforced(self):
        pipeline.CODE_SOURCE_MODE = "interactive"
        with pytest.raises(RuntimeError, match="file-based execution"):
            pipeline.enforce_file_based_execution()

    def test_06_preregistration_verified_in_strict(self):
        # Should match baked commitment
        h = pipeline.verify_window_preregistration()
        assert h == pipeline.PREREG_HASH16

    def test_07_stable_artifact_has_no_timestamp(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        pipeline._WHITEN_MODES_SEEN = set()

        pipeline.write_run_record("fp", "hash", {"a": 1}, {"r": 2}, {}, {"seed": 1})

        assert (tmp_path / "run_record_LATEST.json").exists()
        data = json.loads((tmp_path / "run_record_LATEST.json").read_text(encoding="utf-8"))
        assert "utc_timestamp" not in data
        assert data["execution_flags"]["whitening_modes_seen"] == []

    def test_08_latest_is_bit_identical_across_runs(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        pipeline._WHITEN_MODES_SEEN = {"pinned_kwargs"}
        pipeline.write_run_record("fp", "hash", {"a": 1}, {"r": 2}, {}, {"seed": 1})
        b1 = (tmp_path / "run_record_LATEST.json").read_bytes()

        # second run (audit timestamp changes, stable must not)
        pipeline._WHITEN_MODES_SEEN = {"pinned_kwargs"}
        pipeline.write_run_record("fp", "hash", {"a": 1}, {"r": 2}, {}, {"seed": 1})
        b2 = (tmp_path / "run_record_LATEST.json").read_bytes()

        assert b1 == b2
