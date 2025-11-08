import json
import time
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)


class LicenseCache:
    """Thread-safe license cache with TTL and grace period"""

    _instance = None
    _lock = threading.Lock()

    # Configuration
    CACHE_TTL = 24 * 3600  # 24 hours
    GRACE_PERIOD = 48 * 3600  # 48 hours

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LicenseCache, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance

    def _initialize(self) -> None:
        """Initialize cache and load from disk"""
        # Use vnstock ggcolab for proper directory detection
        try:
            from vnstock.core.config.ggcolab import get_vnstock_directory
            cache_dir = get_vnstock_directory() / "id"
        except ImportError:
            cache_dir = Path.home() / ".vnstock" / "id"
        
        self.cache_dir = cache_dir
        self.cache_file = self.cache_dir / "license_cache.json"
        self.cache = None
        self.lock = threading.Lock()

        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load cache from disk
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                    msg = f"Loaded license cache from {self.cache_file}"
                    logger.debug(msg)
        except Exception as e:
            logger.warning(f"Failed to load license cache: {e}")
            self.cache = None

    def _save_cache(self) -> None:
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
                logger.debug(f"Saved license cache to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save license cache: {e}")

    def get(self, user_id: str | None = None) -> dict | None:
        """
        Get cached license status

        Args:
            user_id: User identifier (machine_id or similar)

        Returns:
            Cache entry if valid (not expired), None otherwise
        """
        with self.lock:
            if not self.cache:
                return None

            current_time = time.time()

            # Check if cache is valid
            cache_time = self.cache.get("checked_at")
            if not cache_time:
                return None

            # Parse cached time
            try:
                cache_time_ts = datetime.fromisoformat(
                    cache_time
                ).timestamp()
            except (ValueError, TypeError):
                cache_time_ts = 0

            age = current_time - cache_time_ts

            # Check if expired (TTL)
            if age > self.CACHE_TTL:
                logger.info(
                    f"License cache expired (age: {age:.0f}s, TTL: "
                    f"{self.CACHE_TTL}s)"
                )
                return None

            # Still valid, return cache
            return self.cache

    def set(self, is_paid: bool, checked_at: str | None = None) -> bool:
        """
        Set license cache

        Args:
            is_paid: Whether user is paid/licensed
            checked_at: When license was checked (ISO format)

        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            try:
                if checked_at is None:
                    checked_at = datetime.now().isoformat()

                cache_time = datetime.fromisoformat(
                    checked_at
                ).timestamp()
                cache_ttl_until = cache_time + self.CACHE_TTL
                grace_until = cache_time + self.GRACE_PERIOD

                self.cache = {
                    "is_paid": is_paid,
                    "checked_at": checked_at,
                    "cache_ttl_until": cache_ttl_until,
                    "grace_period_until": grace_until,
                    "cache_age_seconds": 0
                }

                self._save_cache()
                logger.info(
                    f"License cache updated: is_paid={is_paid}, "
                    f"TTL_expires={datetime.fromtimestamp(cache_ttl_until)}"
                )
                return True
            except Exception as e:
                logger.error(f"Failed to set license cache: {e}")
                return False

    def is_valid(self) -> bool:
        """Check if cache is currently valid (not expired)"""
        with self.lock:
            if not self.cache:
                return False

            current_time = time.time()
            cache_time = self.cache.get("checked_at")

            if not cache_time:
                return False

            try:
                cache_time_ts = datetime.fromisoformat(
                    cache_time
                ).timestamp()
            except (ValueError, TypeError):
                return False

            age = current_time - cache_time_ts

            # Valid if still within TTL
            return age <= self.CACHE_TTL

    def is_in_grace_period(self) -> bool:
        """
        Check if cache is in grace period
        (expired TTL but still within grace period for network failures)
        """
        with self.lock:
            if not self.cache:
                return False

            current_time = time.time()
            cache_time = self.cache.get("checked_at")

            if not cache_time:
                return False

            try:
                cache_time_ts = datetime.fromisoformat(
                    cache_time
                ).timestamp()
            except (ValueError, TypeError):
                return False

            age = current_time - cache_time_ts

            # In grace if expired TTL but within grace period
            return (age > self.CACHE_TTL and
                    age <= self.CACHE_TTL + self.GRACE_PERIOD)

    def get_is_paid(self) -> bool | None:
        """
        Get cached is_paid status

        Returns:
            - True if paid user (from valid cache)
            - False if free user or cache expired
            - None if unknown (no cache or error)
        """
        cache = self.get()
        if cache:
            return cache.get("is_paid", False)

        # Check if in grace period
        if self.is_in_grace_period():
            # Still within grace period, use cached value
            if self.cache:
                logger.info(
                    "Using cached license status (grace period active)"
                )
                return self.cache.get("is_paid", False)

        return None

    def clear(self) -> bool:
        """Clear cache (for testing or manual reset)"""
        with self.lock:
            try:
                self.cache = None
                if self.cache_file.exists():
                    self.cache_file.unlink()
                logger.info("License cache cleared")
                return True
            except Exception as e:
                logger.error(f"Failed to clear license cache: {e}")
                return False

    def get_cache_info(self) -> dict:
        """Get detailed cache information"""
        with self.lock:
            if not self.cache:
                return {"status": "empty"}

            current_time = time.time()
            cache_time_str = self.cache.get("checked_at")

            if not isinstance(cache_time_str, str):
                return {"status": "invalid"}

            try:
                cache_time = datetime.fromisoformat(cache_time_str)
                cache_time_ts = cache_time.timestamp()
            except (ValueError, TypeError):
                return {"status": "invalid"}

            age = current_time - cache_time_ts
            is_valid = age <= self.CACHE_TTL
            in_grace = (age > self.CACHE_TTL and
                        age <= self.CACHE_TTL + self.GRACE_PERIOD)

            return {
                "status": "valid" if is_valid else (
                    "grace_period" if in_grace else "expired"
                ),
                "is_paid": self.cache.get("is_paid"),
                "checked_at": cache_time_str,
                "age_seconds": int(age),
                "ttl_seconds": self.CACHE_TTL,
                "ttl_remaining_seconds": max(
                    0, self.CACHE_TTL - int(age)
                ),
                "grace_period_seconds": self.GRACE_PERIOD,
                "grace_remaining_seconds": max(
                    0, self.CACHE_TTL + self.GRACE_PERIOD - int(age)
                )
            }


# Create singleton instance
license_cache = LicenseCache()
