# Rapid Redis

**Rapid Redis** is a lightweight, educational in-memory cache library inspired by Redis.
It is built entirely in Python for learning purposes and designed to be simple, minimal, and easy to extend.

---

## Overview

Rapid Redis provides a basic Redis-like interface for storing and managing cached data using Python dictionaries under the hood.
It currently supports five common data structures and exposes simple, intuitive methods for cache operations.

---

## Features

* In-memory key-value cache using Python dictionaries
* Basic operations: `set`, `get`, `delete`, `exists`, and `flush`
* Supports multiple data structures:

  * Strings
  * Lists
  * Sets
  * Hashes
  * Sorted Sets
* Easy to use and lightweight — ideal for understanding Redis fundamentals

---

## Installation

You can install Rapid Redis locally using:

```bash
pip install -e .
```

(Ensure you run this from the project root directory where `setup.py` is located.)

---

## Usage

```python
from rapid_redis import RapidCache
from rapid_redis.datastructures import strings, lists, sets, hashes, sortedsets

cache = RapidCache()

# String operations
cache.set("name", "Atharsh")
print(cache.get("name"))  # Output: Atharsh

# List operations
lists.lpush(cache, "mylist", 1, 2, 3)
print(cache.get("mylist"))  # Output: [3, 2, 1]

# Set operations
sets.sadd(cache, "myset", "a", "b", "c")
print(sets.smembers(cache, "myset"))  # Output: {'a', 'b', 'c'}

# Hash operations
hashes.hset(cache, "user:1", "name", "Atharsh")
print(hashes.hget(cache, "user:1", "name"))  # Output: Atharsh

# Sorted set operations
sortedsets.zadd(cache, "scores", 10, "Alice")
sortedsets.zadd(cache, "scores", 5, "Bob")
print(sortedsets.zrange(cache, "scores", 0, -1))  # Output: ['Bob', 'Alice']
```

---

## Roadmap

Planned features for upcoming releases include:

* TTL (Time-to-Live) support for expiring keys
* Persistent cache storage (saving data to disk)
* Thread-safe operations
* Command-line interface for quick cache access
* Optional lightweight server mode for experimentation
* Concurrency for multiple user handling

---

## Contributing

Rapid Redis is an open project — contributions are welcome.
If you’d like to improve functionality, add features, or clean up code, feel free to fork the repository and open a pull request.

---

## License

This project is released under the MIT License.


