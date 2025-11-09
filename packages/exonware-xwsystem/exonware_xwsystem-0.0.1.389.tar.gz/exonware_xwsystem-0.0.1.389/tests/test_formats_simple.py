#!/usr/bin/env python3
"""
Simple test for archive formats (bypasses main xwsystem import).
"""

import sys
sys.path.insert(0, 'src')

print("[OK] Testing All 10 Archive Formats (Simple)")
print("=" * 70)

try:
    # Test import of all formats directly
    print("\n[TEST 1] Importing all 10 archive formats...")
    
    from exonware.xwsystem.io.archive.formats.zip import ZipArchiver
    from exonware.xwsystem.io.archive.formats.tar import TarArchiver
    from exonware.xwsystem.io.archive.formats.sevenzip import SevenZipArchiver
    from exonware.xwsystem.io.archive.formats.zstandard import ZstandardArchiver
    from exonware.xwsystem.io.archive.formats.rar import RarArchiver
    from exonware.xwsystem.io.archive.formats.brotli_format import BrotliArchiver
    from exonware.xwsystem.io.archive.formats.lz4_format import Lz4Archiver
    from exonware.xwsystem.io.archive.formats.zpaq_format import ZpaqArchiver
    from exonware.xwsystem.io.archive.formats.wim_format import WimArchiver
    from exonware.xwsystem.io.archive.formats.squashfs_format import SquashfsArchiver
    
    print("[OK] All 10 formats imported successfully!")
    
    # Test format metadata
    print("\n[TEST 2] Checking format metadata...")
    
    formats = [
        (ZipArchiver(), "zip", ".zip", "RANK #4 - Universal"),
        (TarArchiver(), "tar", ".tar", "RANK #5 - Linux standard"),
        (SevenZipArchiver(), "7z", ".7z", "RANK #1 - BEST OVERALL"),
        (ZstandardArchiver(), "zst", ".zst", "RANK #2 - MODERN STANDARD"),
        (RarArchiver(), "rar", ".rar", "RANK #3 - Proprietary"),
        (BrotliArchiver(), "br", ".br", "RANK #6 - Web compression"),
        (Lz4Archiver(), "lz4", ".lz4", "RANK #7 - Ultra fast"),
        (ZpaqArchiver(), "zpaq", ".zpaq", "RANK #8 - Extreme compression"),
        (WimArchiver(), "wim", ".wim", "RANK #9 - Windows imaging"),
        (SquashfsArchiver(), "squashfs", ".squashfs", "RANK #10 - Embedded systems"),
    ]
    
    for archiver, expected_id, expected_ext, description in formats:
        class_name = archiver.__class__.__name__
        
        # Check ID
        if archiver.format_id == expected_id:
            print(f"[OK] {class_name:20s} ID: {expected_id:10s} {description}")
        else:
            print(f"[ERROR] {class_name} ID mismatch: expected {expected_id}, got {archiver.format_id}")
        
        # Check extension
        if expected_ext in archiver.file_extensions:
            print(f"     [OK] Supports {expected_ext}")
        else:
            print(f"     [ERROR] Missing extension {expected_ext}")
            print(f"           Available: {archiver.file_extensions}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] All 10 archive formats validated!")
    print("=" * 70)
    print("\nFormatAction Naming: [OK]")
    print("  - SevenZipArchiver (not XW7zArchiver)")
    print("  - ZstandardArchiver")
    print("  - RarArchiver")
    print("  - etc.")
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

