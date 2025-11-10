import asyncio

import pytest

from scripts.autonomy_harness import (
    execute_scenarios,
    run_finance_showcase,
    run_local_file_showcase,
    run_research_showcase,
    run_archive_resume_showcase,
    run_ambiguous_query_showcase,
    run_data_analysis_showcase,
    run_repo_overview_showcase,
    run_data_pipeline_showcase,
    run_self_service_shell_showcase,
    run_conversation_memory_showcase,
    run_multi_hop_research_showcase,
    run_repo_refactor_showcase,
)


@pytest.mark.asyncio
async def test_finance_showcase_runs_with_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_finance_showcase()
    assert result["finance_calls"] == [("AAPL", ("revenue", "netIncome")), ("MSFT", ("revenue", "netIncome"))]
    assert "finsight_api" in result["response"].tools_used


@pytest.mark.asyncio
async def test_research_showcase_produces_citation(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_research_showcase()
    assert result["response"].tools_used == ["archive_api"]


@pytest.mark.asyncio
async def test_archive_resume_persists_context(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_archive_resume_showcase()
    assert result["archive_files"]
    assert "Archived context" in result["archive_context"]


@pytest.mark.asyncio
async def test_execute_scenarios_filters_and_serialises(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    results = await execute_scenarios(["ambiguous"])
    scenario_keys = {name for name in results.keys() if not name.startswith("_")}
    assert scenario_keys == {"ambiguous"}
    payload = results["ambiguous"]
    assert isinstance(payload["elapsed_seconds"], float)


@pytest.mark.asyncio
async def test_local_file_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_local_file_showcase()
    assert result["response"].response


@pytest.mark.asyncio
async def test_data_analysis_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_data_analysis_showcase()
    assert "csv_preview" in result
    assert "mean" in result["response"].response
    checks = result["quality_checks"]
    assert checks["contains_mean"] and checks["contains_stdev"]


@pytest.mark.asyncio
async def test_repo_overview_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_repo_overview_showcase()
    snapshot = result["repo_snapshot"]
    assert snapshot["top_dirs"]
    assert "cite_agent" in snapshot["top_dirs"]
    assert "shell_execution" in result["response"].tools_used or result["ledger"]
    assert all(result["quality_checks"].values())


@pytest.mark.asyncio
async def test_data_pipeline_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_data_pipeline_showcase()
    assert result["response"].response.startswith("I inspected the sales dataset")
    assert result["quality_checks"]["reports_top_performer"]


@pytest.mark.asyncio
async def test_self_service_shell_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_self_service_shell_showcase()
    q = result["quality_checks"]
    assert q["auto_executed"]
    assert q["ls_command"]


@pytest.mark.asyncio
async def test_conversation_memory_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_conversation_memory_showcase()
    checks = result["quality_checks"]
    assert checks["memory_recorded"]
    assert checks["memory_recited"]
    assert checks["archive_written"]


@pytest.mark.asyncio
async def test_multi_hop_research_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_multi_hop_research_showcase()
    assert "archive_api" in result["response"].tools_used or result["ledger"]
    checks = result["quality_checks"]
    assert checks["mentions_revenue"] and checks["mentions_net_income"] and checks["mentions_papers"]


@pytest.mark.asyncio
async def test_repo_refactor_showcase(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
    result = await run_repo_refactor_showcase()
    assert "Refactor summary" in result["response"].response
    assert all(result["quality_checks"].values())
