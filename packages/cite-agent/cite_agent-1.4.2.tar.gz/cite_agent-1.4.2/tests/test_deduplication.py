#!/usr/bin/env python3
"""Tests for paper deduplication"""

import pytest
from cite_agent.deduplication import PaperDeduplicator, deduplicate_papers


class TestDeduplication:
    """Test deduplication functionality"""

    def test_exact_doi_match(self):
        """Test deduplication by exact DOI"""
        papers = [
            {"title": "Paper A", "doi": "10.1234/abc"},
            {"title": "Paper A", "doi": "10.1234/abc"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 1

    def test_arxiv_match(self):
        """Test deduplication by arXiv ID"""
        papers = [
            {"title": "Paper B", "arxivId": "2301.12345"},
            {"title": "Paper B", "arxivId": "2301.12345"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 1

    def test_title_fuzzy_match(self):
        """Test deduplication by title similarity"""
        papers = [
            {"title": "Attention Is All You Need"},
            {"title": "Attention is all you need"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 1

    def test_no_duplicates(self):
        """Test with no duplicates"""
        papers = [
            {"title": "Paper 1", "doi": "10.1/1"},
            {"title": "Paper 2", "doi": "10.1/2"},
            {"title": "Paper 3", "doi": "10.1/3"},
        ]
        result = deduplicate_papers(papers)
        assert len(result) == 3

    def test_merge_metadata(self):
        """Test that metadata is merged from duplicates"""
        papers = [
            {"title": "Test", "doi": "10.1/1", "citationCount": 100},
            {"title": "Test", "doi": "10.1/1", "citationCount": 150},
        ]
        result = deduplicate_papers(papers)
        assert result[0]["citationCount"] == 150  # Should keep max


class TestCache:
    """Test disk cache"""

    def test_cache_basic(self, tmp_path):
        """Test basic cache operations"""
        from cite_agent.cache import DiskCache

        cache = DiskCache(cache_dir=str(tmp_path))
        cache.set("test", {"data": "value"}, query="q1")
        result = cache.get("test", query="q1")
        assert result == {"data": "value"}

    def test_cache_expiration(self, tmp_path):
        """Test cache expiration"""
        from cite_agent.cache import DiskCache
        from datetime import datetime, timedelta

        cache = DiskCache(cache_dir=str(tmp_path))

        # Manually set expired entry
        import sqlite3
        conn = sqlite3.connect(str(tmp_path / "cache.db"))
        expired_time = (datetime.now() - timedelta(hours=1)).isoformat()
        conn.execute("""
            INSERT INTO cache (key, value, query_type, created_at, expires_at, size_bytes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("test_key", '{"data": "value"}', "test", datetime.now().isoformat(), expired_time, 100))
        conn.commit()
        conn.close()

        result = cache.get("test", query="q1")
        assert result is None  # Should return None for different query


class TestOfflineMode:
    """Test offline mode"""

    def test_offline_search_local(self, tmp_path):
        """Test local library search"""
        from cite_agent.offline_mode import OfflineMode
        import json

        offline = OfflineMode(data_dir=str(tmp_path))

        # Create a test paper
        paper_file = offline.library_dir / "test_paper.json"
        paper_data = {
            "paper": {
                "title": "Machine Learning Test",
                "authors": [{"name": "John Doe"}],
                "abstract": "This is a test about ML"
            }
        }
        with open(paper_file, 'w') as f:
            json.dump(paper_data, f)

        # Search should find it
        results = offline.search_local_library("machine learning", "default")
        assert len(results) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
