#!/usr/bin/env python3
#exonware/xwsystem/src/exonware/xwsystem/io/archive/formats/__init__.py
"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.389
Generation Date: November 1, 2025

Archive format implementations - COMPREHENSIVE 2025 SUPPORT.

Pluggable archive formats registered with ArchiveFormatRegistry.

SUPPORTED FORMATS (Ranked by compression quality):

| Rank | Format         | Type       | Compression       | Use Case                        |
|------|----------------|------------|-------------------|---------------------------------|
| 1    | 7z             | Container  | LZMA2             | Best ratio + AES-256            |
| 2    | Zstandard      | Stream     | Zstd              | Fast modern (backups/DBs)       |
| 3    | RAR5           | Container  | Proprietary       | Strong + recovery               |
| 4    | ZIP/ZIPX       | Container  | Deflate/LZMA      | Widely supported                |
| 5    | tar.zst/tar.xz | Container  | Zstd/LZMA2        | Linux backups                   |
| 6    | Brotli         | Stream     | Brotli            | Web & text assets               |
| 7    | LZ4            | Stream     | LZ4               | Ultra fast real-time            |
| 8    | ZPAQ           | Journaled  | PAQ               | Extreme compression (archival)  |
| 9    | WIM            | Container  | LZX               | Windows system images           |
| 10   | SquashFS       | Filesystem | LZMA/LZ4          | Embedded systems                |

Priority 1 (Security): Safe format operations
Priority 2 (Usability): Auto-registration + lazy install
Priority 3 (Maintainability): Modular formats
Priority 4 (Performance): Efficient format handling
Priority 5 (Extensibility): Easy to add more formats
"""

# Standard formats (always available)
from .zip import ZipArchiver
from .tar import TarArchiver

# Advanced formats (lazy install on first use)
from .sevenzip import SevenZipArchiver  # RANK #1 - Best overall
from .zstandard import ZstandardArchiver  # RANK #2 - Modern standard
from .rar import RarArchiver  # RANK #3 - Extraction only
from .brotli_format import BrotliArchiver  # RANK #6 - Web compression
from .lz4_format import Lz4Archiver  # RANK #7 - Fastest
from .zpaq_format import ZpaqArchiver  # RANK #8 - Extreme compression
from .wim_format import WimArchiver  # RANK #9 - Windows imaging
from .squashfs_format import SquashfsArchiver  # RANK #10 - Embedded systems

# Auto-register built-in formats
from ..base import get_global_archive_registry

_registry = get_global_archive_registry()

# Register all formats
_registry.register(ZipArchiver)  # ZIP/ZIPX
_registry.register(TarArchiver)  # TAR variants
_registry.register(SevenZipArchiver)  # 7z - BEST OVERALL
_registry.register(ZstandardArchiver)  # Zstd - MODERN STANDARD
_registry.register(RarArchiver)  # RAR5
_registry.register(BrotliArchiver)  # Brotli
_registry.register(Lz4Archiver)  # LZ4
_registry.register(ZpaqArchiver)  # ZPAQ
_registry.register(WimArchiver)  # WIM
_registry.register(SquashfsArchiver)  # SquashFS


# Convenience functions (like codec!)
def get_archiver_for_file(path: str):
    """
    Get archiver by file extension (auto-detection!).
    
    Examples:
        >>> get_archiver_for_file("backup.7z")  # Returns SevenZipArchiver
        >>> get_archiver_for_file("data.tar.zst")  # Returns ZstandardArchiver
    """
    return get_global_archive_registry().get_by_extension(path)


def get_archiver_by_id(format_id: str):
    """
    Get archiver by format ID.
    
    Examples:
        >>> get_archiver_by_id("7z")  # Returns SevenZipArchiver
        >>> get_archiver_by_id("zst")  # Returns ZstandardArchiver
    """
    return get_global_archive_registry().get_by_id(format_id)


def register_archive_format(format_class):
    """Decorator to register custom archive format."""
    get_global_archive_registry().register(format_class)
    return format_class


__all__ = [
    # Standard formats
    "ZipArchiver",
    "TarArchiver",
    
    # Advanced formats (lazy install)
    "SevenZipArchiver",  # RANK #1
    "ZstandardArchiver",  # RANK #2
    "RarArchiver",  # RANK #3
    "BrotliArchiver",  # RANK #6
    "Lz4Archiver",  # RANK #7
    "ZpaqArchiver",  # RANK #8
    "WimArchiver",  # RANK #9
    "SquashfsArchiver",  # RANK #10
    
    # Registry functions
    "get_archiver_for_file",
    "get_archiver_by_id",
    "register_archive_format",
]

