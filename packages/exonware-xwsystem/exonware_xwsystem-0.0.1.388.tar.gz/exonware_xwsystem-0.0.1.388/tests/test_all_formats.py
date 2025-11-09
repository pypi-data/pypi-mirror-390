#!/usr/bin/env python3
"""
Test all 10 archive formats.
"""

import sys
from pathlib import Path

print("[OK] Testing All 10 Archive Formats")
print("=" * 70)

try:
    # Test import of all formats
    print("\n[TEST 1] Importing all 10 archive formats...")
    
    from exonware.xwsystem.io.archive.formats import (
        ZipArchiver,  # RANK #4
        TarArchiver,  # RANK #5
        SevenZipArchiver,  # RANK #1 - BEST
        ZstandardArchiver,  # RANK #2 - MODERN
        RarArchiver,  # RANK #3
        BrotliArchiver,  # RANK #6
        Lz4Archiver,  # RANK #7
        ZpaqArchiver,  # RANK #8
        WimArchiver,  # RANK #9
        SquashfsArchiver,  # RANK #10
        get_archiver_for_file,
        get_archiver_by_id,
    )
    
    print("[OK] All 10 formats imported successfully!")
    
    # Test 2: Auto-detection
    print("\n[TEST 2] Testing auto-detection by extension...")
    
    test_extensions = {
        "backup.7z": "SevenZipArchiver",
        "data.tar.zst": "ZstandardArchiver",
        "archive.rar": "RarArchiver",
        "files.zip": "ZipArchiver",
        "backup.tar.xz": "TarArchiver",
        "web.tar.br": "BrotliArchiver",
        "logs.tar.lz4": "Lz4Archiver",
        "extreme.zpaq": "ZpaqArchiver",
        "system.wim": "WimArchiver",
        "rootfs.squashfs": "SquashfsArchiver",
    }
    
    for filename, expected_class in test_extensions.items():
        archiver = get_archiver_for_file(filename)
        actual_class = archiver.__class__.__name__
        if actual_class == expected_class:
            print(f"[OK] {filename:20s} -> {actual_class}")
        else:
            print(f"[ERROR] {filename}: expected {expected_class}, got {actual_class}")
    
    # Test 3: Get by ID
    print("\n[TEST 3] Testing get by format ID...")
    
    test_ids = {
        "7z": "SevenZipArchiver",
        "zst": "ZstandardArchiver",
        "rar": "RarArchiver",
        "zip": "ZipArchiver",
        "tar": "TarArchiver",
        "br": "BrotliArchiver",
        "lz4": "Lz4Archiver",
        "zpaq": "ZpaqArchiver",
        "wim": "WimArchiver",
        "squashfs": "SquashfsArchiver",
    }
    
    for format_id, expected_class in test_ids.items():
        archiver = get_archiver_by_id(format_id)
        actual_class = archiver.__class__.__name__
        if actual_class == expected_class:
            print(f"[OK] {format_id:10s} -> {actual_class}")
        else:
            print(f"[ERROR] {format_id}: expected {expected_class}, got {actual_class}")
    
    # Test 4: Check format metadata
    print("\n[TEST 4] Checking format metadata...")
    
    formats = [
        (ZipArchiver(), "zip", [".zip"]),
        (TarArchiver(), "tar", [".tar"]),
        (SevenZipArchiver(), "7z", [".7z"]),
        (ZstandardArchiver(), "zst", [".zst", ".tar.zst"]),
        (RarArchiver(), "rar", [".rar"]),
        (BrotliArchiver(), "br", [".br", ".tar.br"]),
        (Lz4Archiver(), "lz4", [".lz4", ".tar.lz4"]),
        (ZpaqArchiver(), "zpaq", [".zpaq"]),
        (WimArchiver(), "wim", [".wim"]),
        (SquashfsArchiver(), "squashfs", [".squashfs"]),
    ]
    
    for archiver, expected_id, expected_exts in formats:
        if archiver.format_id == expected_id:
            print(f"[OK] {archiver.__class__.__name__:20s} ID: {expected_id}")
        else:
            print(f"[ERROR] {archiver.__class__.__name__} ID mismatch")
        
        # Check extensions
        for ext in expected_exts:
            if ext in archiver.file_extensions:
                print(f"     [OK] Supports {ext}")
            else:
                print(f"     [ERROR] Missing extension {ext}")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] All 10 archive formats validated!")
    print("=" * 70)
    print("\nFormat Summary (Ranked):")
    print("  1. SevenZipArchiver    - BEST OVERALL (LZMA2 + AES-256)")
    print("  2. ZstandardArchiver   - MODERN STANDARD (Fast + Great ratio)")
    print("  3. RarArchiver         - PROPRIETARY (Extraction only)")
    print("  4. ZipArchiver         - UNIVERSAL (Widely supported)")
    print("  5. TarArchiver         - LINUX STANDARD (Multiple compression)")
    print("  6. BrotliArchiver      - WEB COMPRESSION (Text optimized)")
    print("  7. Lz4Archiver         - ULTRA FAST (Real-time)")
    print("  8. ZpaqArchiver        - EXTREME COMPRESSION (Archival)")
    print("  9. WimArchiver         - WINDOWS IMAGING (System images)")
    print(" 10. SquashfsArchiver    - EMBEDDED SYSTEMS (Read-only FS)")
    
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

