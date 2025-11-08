# Main Rapid cache module 

class RapidCache:
    def __init__(self):
        self.data_store = {}

    def set(self, key, value):
        """Set a value in the cache."""
        self.data_store[key] = value
        return True

    def get(self, key):
        """Get a value from the cache."""
        return self.data_store.get(key, None)
    
    def delete(self, key):
        """Delete a value from the cache."""
        if key in self.data_store:
            del self.data_store[key]
            return True
        return False
    
    def clear(self):
        """Clear the entire cache."""
        self.data_store.clear()
        return True
    

    