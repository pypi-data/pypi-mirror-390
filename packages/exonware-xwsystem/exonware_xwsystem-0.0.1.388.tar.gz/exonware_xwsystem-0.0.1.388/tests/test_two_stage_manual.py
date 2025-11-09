#!/usr/bin/env python3
"""
Manual test for two-stage lazy loading.
Tests that imports succeed without dependencies, and deps install on usage.
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("="*70)
print("Two-Stage Lazy Loading Test")
print("="*70)
print()

# Stage 0: Enable lazy install
print("[TEST] Enabling lazy install for xwsystem...")
from exonware.xwsystem.utils.lazy_package import enable_lazy_install, set_lazy_install_mode, LazyInstallMode, install_import_hook

enable_lazy_install('xwsystem')
set_lazy_install_mode('xwsystem', LazyInstallMode.AUTO)
install_import_hook('xwsystem')
print("[OK] Lazy install enabled\n")

# Stage 1: Import xwsystem (should be fast, no deps installed)
print("[STAGE 1] Testing import exonware.xwsystem...")
start = time.time()
import exonware.xwsystem
elapsed = time.time() - start
print(f"[OK] Import succeeded in {elapsed:.3f}s\n")

# Stage 1b: Import AvroSerializer (should succeed even without fastavro)
print("[STAGE 1] Testing from exonware.xwsystem import AvroSerializer...")
start = time.time()
try:
    from exonware.xwsystem import AvroSerializer
    elapsed = time.time() - start
    print(f"[OK] Import succeeded in {elapsed:.3f}s")
    print(f"[INFO] AvroSerializer type: {type(AvroSerializer)}")
    print(f"[INFO] AvroSerializer repr: {AvroSerializer}")
    print()
except Exception as e:
    elapsed = time.time() - start
    print(f"[FAIL] Import failed in {elapsed:.3f}s: {e}\n")
    import traceback
    traceback.print_exc()

# Stage 2: Try to instantiate (should trigger dependency install)
print("[STAGE 2] Testing AvroSerializer() instantiation...")
start = time.time()
try:
    serializer = AvroSerializer()
    elapsed = time.time() - start
    print(f"[OK] Instantiation succeeded in {elapsed:.3f}s")
    print(f"[INFO] Serializer type: {type(serializer)}")
    print()
except Exception as e:
    elapsed = time.time() - start
    print(f"[FAIL] Instantiation failed in {elapsed:.3f}s: {e}\n")
    import traceback
    traceback.print_exc()

print("="*70)
print("Test Complete!")
print("="*70)

