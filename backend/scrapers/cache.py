"""
Redis Dual-Tier Cache & Request Deduplication
=============================================
Manages:
1. Static Product Metadata Cache (Title, Brand, Image, Product ID, Canonical URL) - 24 hours TTL
2. Dynamic Pricing Cache (Current Price, MRP, Discount, Availability) - 15 minutes TTL
3. Per-Variant Granular Pricing Support
4. In-flight Request Deduplication via Async Lock
"""
import json
import logging
import asyncio
from typing import Optional, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)

# In-memory fallback if Redis is unavailable
_MEMORY_CACHE: Dict[str, Any] = {}
_IN_FLIGHT_LOCKS: Dict[str, asyncio.Lock] = {}
_GLOBAL_LOCK = asyncio.Lock()


_REDIS_CLIENT = None


class ScraperCache:
    STATIC_TTL_SECONDS = 86400  # 24 hours
    DYNAMIC_TTL_SECONDS = 300   # 5 minutes (fresh live pricing)

    @classmethod
    def _get_redis_client(cls):
        global _REDIS_CLIENT
        if _REDIS_CLIENT is False:
            return None
        if _REDIS_CLIENT is not None:
            return _REDIS_CLIENT
        try:
            import os
            import redis
            # Check if running outside Docker with a docker hostname 'redis'
            redis_url = settings.REDIS_URL
            is_docker = os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")
            if not is_docker and "@redis:" in redis_url or "://redis:" in redis_url:
                # Avoid 3-second Windows DNS hang trying to resolve 'redis'
                redis_url = redis_url.replace("://redis:", "://127.0.0.1:").replace("@redis:", "@127.0.0.1:")

            client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=0.15,
                socket_timeout=0.15,
            )
            client.ping()
            _REDIS_CLIENT = client
            return _REDIS_CLIENT
        except Exception as e:
            logger.info(f"Redis unavailable ({e}). Using ultra-fast in-memory cache fallback.")
            _REDIS_CLIENT = False
            return None

    @classmethod
    def _make_key(cls, tier: str, platform: str, product_id: str, variant_key: Optional[str] = None) -> str:
        base = f"pricewatch:{tier}:{platform}:{product_id}"
        if variant_key:
            safe_var = variant_key.replace(" ", "_").lower()
            return f"{base}:{safe_var}"
        return base

    @classmethod
    def get_static_cache(cls, platform: str, product_id: str, variant_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached static metadata (title, brand, image)."""
        key = cls._make_key("static", platform, product_id, variant_key)
        r = cls._get_redis_client()
        if r:
            try:
                val = r.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.debug(f"Redis get_static_cache error: {e}")
                global _REDIS_CLIENT
                _REDIS_CLIENT = False
        mem = _MEMORY_CACHE.get(key)
        if mem:
            return mem
        if variant_key:
            return cls.get_static_cache(platform, product_id, variant_key=None)
        return None

    @classmethod
    def set_static_cache(cls, platform: str, product_id: str, data: Dict[str, Any], variant_key: Optional[str] = None):
        """Save static product metadata to cache."""
        key = cls._make_key("static", platform, product_id, variant_key)
        r = cls._get_redis_client()
        if r:
            try:
                r.setex(key, cls.STATIC_TTL_SECONDS, json.dumps(data))
                if variant_key:
                    # Also populate base product cache
                    base_key = cls._make_key("static", platform, product_id, None)
                    r.setex(base_key, cls.STATIC_TTL_SECONDS, json.dumps(data))
                return
            except Exception as e:
                logger.debug(f"Redis set_static_cache error: {e}")
                global _REDIS_CLIENT
                _REDIS_CLIENT = False
        _MEMORY_CACHE[key] = data
        if variant_key:
            _MEMORY_CACHE[cls._make_key("static", platform, product_id, None)] = data

    @classmethod
    def get_dynamic_cache(cls, platform: str, product_id: str, variant_key: Optional[str] = None, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """Retrieve cached dynamic price and availability. If force_refresh=True, bypass cache."""
        if force_refresh:
            return None
        key = cls._make_key("dynamic", platform, product_id, variant_key)
        r = cls._get_redis_client()
        if r:
            try:
                val = r.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.debug(f"Redis get_dynamic_cache error: {e}")
                global _REDIS_CLIENT
                _REDIS_CLIENT = False
        mem = _MEMORY_CACHE.get(key)
        if mem:
            return mem
        if variant_key:
            return cls.get_dynamic_cache(platform, product_id, variant_key=None, force_refresh=force_refresh)
        return None

    @classmethod
    def set_dynamic_cache(cls, platform: str, product_id: str, data: Dict[str, Any], variant_key: Optional[str] = None):
        """Save dynamic price to cache."""
        key = cls._make_key("dynamic", platform, product_id, variant_key)
        r = cls._get_redis_client()
        if r:
            try:
                r.setex(key, cls.DYNAMIC_TTL_SECONDS, json.dumps(data))
                return
            except Exception as e:
                logger.debug(f"Redis set_dynamic_cache error: {e}")
                global _REDIS_CLIENT
                _REDIS_CLIENT = False
        _MEMORY_CACHE[key] = data

    @classmethod
    def clear_all(cls):
        """Clear memory cache and Redis keys for testing."""
        global _MEMORY_CACHE
        _MEMORY_CACHE.clear()
        r = cls._get_redis_client()
        if r:
            try:
                keys = r.keys("pricewatch:*")
                if keys:
                    r.delete(*keys)
            except Exception:
                pass

    @classmethod
    async def get_url_lock(cls, canonical_id: str) -> asyncio.Lock:
        """Get or create an async lock for request deduplication."""
        async with _GLOBAL_LOCK:
            if canonical_id not in _IN_FLIGHT_LOCKS:
                _IN_FLIGHT_LOCKS[canonical_id] = asyncio.Lock()
            return _IN_FLIGHT_LOCKS[canonical_id]
