#!/usr/bin/env python3
#exonware/xwsystem/src/exonware/xwsystem/io/serialization/formats/binary/__init__.py
"""Binary serialization formats (core lightweight formats)."""

# Core binary formats
from .msgpack import XWMsgPackSerializer, MsgPackSerializer
from .pickle import XWPickleSerializer, PickleSerializer
from .bson import XWBsonSerializer, BsonSerializer
from .marshal import XWMarshalSerializer, MarshalSerializer
from .cbor import XWCborSerializer, CborSerializer
from .plistlib import XWPlistSerializer, PlistlibSerializer

__all__ = [
    # I→A→XW pattern (XW prefix)
    "XWMsgPackSerializer",
    "XWPickleSerializer",
    "XWBsonSerializer",
    "XWMarshalSerializer",
    "XWCborSerializer",
    "XWPlistSerializer",
    
    # Backward compatibility aliases
    "MsgPackSerializer",
    "PickleSerializer",
    "BsonSerializer",
    "MarshalSerializer",
    "CborSerializer",
    "PlistlibSerializer",
]

# NOTE: Enterprise binary formats moved to xwformats:
# - UBJSON (py-ubjson library, ~100 KB)
# 
# Install with: pip install exonware-xwformats
