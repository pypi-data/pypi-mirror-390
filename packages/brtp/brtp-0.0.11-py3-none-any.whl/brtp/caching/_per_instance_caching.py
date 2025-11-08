import functools
from typing import Callable


# =================================================================================================
#  per_instance_lru_cache
# =================================================================================================
def per_instance_lru_cache(
    method: Callable | None = None,
    *,
    maxsize: int | None = 128,
    typed: bool = False,
):
    """
    Caching decorator to be applied to instance methods, instantiating a lru_cache on a per-instance basis.

    This solves the following problems of the regular @lru_cache decorator:
      - when applied to instance methods, the cache is shared across all instances of the class, making it impossible
        e.g. to clear the cache for a give instance
      - the cache holds strong references to the instance, preventing it from being garbage collected

    This decorator is intended to behave the same as the regular @lru_cache decorator, but...
      - keeps a separate cache per instance (instantiated on first method call per instance)
      - makes sure all additional functionality (cache_clear, ...) also works on a per-instance basis

    Example:

        class MyClass:

            @per_instance_lru_cache
            def compute_something(self, x: int) -> int:
                # expensive computation here
                pass

            @per_instance_lru_cache(maxsize=256, typed=True)
            def compute_something_else(self, y: int) -> int:
                # expensive computation here
                pass


    """

    def decorator(wrapped: Callable) -> Callable:
        def wrapper(self: object) -> Callable:
            # Create a cached version bound to this specific instance
            return functools.lru_cache(maxsize=maxsize, typed=typed)(
                functools.update_wrapper(
                    functools.partial(wrapped, self),
                    wrapped,
                )
            )

        # the below usage of cached_property implements the actual per-instance behavior,
        # making sure that the wrapper function is only called on first invocation per instance and then remembered,
        # creating a new cache per instance
        return functools.cached_property(wrapper)  # type: ignore

    return decorator if method is None else decorator(method)


# =================================================================================================
#  per_instance_cache
# =================================================================================================
per_instance_cache = per_instance_lru_cache(maxsize=None)
