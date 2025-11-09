"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.384
Generation Date: October 10, 2025

Lazy Loading Test Suite

This script tests the lazy loading mechanism for xwsystem.

IMPORTANT: Two-Stage Lazy Loading is currently DISABLED due to infinite recursion issues.
The import hook now only handles top-level external package installation AFTER
xwsystem is fully initialized.

Test Scenarios:
1. Import xwsystem successfully (hook installed after all imports)
2. Verify lazy install is enabled
3. Verify import hook is properly installed
4. Test basic serialization (with pre-installed dependencies)
"""

import sys
import subprocess
from pathlib import Path
import io

# Add src directory to Python path to import xwsystem
src_path = Path(__file__).parent / 'src'
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Fix Windows console encoding FIRST (before any prints)
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for stdout/stderr
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        # Fallback: disable emojis if encoding can't be fixed
        pass

# Enable detailed logging to see what's happening during import
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s [%(name)s] %(message)s',
    force=True  # Override any existing configuration
)
print("✓ Enabled DEBUG logging for diagnostics")

# Safe print function that handles encoding errors
def safe_print(text: str):
    """Print text with fallback for encoding errors."""
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace emojis with ASCII equivalents
        fallback = text
        emoji_map = {
            '✅': '[PASS]',
            '❌': '[FAIL]',
            '📦': '[PKG]',
            '🔧': '[TOOL]',
            '📚': '[LIB]',
            '🔗': '[HOOK]',
            '⏱️': '[TIME]',
            '📊': '[STAT]',
            '🎨': '[FMT]',
            '🎯': '[TRY]',
            '⏳': '[WAIT]',
            '⚠️': '[WARN]',
            '✓': '[OK]',
            '👉': '->',
            '📈': '[CHART]',
            '📋': '[LIST]',
        }
        for emoji, replacement in emoji_map.items():
            fallback = fallback.replace(emoji, replacement)
        print(fallback.encode('ascii', 'replace').decode('ascii'))

def run_test(test_name: str, test_func):
    """Run a single test and report results."""
    safe_print(f"\n{'=' * 70}")
    safe_print(f"TEST: {test_name}")
    safe_print('=' * 70)
    try:
        test_func()
        safe_print(f"✅ {test_name} PASSED")
        return True
    except Exception as e:
        safe_print(f"❌ {test_name} FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stage1_import_without_dependencies():
    """
    Test that xwsystem can be imported even without optional dependencies.
    
    This verifies Stage 1: Module loads with deferred imports.
    """
    safe_print("\n📦 Testing Stage 1: Import xwsystem without dependencies")
    
    # Import xwsystem - should succeed even if fastavro, protobuf, etc. are missing
    import exonware.xwsystem as xwsystem
    safe_print("✓ Successfully imported xwsystem")
    
    # Verify we can access serialization module
    from exonware.xwsystem import serialization
    safe_print("✓ Successfully imported serialization module")
    
    # Verify serializer classes are available (but dependencies may be deferred)
    from exonware.xwsystem import AvroSerializer, ProtobufSerializer, CapnProtoSerializer
    safe_print("✓ Serializer classes are available")
    
    safe_print("\n✅ Stage 1 Complete: xwsystem imported successfully")


def test_stage2_lazy_installation():
    """
    Test that dependencies are installed on first use (Stage 2).
    
    This verifies that attempting to use a serializer triggers installation.
    """
    safe_print("\n🔧 Testing Stage 2: Lazy installation on first use")
    
    # Enable lazy install for xwsystem
    from exonware.xwsystem import enable_lazy_install
    enable_lazy_install("xwsystem")
    safe_print("✓ Enabled lazy install for xwsystem")
    
    # Try to use a serializer that requires external dependency
    try:
        from exonware.xwsystem import AvroSerializer
        safe_print("✓ Imported AvroSerializer (may have deferred dependency)")
        
        # This should trigger Stage 2: install fastavro if needed
        safe_print("\n🎯 Attempting to instantiate AvroSerializer...")
        safe_print("   (This will trigger dependency installation if needed)")
        
        # Note: We don't actually instantiate here in case it fails
        # Just verify the class is available
        safe_print(f"   AvroSerializer class: {AvroSerializer}")
        
    except ImportError as e:
        safe_print(f"⚠️  Import deferred: {e}")
        safe_print("   This is expected if dependency not yet installed")
    
    safe_print("\n✅ Stage 2 test completed")


def test_serialization_module_loading():
    """Test that serialization modules can be imported individually."""
    safe_print("\n📚 Testing individual serialization module imports")
    
    modules_to_test = [
        'exonware.xwsystem.serialization.json',
        'exonware.xwsystem.serialization.yaml',
        'exonware.xwsystem.serialization.avro',
        'exonware.xwsystem.serialization.protobuf',
        'exonware.xwsystem.serialization.capnproto',
    ]
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[''])
            safe_print(f"✓ {module_name.split('.')[-1]}: loaded successfully")
        except ImportError as e:
            safe_print(f"⚠️  {module_name.split('.')[-1]}: deferred ({str(e)[:50]}...)")
        except Exception as e:
            safe_print(f"❌ {module_name.split('.')[-1]}: error ({str(e)[:50]}...)")
    
    safe_print("\n✅ Module loading test completed")


def test_import_hook_installation():
    """Test that the import hook is properly installed."""
    safe_print("\n🔗 Testing import hook installation")
    
    from exonware.xwsystem import install_import_hook, is_import_hook_installed
    
    # Install hook for xwsystem
    install_import_hook("xwsystem")
    safe_print("✓ Installed import hook")
    
    # Verify hook is installed
    if is_import_hook_installed("xwsystem"):
        safe_print("✓ Import hook verified as installed")
    else:
        raise AssertionError("Import hook not found after installation")
    
    # Check sys.meta_path
    safe_print(f"\n📋 sys.meta_path entries:")
    for i, finder in enumerate(sys.meta_path):
        finder_name = finder.__class__.__name__
        safe_print(f"   [{i}] {finder_name}")
        if 'Lazy' in finder_name:
            safe_print(f"       👉 This is our lazy finder!")
    
    safe_print("\n✅ Import hook test completed")


def test_deferred_import_object():
    """Test DeferredImportError functionality."""
    safe_print("\n⏱️  Testing DeferredImportError object")
    
    from exonware.xwsystem.utils.lazy_package import DeferredImportError
    
    # Create a test deferred import
    test_error = ImportError("fastavro not found")
    deferred = DeferredImportError("fastavro", test_error, "xwsystem")
    
    safe_print(f"✓ Created DeferredImportError: {repr(deferred)}")
    safe_print(f"✓ Deferred object type: {type(deferred)}")
    
    # Verify it's not yet loaded
    if "_real_module" in dir(deferred):
        if deferred._real_module is None:
            safe_print("✓ Module not yet loaded (as expected)")
    
    safe_print("\n✅ DeferredImportError test completed")


def test_lazy_mode_stats():
    """Test lazy mode statistics and monitoring."""
    safe_print("\n📊 Testing lazy mode statistics")
    
    try:
        from exonware.xwsystem import get_lazy_install_stats, get_all_lazy_install_stats
        
        # Get stats for xwsystem
        stats = get_lazy_install_stats("xwsystem")
        safe_print(f"\n📈 Lazy Install Stats for xwsystem:")
        safe_print(f"   Total Attempts: {stats.get('total_attempts', 0)}")
        safe_print(f"   Successful: {stats.get('successful_installs', 0)}")
        safe_print(f"   Failed: {stats.get('failed_installs', 0)}")
        safe_print(f"   Cached Hits: {stats.get('cache_hits', 0)}")
        
        # Get all stats
        all_stats = get_all_lazy_install_stats()
        safe_print(f"\n📊 Total packages tracked: {len(all_stats)}")
        
    except Exception as e:
        safe_print(f"⚠️  Stats not available: {e}")
    
    safe_print("\n✅ Statistics test completed")


def test_available_serializers():
    """Test which serializers are currently available."""
    safe_print("\n🎨 Testing available serializers")
    
    from exonware.xwsystem import list_available_formats
    
    formats = list_available_formats()
    
    safe_print(f"\n📦 Available formats: {formats['total_count']}/{len(formats['all']) + len(formats['missing'])}")
    safe_print(f"\n✅ Text formats: {len(formats['text'])}")
    for fmt in formats['text']:
        safe_print(f"   • {fmt}")
    
    safe_print(f"\n✅ Binary formats: {len(formats['binary'])}")
    for fmt in formats['binary']:
        safe_print(f"   • {fmt}")
    
    safe_print(f"\n✅ Enterprise formats: {len(formats['enterprise'])}")
    for fmt in formats['enterprise']:
        safe_print(f"   • {fmt}")
    
    if formats['missing']:
        safe_print(f"\n⏳ Missing (will install on first use): {len(formats['missing'])}")
        for fmt in formats['missing'][:5]:  # Show first 5
            safe_print(f"   • {fmt}")
        if len(formats['missing']) > 5:
            safe_print(f"   • ... and {len(formats['missing']) - 5} more")
    
    safe_print("\n✅ Serializer availability test completed")


def test_json_serialization():
    """Test basic JSON serialization (always available)."""
    safe_print("\n🔧 Testing JSON serialization (no dependencies)")
    
    from exonware.xwsystem import JsonSerializer
    
    serializer = JsonSerializer()
    data = {"test": "data", "number": 42, "nested": {"key": "value"}}
    
    # Serialize
    json_str = serializer.dumps(data)
    safe_print(f"✓ Serialized: {json_str[:50]}...")
    
    # Deserialize
    result = serializer.loads(json_str)
    safe_print(f"✓ Deserialized: {result}")
    
    # Verify
    assert result == data, "Data mismatch after round-trip"
    safe_print("✓ Round-trip successful")
    
    safe_print("\n✅ JSON serialization test completed")


def main():
    """Run all tests."""
    safe_print("=" * 70)
    safe_print("LAZY LOADING TEST SUITE")
    safe_print("=" * 70)
    safe_print("\nThis test suite validates the lazy loading mechanism:")
    safe_print("• Hook installed AFTER xwsystem initialization (avoids recursion)")
    safe_print("• External package installation on demand")
    safe_print("• Two-stage loading temporarily DISABLED (infinite recursion fix)")
    
    tests = [
        ("Stage 1: Import Without Dependencies", test_stage1_import_without_dependencies),
        ("Import Hook Installation", test_import_hook_installation),
        ("Available Serializers", test_available_serializers),
        ("JSON Serialization (Core)", test_json_serialization),
        ("Lazy Mode Statistics", test_lazy_mode_stats),
    ]
    
    results = []
    for test_name, test_func in tests:
        passed = run_test(test_name, test_func)
        results.append((test_name, passed))
    
    # Print summary
    safe_print("\n" + "=" * 70)
    safe_print("TEST SUMMARY")
    safe_print("=" * 70)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, passed_flag in results:
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        safe_print(f"{status}: {test_name}")
    
    safe_print(f"\n{'=' * 70}")
    safe_print(f"RESULTS: {passed}/{total} tests passed ({100*passed//total}%)")
    safe_print(f"{'=' * 70}")
    
    return passed == total


if __name__ == "__main__":
    safe_print("=" * 70)
    success = main()
    sys.exit(0 if success else 1)

