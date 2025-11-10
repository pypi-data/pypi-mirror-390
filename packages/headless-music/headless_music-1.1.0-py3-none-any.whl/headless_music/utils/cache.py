from functools import wraps
import logging


class SimpleCache:
    def __init__(self, max_size=100):
        self._cache = {}
        self._max_size = max_size

    def get(self, key):
        return self._cache.get(key)

    def set(self, key, value):
        if len(self._cache) >= self._max_size:
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        self._cache[key] = value

    def clear(self):
        self._cache.clear()

panel_cache = SimpleCache(max_size=50)
art_cache = SimpleCache(max_size=32)