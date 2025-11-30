from functools import wraps
from time import time
import hashlib
import json
from typing import Optional, Any
import logging
logger = logging.getLogger(__name__)
class SimpleCache:
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time() - timestamp < self.ttl:
                logger.debug(f"Cache HIT: {key}")
                return value
            else:
                # Expiró
                del self.cache[key]
                logger.debug(f"Cache EXPIRED: {key}")
        logger.debug(f"Cache MISS: {key}")
        return None
    def set(self, key: str, value: Any):
        self.cache[key] = (value, time())
        logger.debug(f"Cache SET: {key}")
    def clear(self):
        self.cache.clear()
        logger.info("Cache cleared")
    def size(self) -> int:
        return len(self.cache)
def generate_cache_key(texto: str) -> str:
    return hashlib.md5(texto.encode()).hexdigest()
def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        result = await func(*args, **kwargs)
        elapsed = (time() - start) * 1000
        logger.info(f"{func.__name__} took {elapsed:.2f}ms")
        return result
    return wrapper