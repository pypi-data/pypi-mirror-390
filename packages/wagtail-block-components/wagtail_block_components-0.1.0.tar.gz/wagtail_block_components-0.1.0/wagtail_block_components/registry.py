from wagtail import hooks


class ComponentRegistry:
    def __init__(self):
        self._cache = {}
        self._cache_built = False

    def _build_cache(self):
        self._cache = {}

        for fn in hooks.get_hooks("register_components"):
            result = fn()
            if not result:
                continue

            for block_class in result:
                self._cache[block_class.__name__] = block_class

        self._cache_built = True

    def get(self, name):
        if not self._cache_built:
            self._build_cache()
        return self._cache.get(name)

    def clear_cache(self):
        self._cache_built = False
        self._cache = {}


registry = ComponentRegistry()
