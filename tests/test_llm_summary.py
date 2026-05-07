import json
import sys
import types
from pathlib import Path

from data_reconciliation_agent.llm_summary import build_llm_summary_input, build_summary_prompt, generate_llm_summary


def _trace() -> dict:
    return {
        "mode": "deterministic",
        "key_mode": "mapping_config",
        "source_path": "source.csv",
        "target_path": "target.csv",
        "source_row_count": 10,
        "target_row_count": 11,
        "key_checks": {
            "duplicate_key_row_count_source": 1,
            "duplicate_key_row_count_target": 2,
            "null_key_count_source": 0,
            "null_key_count_target": 1,
        },
        "record_comparison": {"matched_key_count": 8, "missing_in_target_count": 2, "unexpected_in_target_count": 3},
        "value_comparison": {"enabled": True, "mismatched_value_count": 4, "mismatched_field_counts": {"a -> b": 4}},
        "output_files": {"exceptions_written": ["missing_in_target.csv"]},
        "warnings": [],
        "blocking_errors": [],
    }


def test_build_llm_summary_input_extracts_high_level_facts() -> None:
    result = build_llm_summary_input(_trace())
    assert result["matched_key_count"] == 8
    assert result["mismatches_by_field"]["a -> b"] == 4


def test_build_summary_prompt_includes_non_authoritative_instruction() -> None:
    prompt = build_summary_prompt(build_llm_summary_input(_trace()))
    assert "Deterministic outputs are authoritative" in prompt
    assert "Do not invent findings" in prompt


def test_fallback_generation_writes_summary_without_api_key(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    trace_path = tmp_path / "reconciliation_trace.json"
    trace_path.write_text(json.dumps(_trace()), encoding="utf-8")
    result = generate_llm_summary(str(trace_path), str(tmp_path))
    assert result.summary_written is True
    assert result.external_llm_used is False
    assert result.provider == "deterministic_fallback"
    assert (tmp_path / "llm_summary.md").exists()
    text = (tmp_path / "llm_summary.md").read_text(encoding="utf-8")
    assert "Generated without an external LLM" in text
    assert "source_value" not in text


def test_api_key_set_but_openai_missing_falls_back(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "openai", None)
    trace_path = tmp_path / "reconciliation_trace.json"
    trace_path.write_text(json.dumps(_trace()), encoding="utf-8")

    result = generate_llm_summary(str(trace_path), str(tmp_path), provider="openai")

    assert result.external_llm_used is False
    assert result.provider == "deterministic_fallback"
    assert any("not installed" in warning for warning in result.warnings)


def test_mocked_openai_returns_text(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured["kwargs"] = kwargs
            return types.SimpleNamespace(output_text="## Executive summary\nMocked summary text")

    class FakeOpenAI:
        def __init__(self):
            self.responses = FakeResponses()

    fake_module = types.SimpleNamespace(OpenAI=FakeOpenAI)
    monkeypatch.setitem(sys.modules, "openai", fake_module)

    trace_path = tmp_path / "reconciliation_trace.json"
    trace_path.write_text(json.dumps(_trace()), encoding="utf-8")
    result = generate_llm_summary(str(trace_path), str(tmp_path), provider="openai")

    assert result.external_llm_used is True
    assert result.provider == "openai"
    text = (tmp_path / "llm_summary.md").read_text(encoding="utf-8")
    assert "Mocked summary text" in text
    prompt = captured["kwargs"]["input"][0]["content"][0]["text"]
    assert "source_value" not in prompt
    assert "target_value" not in prompt
