#!/usr/bin/env python3
"""
#exonware/xwsystem/tests/verify_installation.py

Verify xwsystem installation and basic functionality.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 01-Nov-2025

Usage:
    python tests/verify_installation.py
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        # Set UTF-8 encoding for Windows console
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        # Fallback: disable emoji if encoding fails
        pass

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def verify_import():
    """Verify caching module can be imported."""
    try:
        # Import directly from caching submodule to avoid package-level imports
        from exonware.xwsystem.caching.lru_cache import LRUCache
        from exonware.xwsystem.caching.lfu_cache import LFUCache
        from exonware.xwsystem.caching.ttl_cache import TTLCache
        print("✅ Caching module import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Import failed with error: {e}")
        return False


def verify_caching_functionality():
    """Verify caching module works."""
    try:
        from exonware.xwsystem.caching.lru_cache import LRUCache
        
        cache = LRUCache(capacity=10)
        cache.put('test_key', 'test_value')
        result = cache.get('test_key')
        
        if result == 'test_value':
            print("✅ Caching functionality works")
            return True
        else:
            print("❌ Caching functionality failed: unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ Caching functionality failed: {e}")
        return False


def verify_dependencies():
    """Verify critical dependencies are available."""
    try:
        import pytest
        print("✅ pytest available")
        return True
    except ImportError as e:
        print(f"❌ Dependency check failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("="*80)
    print("🔍 Verifying xwsystem caching module installation...")
    print("="*80)
    print()

    checks = [
        ("Caching Module Import", verify_import),
        ("Caching Functionality", verify_caching_functionality),
        ("Dependencies", verify_dependencies),
    ]

    results = []
    for name, check_func in checks:
        print(f"Testing {name}...")
        results.append(check_func())
        print()

    print("="*80)
    if all(results):
        print("🎉 SUCCESS! xwsystem caching module is ready to use!")
        print("="*80)
        sys.exit(0)
    else:
        print("💥 FAILED! Some checks did not pass.")
        print("="*80)
        sys.exit(1)


if __name__ == "__main__":
    main()
