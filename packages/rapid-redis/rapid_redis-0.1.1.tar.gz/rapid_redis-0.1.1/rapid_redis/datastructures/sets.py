# Set Support

def sadd(cache, key, *values):
    """Add members to the set stored at key."""
    if key not in cache.data_store:
        cache.data_store[key] = set()
    for value in values:
        cache.data_store[key].add(value)
    return len(cache.data_store[key])

def smembers(cache, key):
    """Get all members"""
    return cache.data_store.get(key, set())
