# List Support 

def lpush(cache,key,*values):
    """Push values to the left of the list stored at key."""
    if key not in cache.data_store:
        cache.data_store[key] = []
    if not isinstance(cache.data_store[key], list):
        raise TypeError("Value at key is not a list")
    for value in values:
        cache.data_store[key].insert(0, value)
    return len(cache.data_store[key])

def rpush(cache,key,*values):
    """Push values to the right of the list stored at key."""
    if key not in cache.data_store:
        cache.data_store[key] = []
    if not isinstance(cache.data_store[key], list):
        raise TypeError("Value at key is not a list")
    for value in values:
        cache.data_store[key].append(value)
    return len(cache.data_store[key])

def lpop(cache,key):
    """Pop a value from the left of the list stored at key."""
    if key not in cache.data_store or not isinstance(cache.data_store[key], list):
        return None
    if len(cache.data_store[key]) == 0:
        return None
    return cache.data_store[key].pop(0)

