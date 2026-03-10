"""Intelligent caching system for AI responses and processing results."""

import hashlib
import json
import pickle
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.logger_service import get_logger


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class CacheBackend(ABC):
    """Abstract cache backend interface."""

    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        pass

    @abstractmethod
    def set(self, entry: CacheEntry) -> bool:
        """Set cache entry."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete cache entry by key."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache entries."""
        pass

    @abstractmethod
    def keys(self) -> List[str]:
        """Get all cache keys."""
        pass


class MemoryCacheBackend(CacheBackend):
    """In-memory cache backend with thread safety."""

    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self.max_size = max_size
        self.logger = get_logger(__name__)

    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            entry = self._cache.get(key)
            if entry:
                # Check expiration
                if entry.expires_at and datetime.utcnow() > entry.expires_at:
                    del self._cache[key]
                    return None

                # Update access stats
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow()
                return entry
            return None

    def set(self, entry: CacheEntry) -> bool:
        with self._lock:
            # Evict if at capacity
            if len(self._cache) >= self.max_size and entry.key not in self._cache:
                self._evict_lru()

            # Calculate size
            try:
                entry.size_bytes = len(pickle.dumps(entry.value))
            except Exception:
                entry.size_bytes = len(str(entry.value))

            self._cache[entry.key] = entry
            return True

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._cache.pop(key, None) is not None

    def clear(self) -> bool:
        with self._lock:
            self._cache.clear()
            return True

    def keys(self) -> List[str]:
        with self._lock:
            return list(self._cache.keys())

    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self._cache:
            return

        # Find LRU entry
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed or self._cache[k].created_at,
        )
        del self._cache[lru_key]
        self.logger.debug(f"Evicted LRU cache entry: {lru_key}")


class FileCacheBackend(CacheBackend):
    """File-based cache backend for persistence."""

    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)

    def get(self, key: str) -> Optional[CacheEntry]:
        cache_file = self.cache_dir / f"{self._hash_key(key)}.cache"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "rb") as f:
                entry = pickle.load(f)

            # Check expiration
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                cache_file.unlink()
                return None

            # Update access stats
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()

            # Save updated stats
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)

            return entry
        except Exception as e:
            self.logger.error(f"Error reading cache file {cache_file}: {e}")
            return None

    def set(self, entry: CacheEntry) -> bool:
        cache_file = self.cache_dir / f"{self._hash_key(entry.key)}.cache"

        try:
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)
            return True
        except Exception as e:
            self.logger.error(f"Error writing cache file {cache_file}: {e}")
            return False

    def delete(self, key: str) -> bool:
        cache_file = self.cache_dir / f"{self._hash_key(key)}.cache"

        try:
            if cache_file.exists():
                cache_file.unlink()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting cache file {cache_file}: {e}")
            return False

    def clear(self) -> bool:
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cache directory: {e}")
            return False

    def keys(self) -> List[str]:
        # Note: This is expensive for file backend
        keys = []
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)
                keys.append(entry.key)
            except Exception:
                continue
        return keys

    def _hash_key(self, key: str) -> str:
        """Generate filename-safe hash of key."""
        return hashlib.sha256(key.encode()).hexdigest()[:16]


class IntelligentCache:
    """Intelligent caching system with multiple backends and strategies."""

    def __init__(
        self,
        backend: Optional[CacheBackend] = None,
        default_ttl: int = 3600,  # 1 hour
        max_key_length: int = 250,
    ):
        self.backend = backend or MemoryCacheBackend()
        self.default_ttl = default_ttl
        self.max_key_length = max_key_length
        self.logger = get_logger(__name__)

        # Cache statistics
        self.stats = {"hits": 0, "misses": 0, "sets": 0, "deletes": 0, "evictions": 0}

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        cache_key = self._normalize_key(key)

        entry = self.backend.get(cache_key)
        if entry:
            self.stats["hits"] += 1
            self.logger.debug(f"Cache hit for key: {cache_key}")
            return entry.value

        self.stats["misses"] += 1
        self.logger.debug(f"Cache miss for key: {cache_key}")
        return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Set value in cache."""
        cache_key = self._normalize_key(key)
        ttl = ttl or self.default_ttl

        expires_at = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None

        entry = CacheEntry(
            key=cache_key,
            value=value,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            tags=tags or [],
        )

        success = self.backend.set(entry)
        if success:
            self.stats["sets"] += 1
            self.logger.debug(f"Cache set for key: {cache_key}")

        return success

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        cache_key = self._normalize_key(key)
        success = self.backend.delete(cache_key)

        if success:
            self.stats["deletes"] += 1
            self.logger.debug(f"Cache delete for key: {cache_key}")

        return success

    def clear(self) -> bool:
        """Clear all cache entries."""
        success = self.backend.clear()
        if success:
            self.stats = dict.fromkeys(self.stats, 0)
            self.logger.info("Cache cleared")
        return success

    def get_or_set(
        self,
        key: str,
        func: callable,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Any:
        """Get value from cache or set it using function."""
        value = self.get(key)
        if value is not None:
            return value

        # Compute value
        value = func()
        self.set(key, value, ttl, tags)
        return value

    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate all entries with any of the given tags."""
        invalidated = 0

        for cache_key in self.backend.keys():
            entry = self.backend.get(cache_key)
            if entry and any(tag in entry.tags for tag in tags):
                self.backend.delete(cache_key)
                invalidated += 1

        self.logger.info(f"Invalidated {invalidated} cache entries by tags: {tags}")
        return invalidated

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            **self.stats,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "cache_size": len(self.backend.keys()),
        }

    def _normalize_key(self, key: str) -> str:
        """Normalize cache key."""
        # Truncate if too long
        if len(key) > self.max_key_length:
            hash_suffix = hashlib.md5(key.encode()).hexdigest()[:8]
            key = key[: self.max_key_length - 9] + "_" + hash_suffix

        # Replace problematic characters
        return key.replace(" ", "_").replace("/", "_").replace("\\", "_")


class AIResponseCache:
    """Specialized cache for AI responses."""

    def __init__(self, cache: Optional[IntelligentCache] = None):
        self.cache = cache or IntelligentCache(
            backend=FileCacheBackend("cache/ai_responses"),
            default_ttl=86400,  # 24 hours
        )
        self.logger = get_logger(__name__)

    def get_ai_response(
        self, prompt: str, model: str, parameters: Dict[str, Any]
    ) -> Optional[str]:
        """Get cached AI response."""
        cache_key = self._generate_ai_key(prompt, model, parameters)
        return self.cache.get(cache_key)

    def cache_ai_response(
        self,
        prompt: str,
        model: str,
        parameters: Dict[str, Any],
        response: str,
        ttl: Optional[int] = None,
    ) -> bool:
        """Cache AI response."""
        cache_key = self._generate_ai_key(prompt, model, parameters)
        tags = ["ai_response", f"model_{model}"]

        return self.cache.set(cache_key, response, ttl, tags)

    def invalidate_model_responses(self, model: str) -> int:
        """Invalidate all responses for a specific model."""
        return self.cache.invalidate_by_tags([f"model_{model}"])

    def _generate_ai_key(
        self, prompt: str, model: str, parameters: Dict[str, Any]
    ) -> str:
        """Generate cache key for AI request."""
        # Create deterministic key from prompt, model, and parameters
        key_data = {
            "prompt": prompt,
            "model": model,
            "parameters": sorted(parameters.items()),
        }

        key_json = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()

        return f"ai_response_{model}_{key_hash}"


# Global cache instances
default_cache = IntelligentCache()
ai_response_cache = AIResponseCache()


def cached(ttl: int = 3600, tags: Optional[List[str]] = None):
    """Decorator for caching function results."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_data = {
                "function": func.__name__,
                "args": args,
                "kwargs": sorted(kwargs.items()),
            }
            key = json.dumps(key_data, sort_keys=True, default=str)

            return default_cache.get_or_set(
                key, lambda: func(*args, **kwargs), ttl, tags
            )

        return wrapper

    return decorator
