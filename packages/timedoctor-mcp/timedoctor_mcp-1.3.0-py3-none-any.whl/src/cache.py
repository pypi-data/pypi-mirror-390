"""
Simple file-based caching system for Time Doctor reports.
Caches daily reports with TTL (time-to-live) to improve performance.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

# Handle both package import and direct execution
try:
    from .constants import CACHE_DIR_NAME, CACHE_TTL_SECONDS
except ImportError:
    from constants import CACHE_DIR_NAME, CACHE_TTL_SECONDS

logger = logging.getLogger(__name__)


class ReportCache:
    """
    File-based cache for Time Doctor daily reports.
    Stores HTML content with timestamp for TTL validation.
    """

    def __init__(self, cache_dir: Path | None = None):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory for cache files. Defaults to project_dir/.cache
        """
        if cache_dir is None:
            # Use project directory's .cache folder
            script_dir = Path(__file__).parent
            project_dir = script_dir.parent
            cache_dir = project_dir / CACHE_DIR_NAME

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl_seconds = CACHE_TTL_SECONDS

        logger.debug(f"ReportCache initialized at {self.cache_dir} with TTL={self.ttl_seconds}s")

    def _get_cache_key(self, date: str) -> str:
        """
        Get cache filename for a date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            str: Cache filename
        """
        return f"report_{date}.json"

    def _get_cache_path(self, date: str) -> Path:
        """
        Get full path to cache file.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            Path: Full path to cache file
        """
        return self.cache_dir / self._get_cache_key(date)

    def get(self, date: str) -> str | None:
        """
        Get cached report HTML for a date.

        Args:
            date: Date in YYYY-MM-DD format

        Returns:
            str | None: HTML content if cached and not expired, None otherwise
        """
        try:
            cache_path = self._get_cache_path(date)

            if not cache_path.exists():
                logger.debug(f"Cache miss for {date} - file not found")
                return None

            # Read cache file
            with open(cache_path, encoding="utf-8") as f:
                cache_data = json.load(f)

            # Check if cache is expired
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            age = datetime.now() - cached_at

            if age.total_seconds() > self.ttl_seconds:
                logger.debug(f"Cache expired for {date} (age: {age.total_seconds():.1f}s)")
                # Delete expired cache file
                cache_path.unlink()
                return None

            logger.info(f"Cache hit for {date} (age: {age.total_seconds():.1f}s)")
            return cache_data["html"]

        except Exception as e:
            logger.warning(f"Error reading cache for {date}: {e}")
            return None

    def set(self, date: str, html: str) -> None:
        """
        Cache report HTML for a date.

        Args:
            date: Date in YYYY-MM-DD format
            html: HTML content to cache
        """
        try:
            cache_path = self._get_cache_path(date)

            cache_data = {
                "date": date,
                "cached_at": datetime.now().isoformat(),
                "html": html,
            }

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False)

            logger.debug(f"Cached report for {date} at {cache_path}")

        except Exception as e:
            logger.warning(f"Error writing cache for {date}: {e}")

    def clear(self) -> int:
        """
        Clear all cached reports.

        Returns:
            int: Number of cache files deleted
        """
        try:
            count = 0
            for cache_file in self.cache_dir.glob("report_*.json"):
                cache_file.unlink()
                count += 1

            logger.info(f"Cleared {count} cache files")
            return count

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0

    def clear_expired(self) -> int:
        """
        Clear only expired cache entries.

        Returns:
            int: Number of expired cache files deleted
        """
        try:
            count = 0
            now = datetime.now()

            for cache_file in self.cache_dir.glob("report_*.json"):
                try:
                    with open(cache_file, encoding="utf-8") as f:
                        cache_data = json.load(f)

                    cached_at = datetime.fromisoformat(cache_data["cached_at"])
                    age = now - cached_at

                    if age.total_seconds() > self.ttl_seconds:
                        cache_file.unlink()
                        count += 1

                except Exception as e:
                    logger.warning(f"Error checking cache file {cache_file}: {e}")
                    continue

            logger.info(f"Cleared {count} expired cache files")
            return count

        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
            return 0

    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            dict: Statistics including total files, expired files, cache size
        """
        try:
            total_files = 0
            expired_files = 0
            total_size = 0
            now = datetime.now()

            for cache_file in self.cache_dir.glob("report_*.json"):
                try:
                    total_files += 1
                    total_size += cache_file.stat().st_size

                    with open(cache_file, encoding="utf-8") as f:
                        cache_data = json.load(f)

                    cached_at = datetime.fromisoformat(cache_data["cached_at"])
                    age = now - cached_at

                    if age.total_seconds() > self.ttl_seconds:
                        expired_files += 1

                except Exception:
                    continue

            return {
                "total_files": total_files,
                "valid_files": total_files - expired_files,
                "expired_files": expired_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "ttl_seconds": self.ttl_seconds,
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
