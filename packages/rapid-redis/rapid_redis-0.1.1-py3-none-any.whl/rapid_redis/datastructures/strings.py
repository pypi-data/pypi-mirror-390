# String Support

def set_string(cache, key, value):
    """Set a string value in the cache."""
    cache.set(key, str(value))
    return True

def get_string(cache, key):
    """Get a string value from the cache."""
    value = cache.get(key)
    if not isinstance(value, str):
        return None
    return value