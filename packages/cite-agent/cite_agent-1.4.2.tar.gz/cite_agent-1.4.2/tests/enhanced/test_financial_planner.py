import os

import pytest

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent


def test_plan_financial_request_extracts_tickers_and_metrics():
    agent = EnhancedNocturnalAgent()
    tickers, metrics = agent._plan_financial_request(
        "Compare revenue and net income for Apple and Microsoft"
    )
    assert tickers == ["AAPL", "MSFT"]
    assert metrics == ["revenue", "netIncome"]


def test_plan_financial_request_uses_session_history():
    agent = EnhancedNocturnalAgent()
    session_key = "user:conv"
    agent._session_topics[session_key] = {"metrics": ["netIncome"]}

    tickers, metrics = agent._plan_financial_request(
        "How is Apple doing lately?", session_key=session_key
    )
    assert tickers == ["AAPL"]
    assert metrics == ["netIncome"]


def test_plan_financial_request_defaults_when_ambiguous():
    agent = EnhancedNocturnalAgent()
    tickers, metrics = agent._plan_financial_request("Tell me about the market")
    assert tickers == []
    assert metrics == ["revenue", "grossProfit"]


def test_check_query_budget_enforces_limit():
    agent = EnhancedNocturnalAgent()
    agent.daily_query_limit = 2
    agent.per_user_query_limit = 2

    assert agent._check_query_budget("tester")
    agent._record_query_usage("tester")
    agent._record_query_usage("tester")
    assert not agent._check_query_budget("tester")


def test_format_archive_summary_compacts_response():
    agent = EnhancedNocturnalAgent()
    summary = agent._format_archive_summary(
        "What is Tesla's revenue?",
        "Tesla reported $96.77B in trailing twelve month revenue with 15% YoY growth.",
        {"financial": {"TSLA": {"value": 96770000000}}},
    )
    assert summary["question"].startswith("What is Tesla")
    assert "Tesla" in summary["summary"]
    assert summary["citations"]
@pytest.fixture(autouse=True)
def redirect_archive(tmp_path, monkeypatch):
    monkeypatch.setenv("CITE_AGENT_ARCHIVE_DIR", str(tmp_path / "archive"))
