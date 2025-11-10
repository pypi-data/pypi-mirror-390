#!/usr/bin/env python3
"""
Offline Mode - Graceful Degradation When Backend Unavailable

Allows cite-agent to continue functioning with reduced features when:
- Backend is unreachable
- Network is down
- User wants to work offline

Features available offline:
- Browse local library
- Search local papers
- Export citations
- View history
- Read saved PDFs
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class OfflineMode:
    """
    Manages offline functionality

    Provides graceful degradation when backend is unavailable
    """

    def __init__(self, data_dir: str = "~/.cite_agent"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(exist_ok=True)

        # Local data directories
        self.cache_dir = self.data_dir / "cache"
        self.library_dir = self.data_dir / "papers"
        self.history_dir = self.data_dir / "sessions"

        # Create directories
        self.cache_dir.mkdir(exist_ok=True)
        self.library_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)

        self.is_offline = False

    def enable_offline_mode(self):
        """Enable offline mode"""
        self.is_offline = True
        logger.info("📴 Offline mode enabled")

    def disable_offline_mode(self):
        """Disable offline mode"""
        self.is_offline = False
        logger.info("📡 Online mode enabled")

    def search_local_library(self, query: str, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        Search papers in local library

        Args:
            query: Search query (title, author, keywords)
            user_id: User identifier

        Returns:
            List of matching papers
        """
        results = []
        query_lower = query.lower()

        # Search through all saved papers
        pattern = f"{user_id}_*.json" if user_id != "default" else "*.json"

        for paper_file in self.library_dir.glob(pattern):
            try:
                with open(paper_file, 'r') as f:
                    paper_data = json.load(f)

                paper = paper_data.get("paper", {})

                # Simple text matching
                title = paper.get("title", "").lower()
                authors = " ".join([a.get("name", "") for a in paper.get("authors", [])]).lower()
                abstract = paper.get("abstract", "").lower()

                if (query_lower in title or
                    query_lower in authors or
                    query_lower in abstract):
                    results.append(paper)

            except Exception as e:
                logger.warning(f"Error reading paper file {paper_file}: {e}")

        logger.info(f"🔍 Found {len(results)} papers in local library")
        return results

    def get_cached_search(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Get cached search results

        Args:
            query: Search query

        Returns:
            Cached results if available, None otherwise
        """
        # Create cache key from query
        import hashlib
        cache_key = hashlib.sha256(query.encode()).hexdigest()[:16]
        cache_file = self.cache_dir / f"search_{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)

                # Check if cache is stale (older than 24 hours)
                cached_time = datetime.fromisoformat(cached.get("timestamp", "2000-01-01"))
                age_hours = (datetime.now() - cached_time).total_seconds() / 3600

                if age_hours < 24:
                    logger.info(f"💾 Using cached results (age: {age_hours:.1f}h)")
                    return cached.get("results")
                else:
                    logger.info(f"⏰ Cache expired (age: {age_hours:.1f}h)")

            except Exception as e:
                logger.warning(f"Error reading cache: {e}")

        return None

    def cache_search_results(self, query: str, results: Dict[str, Any]):
        """
        Cache search results for offline use

        Args:
            query: Search query
            results: API results to cache
        """
        import hashlib
        cache_key = hashlib.sha256(query.encode()).hexdigest()[:16]
        cache_file = self.cache_dir / f"search_{cache_key}.json"

        try:
            cache_data = {
                "query": query,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"💾 Cached results for: {query}")

        except Exception as e:
            logger.warning(f"Failed to cache results: {e}")

    def get_library_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """
        Get statistics about local library

        Args:
            user_id: User identifier

        Returns:
            Library statistics
        """
        pattern = f"{user_id}_*.json" if user_id != "default" else "*.json"
        paper_files = list(self.library_dir.glob(pattern))

        total_papers = len(paper_files)
        total_size = sum(f.stat().st_size for f in paper_files)

        # Count by year
        by_year = {}
        for paper_file in paper_files:
            try:
                with open(paper_file, 'r') as f:
                    paper_data = json.load(f)
                year = paper_data.get("paper", {}).get("year", "unknown")
                by_year[year] = by_year.get(year, 0) + 1
            except:
                pass

        return {
            "total_papers": total_papers,
            "total_size_mb": total_size / (1024 * 1024),
            "papers_by_year": by_year,
            "library_path": str(self.library_dir)
        }

    def get_recent_queries(self, user_id: str = "default", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent queries from history

        Args:
            user_id: User identifier
            limit: Maximum number of queries to return

        Returns:
            List of recent queries
        """
        pattern = f"{user_id}_*.json" if user_id != "default" else "*.json"
        session_files = list(self.history_dir.glob(pattern))

        # Sort by modification time
        session_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        recent = []
        for session_file in session_files[:limit]:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    recent.append({
                        "query": session_data.get("query"),
                        "timestamp": session_data.get("timestamp"),
                        "session_id": session_data.get("session_id")
                    })
            except Exception as e:
                logger.warning(f"Error reading session file: {e}")

        return recent

    def can_work_offline(self) -> bool:
        """
        Check if offline work is possible

        Returns:
            True if local library has data
        """
        has_papers = len(list(self.library_dir.glob("*.json"))) > 0
        has_cache = len(list(self.cache_dir.glob("*.json"))) > 0

        return has_papers or has_cache

    def get_offline_capabilities(self) -> Dict[str, bool]:
        """
        Get what features are available offline

        Returns:
            Dictionary of feature availability
        """
        stats = self.get_library_stats()

        return {
            "search_library": stats["total_papers"] > 0,
            "export_citations": stats["total_papers"] > 0,
            "view_history": len(list(self.history_dir.glob("*.json"))) > 0,
            "cached_searches": len(list(self.cache_dir.glob("search_*.json"))) > 0,
            "api_searches": False,  # Never available offline
            "pdf_reading": False,    # Requires network for download
            "financial_data": False  # Requires network
        }

    def show_offline_message(self):
        """Display helpful offline mode message"""
        from rich.console import Console
        from rich.panel import Panel
        from rich.markdown import Markdown

        console = Console()

        capabilities = self.get_offline_capabilities()
        stats = self.get_library_stats()

        message = f"""
# 📴 Offline Mode

You're currently offline, but you can still:

{'✅ **Search your library** (' + str(stats['total_papers']) + ' papers)' if capabilities['search_library'] else '❌ Search your library (no papers saved)'}
{'✅ **Export citations** to BibTeX' if capabilities['export_citations'] else '❌ Export citations (no papers saved)'}
{'✅ **View search history**' if capabilities['view_history'] else '❌ View search history (no history)'}
{'✅ **Use cached searches**' if capabilities['cached_searches'] else '❌ Use cached searches (no cache)'}

## Not Available Offline:
- ❌ New paper searches (requires network)
- ❌ PDF downloads (requires network)
- ❌ Financial data (requires network)

## To Get Back Online:
1. Check your internet connection
2. Restart cite-agent
3. Run `cite-agent --doctor` to diagnose

## Offline Commands:
```bash
cite-agent --library          # Browse saved papers
cite-agent --export-bibtex    # Export citations
cite-agent --history          # View past queries
```
"""

        console.print(Panel(
            Markdown(message),
            title="[bold yellow]Offline Mode Active[/]",
            border_style="yellow"
        ))


# Global offline mode instance
_offline_mode = None


def get_offline_mode() -> OfflineMode:
    """Get global offline mode instance"""
    global _offline_mode
    if _offline_mode is None:
        _offline_mode = OfflineMode()
    return _offline_mode


async def check_backend_available(backend_url: str, timeout: float = 5.0) -> bool:
    """
    Check if backend is available

    Args:
        backend_url: Backend URL to check
        timeout: Timeout in seconds

    Returns:
        True if backend is reachable
    """
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{backend_url}/api/health",
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                return response.status == 200
    except:
        try:
            # Fallback: try root endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    backend_url,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    return response.status < 500
        except:
            return False
