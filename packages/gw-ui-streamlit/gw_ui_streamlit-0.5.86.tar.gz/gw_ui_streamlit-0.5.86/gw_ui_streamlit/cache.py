import time

class GWSCache:
    def __init__(self):
        """
        Initializes an instance of the class with an empty cache.

        Attributes:
            cache (dict): A dictionary to store cached data.
        """
        self.cache = {}

    def set(self, key, value, ttl=None):
        """
        Stores a value in the cache with an optional time-to-live (TTL).

        Args:
            key (str): The key under which the value will be stored.
            value (Any): The value to store in the cache.
            ttl (Optional[float]): The time-to-live in seconds for the cached value. 
                If None, the value will not expire.

        """
        expires_at = time.time() + ttl if ttl is not None else None
        self.cache[key] = (value, expires_at)

    def get(self, key):
        """
        Retrieve the value associated with the given key from the cache.

        This method first performs cleanup to remove expired items from the cache
        before attempting to retrieve the requested item. If the key does not exist
        in the cache or the item has expired, it returns None.

        Args:
            key (str): The key associated with the cached value.

        Returns:
            Any: The value associated with the key if it exists and has not expired,
            otherwise None.
        """
        self.cleanup()  # Clean expired items before retrieving
        item = self.cache.get(key)
        if item is None:
            return None
        value, _ = item
        return value

    def delete(self, key):
        """
        Deletes an entry from the cache based on the provided key.

        Args:
            key (str): The key of the cache entry to be deleted.

        Returns:
            None
        """
        if key in self.cache:
            del self.cache[key]

    def clear(self):
        """
        Clears the cache by removing all stored items.

        This method empties the cache, ensuring that no previously stored data remains.
        It is useful for resetting the cache or freeing up memory.

        Returns:
            None
        """
        self.cache.clear()

    def has_key(self, key):
        """
        Check if a given key exists in the cache.

        This method first performs cleanup to remove expired items from the cache
        before checking for the presence of the specified key.

        Args:
            key (str): The key to check for in the cache.

        Returns:
            bool: True if the key exists in the cache, False otherwise.
        """
        self.cleanup()  # Clean expired items before checking
        return key in self.cache

    def cleanup(self):
        """
        Removes expired items from the cache.

        This method iterates through the cache and deletes entries whose expiration
        time has passed. Expired entries are identified by comparing the current time
        with their `expires_at` value.

        Attributes:
            self.cache (dict): A dictionary where keys are cache identifiers and values
                               are tuples containing the cached data and its expiration time.

        Note:
            Entries with `expires_at` set to `None` are considered non-expiring and are
            not removed.
        """
        now = time.time()
        expired_keys = [key for key, (_, expires_at) in self.cache.items()
                        if expires_at is not None and now > expires_at]
        for key in expired_keys:
            del self.cache[key]
    
