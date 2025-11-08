# Hash Support

def hset(cache, key, field, value):
    """Set the value of a field in a hash stored at key."""
    if key not in cache.data_store:
        cache.data_store[key] = {}
    cache.data_store[key][field] = value
    return True

def hget(cache, key, field):
    """Get the value of a field in a hash stored at key."""
    if key not in cache.data_store or not isinstance(cache.data_store[key], dict):
        return None
    return cache.data_store[key].get(field, None)