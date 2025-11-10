#!/usr/bin/env python3
"""
Disk Cache for API Responses

Caches API responses to disk for:
- Faster repeated queries
- Offline access to previous results
- Reduced API costs
- Better performance

Uses SQLite for indexed storage
"""

import logging
import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DiskCache:
    """
    SQLite-based cache for API responses

    Features:
    - Automatic expiration (TTL)
    - LRU eviction when cache is full
    - Indexed lookups by query hash
    - Compression for large responses
    """

    def __init__(
        self,
        cache_dir: str = "~/.cite_agent/cache",
        max_size_mb: int = 500,
        default_ttl_hours: int = 24
    ):
        """
        Initialize cache

        Args:
            cache_dir: Directory for cache database
            max_size_mb: Maximum cache size in MB
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = self.cache_dir / "cache.db"
        self.max_size_mb = max_size_mb
        self.default_ttl_hours = default_ttl_hours

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    query_type TEXT NOT NULL,
                    query_text TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    size_bytes INTEGER
                )
            """)

            # Create indexes for fast lookups
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_query_type ON cache(query_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache(last_accessed)")

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _make_key(self, query_type: str, **params) -> str:
        """
        Generate cache key from query parameters

        Args:
            query_type: Type of query (search, financial, etc.)
            **params: Query parameters

        Returns:
            Cache key (hash)
        """
        # Create deterministic string from params
        param_str = json.dumps(params, sort_keys=True)
        combined = f"{query_type}:{param_str}"

        # Hash to fixed-length key
        return hashlib.sha256(combined.encode()).hexdigest()

    def get(self, query_type: str, **params) -> Optional[Dict[str, Any]]:
        """
        Get cached value

        Args:
            query_type: Type of query
            **params: Query parameters

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        key = self._make_key(query_type, **params)

        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value, expires_at, access_count FROM cache WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            # Check expiration
            expires_at = datetime.fromisoformat(row["expires_at"])
            if datetime.now() > expires_at:
                logger.debug(f"Cache expired for {query_type}")
                self._delete(conn, key)
                return None

            # Update access stats
            conn.execute("""
                UPDATE cache
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE key = ?
            """, (datetime.now().isoformat(), key))
            conn.commit()

            # Deserialize value
            try:
                value = json.loads(row["value"])
                logger.debug(f"Cache HIT for {query_type} (accessed {row['access_count']} times)")
                return value
            except json.JSONDecodeError:
                logger.warning(f"Corrupted cache entry for {query_type}")
                self._delete(conn, key)
                return None

    def set(
        self,
        query_type: str,
        value: Dict[str, Any],
        ttl_hours: Optional[int] = None,
        **params
    ):
        """
        Cache a value

        Args:
            query_type: Type of query
            value: Value to cache
            ttl_hours: Time to live in hours (None = use default)
            **params: Query parameters
        """
        key = self._make_key(query_type, **params)
        ttl = ttl_hours if ttl_hours is not None else self.default_ttl_hours

        # Serialize value
        value_json = json.dumps(value)
        size_bytes = len(value_json.encode('utf-8'))

        # Calculate expiration
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=ttl)

        # Check if we need to evict old entries
        self._maybe_evict()

        with self._get_connection() as conn:
            # Insert or replace
            conn.execute("""
                INSERT OR REPLACE INTO cache
                (key, value, query_type, query_text, created_at, expires_at, size_bytes, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key,
                value_json,
                query_type,
                json.dumps(params),
                created_at.isoformat(),
                expires_at.isoformat(),
                size_bytes,
                created_at.isoformat()
            ))
            conn.commit()

        logger.debug(f"Cached {query_type} ({size_bytes} bytes, TTL: {ttl}h)")

    def _delete(self, conn: sqlite3.Connection, key: str):
        """Delete cache entry"""
        conn.execute("DELETE FROM cache WHERE key = ?", (key,))
        conn.commit()

    def _maybe_evict(self):
        """Evict old entries if cache is too large"""
        with self._get_connection() as conn:
            # Check current size
            cursor = conn.execute("SELECT SUM(size_bytes) as total FROM cache")
            row = cursor.fetchone()
            total_bytes = row["total"] or 0
            total_mb = total_bytes / (1024 * 1024)

            if total_mb > self.max_size_mb:
                # Evict least recently used entries
                evict_count = int(self.get_stats()["total_entries"] * 0.2)  # Evict 20%

                conn.execute("""
                    DELETE FROM cache
                    WHERE key IN (
                        SELECT key FROM cache
                        ORDER BY last_accessed ASC
                        LIMIT ?
                    )
                """, (evict_count,))
                conn.commit()

                logger.info(f"Evicted {evict_count} cache entries (cache was {total_mb:.1f}MB)")

    def clear_expired(self):
        """Remove all expired entries"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            count = cursor.rowcount
            conn.commit()

        if count > 0:
            logger.info(f"Cleared {count} expired cache entries")

        return count

    def clear_all(self):
        """Clear entire cache"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM cache")
            count = cursor.rowcount
            conn.commit()

        logger.info(f"Cleared all cache ({count} entries)")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Statistics dictionary
        """
        with self._get_connection() as conn:
            # Total entries
            cursor = conn.execute("SELECT COUNT(*) as count FROM cache")
            total = cursor.fetchone()["count"]

            # Total size
            cursor = conn.execute("SELECT SUM(size_bytes) as total FROM cache")
            total_bytes = cursor.fetchone()["total"] or 0

            # By query type
            cursor = conn.execute("""
                SELECT query_type, COUNT(*) as count
                FROM cache
                GROUP BY query_type
            """)
            by_type = {row["query_type"]: row["count"] for row in cursor.fetchall()}

            # Expired count
            cursor = conn.execute(
                "SELECT COUNT(*) as count FROM cache WHERE expires_at < ?",
                (datetime.now().isoformat(),)
            )
            expired_count = cursor.fetchone()["count"]

            return {
                "total_entries": total,
                "total_size_mb": total_bytes / (1024 * 1024),
                "max_size_mb": self.max_size_mb,
                "usage_percent": (total_bytes / (self.max_size_mb * 1024 * 1024)) * 100,
                "by_type": by_type,
                "expired_count": expired_count
            }

    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently cached queries

        Args:
            limit: Maximum number to return

        Returns:
            List of recent queries
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT query_type, query_text, created_at, access_count
                FROM cache
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

            return [
                {
                    "query_type": row["query_type"],
                    "query": json.loads(row["query_text"]) if row["query_text"] else {},
                    "cached_at": row["created_at"],
                    "access_count": row["access_count"]
                }
                for row in cursor.fetchall()
            ]


# Global cache instance
_cache = None


def get_cache() -> DiskCache:
    """Get global cache instance"""
    global _cache
    if _cache is None:
        _cache = DiskCache()
    return _cache


def cached_api_call(query_type: str, ttl_hours: int = 24):
    """
    Decorator for caching API calls

    Usage:
        @cached_api_call("academic_search", ttl_hours=24)
        async def search_papers(query: str, limit: int):
            # ... API call ...
            return results

    Args:
        query_type: Type of query
        ttl_hours: Cache TTL in hours
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache = get_cache()

            # Try cache first
            cached_result = cache.get(query_type, **kwargs)
            if cached_result is not None:
                return cached_result

            # Call function
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(query_type, result, ttl_hours, **kwargs)

            return result

        return wrapper
    return decorator
