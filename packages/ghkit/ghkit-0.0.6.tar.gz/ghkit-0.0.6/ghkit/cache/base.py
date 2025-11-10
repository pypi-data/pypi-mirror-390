from functools import wraps


class Cache:
    """Cache backend interface."""

    def get(self, key):
        """Get value by key."""
        raise NotImplementedError()

    def set(self, key, value, ttl=None):
        """Set key-value pair to cache."""
        raise NotImplementedError()

    def delete(self, key):
        """Delete key."""
        raise NotImplementedError()

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __call__(self, ttl=None, key_name=None):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if key_name:
                    key = key_name(*args, **kwargs) if callable(key_name) else key_name
                else:
                    key = func.__name__
                value = self.get(key)
                if value is None:
                    value = func(*args, **kwargs)
                    self.set(key, value, ttl=ttl)
                return value

            return wrapper

        return decorator
