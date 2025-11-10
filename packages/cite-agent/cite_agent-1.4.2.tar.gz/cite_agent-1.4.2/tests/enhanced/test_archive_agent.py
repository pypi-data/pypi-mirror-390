"""Tests for Archive integration in the enhanced agent."""

import pytest

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent


class _MockResponse:
    def __init__(self, status: int, payload=None):
        self.status = status
        self._payload = payload or {}
        self._text = ""

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        return self._payload

    async def text(self):
        return self._text


class _MockSession:
    def __init__(self, response: _MockResponse):
        self.response = response
        self.post_calls = []

    def post(self, url, json=None, headers=None, **kwargs):
        self.post_calls.append({
            "url": url,
            "json": json,
            "headers": headers,
            "extra": kwargs,
        })
        return self.response


@pytest.mark.asyncio
async def test_call_archive_api_success(monkeypatch):
    agent = EnhancedNocturnalAgent()

    mock_session = _MockSession(_MockResponse(200, {"result": "ok"}))
    agent.session = mock_session
    agent.archive_base_url = "http://127.0.0.1:8000/api"

    async def backend_ready():
        return True, ""

    monkeypatch.setattr(agent, "_ensure_backend_ready", backend_ready)

    payload = {"query": "graph learning", "limit": 5}
    result = await agent._call_archive_api("search", payload)

    assert result == {"result": "ok"}
    assert len(mock_session.post_calls) == 1
    call = mock_session.post_calls[0]
    assert call["url"] == "http://127.0.0.1:8000/api/search"
    assert call["json"] == payload
    assert call["extra"] == {"timeout": 30}
    assert call["headers"]["X-API-Key"] == "demo-key-123"
    assert call["headers"]["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_call_archive_api_handles_error(monkeypatch):
    agent = EnhancedNocturnalAgent()

    error_response = _MockResponse(500)
    error_response._text = "internal error"
    mock_session = _MockSession(error_response)
    agent.session = mock_session
    agent.archive_base_url = "http://127.0.0.1:8000/api"

    async def backend_ready():
        return True, ""

    monkeypatch.setattr(agent, "_ensure_backend_ready", backend_ready)

    result = await agent._call_archive_api("search", {"query": "x"})

    assert "error" in result
    assert result["error"] == "Archive API error: 500"
