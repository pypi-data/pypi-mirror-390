import json
from pathlib import Path

from cite_agent.conversation_archive import ConversationArchive


def test_conversation_archive_round_trip(tmp_path):
    archive = ConversationArchive(root=tmp_path / "archive")

    archive.record_entry(
        "user-1",
        "session-1",
        "What is Tesla's revenue?",
        "Tesla reported $96.77B trailing revenue with SEC citations.",
        ["finsight_api"],
        ["10-K 2024"],
    )

    archive.record_entry(
        "user-1",
        "session-1",
        "Any recent papers on transformers?",
        "Found 3 papers with verified DOIs.",
        ["archive_api"],
        ["Attention Is All You Need"],
    )

    context = archive.get_recent_context("user-1", "session-1")
    assert "Archived context" in context
    assert "Tesla" in context
    assert "verified dois" in context.lower()

    files = archive.list_conversations()
    assert files

    # Ensure contents persisted as JSON
    path = Path(tmp_path / "archive").glob("*.json")
    first_file = next(path)
    payload = json.loads(first_file.read_text())
    assert isinstance(payload, list)
    assert len(payload) == 2
