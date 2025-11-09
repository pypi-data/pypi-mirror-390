#!/usr/bin/env python3
#exonware/xwsystem/src/exonware/xwsystem/io/serialization/formats/database/__init__.py
"""Database-based serialization formats (core lightweight formats only)."""

# Core lightweight database formats (built-in, ~0 KB)
from .sqlite3 import XWSqlite3Serializer, Sqlite3Serializer
from .dbm import XWDbmSerializer, DbmSerializer
from .shelve import XWShelveSerializer, ShelveSerializer

__all__ = [
    # I→A→XW pattern (XW prefix)
    "XWSqlite3Serializer",
    "XWDbmSerializer",
    "XWShelveSerializer",
    
    # Backward compatibility aliases
    "Sqlite3Serializer",
    "DbmSerializer",
    "ShelveSerializer",
]

# NOTE: Enterprise database formats moved to xwformats:
# - LMDB (lmdb library, ~1.5 MB)
# - GraphDB (neo4j, pydgraph libraries, ~15 MB)
# - LevelDB (plyvel library, ~2 MB)
# 
# Install with: pip install exonware-xwformats
