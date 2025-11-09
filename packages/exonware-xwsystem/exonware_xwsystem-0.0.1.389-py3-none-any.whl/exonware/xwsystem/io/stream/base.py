#!/usr/bin/env python3
#exonware/xwsystem/src/exonware/xwsystem/io/stream/base.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.389
Generation Date: 30-Oct-2025

Base classes for stream operations.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from ..contracts import ICodecIO, IPagedCodecIO

T = TypeVar('T')
R = TypeVar('R')

__all__ = ['ACodecIO', 'APagedCodecIO']


class ACodecIO(ICodecIO[T, R], ABC, Generic[T, R]):
    """Abstract base for codec I/O operations."""
    
    def __init__(self, codec, source):
        """Initialize codec I/O."""
        self._codec = codec
        self._source = source
    
    @property
    def codec(self):
        """The codec."""
        return self._codec
    
    @property
    def source(self):
        """The source."""
        return self._source


class APagedCodecIO(ACodecIO[T, R], IPagedCodecIO[T, R], ABC, Generic[T, R]):
    """Abstract base for paged codec I/O."""
    pass

