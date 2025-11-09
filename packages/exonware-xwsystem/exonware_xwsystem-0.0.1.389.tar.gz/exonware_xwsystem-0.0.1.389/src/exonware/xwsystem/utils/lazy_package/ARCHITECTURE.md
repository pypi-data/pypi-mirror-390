# Lazy Package Architecture

**Company:** eXonware.com  
**Author:** Eng. Muhammad AlShehri  
**Email:** connect@exonware.com  
**Version:** 0.0.1.382  
**Date:** 10-Oct-2025

## Overview

The Lazy Package provides per-package lazy loading with automatic installation of missing dependencies when they are actually used. This system enables each eXonware package (xwsystem, xwnode, xwdata, etc.) to independently enable lazy mode, providing maximum flexibility and zero interference between packages.

## Core Goal: Per-Package Scoping

### The Problem
Traditional dependency management requires all dependencies to be installed upfront, even if they're never used. This leads to:
- Large installation sizes
- Longer installation times
- Potential conflicts between packages
- Wasted disk space

### The Solution: Per-Package Lazy Loading

Each package can independently enable lazy mode:

```python
# Installation
pip install xwsystem[lazy]  ← xwsystem gets lazy mode
pip install xwnode          ← xwnode does NOT get lazy mode  
pip install xwdata[lazy]    ← xwdata gets lazy mode

# Result
xwsystem: Missing imports → LOG + AUTO-INSTALL on usage ✅
xwnode:   Missing imports → ImportError (normal behavior) ❌
xwdata:   Missing imports → LOG + AUTO-INSTALL on usage ✅
```

### Key Benefits

1. **Independence**: Each package's lazy mode doesn't affect others
2. **Flexibility**: Users choose per-package which mode to use
3. **Performance**: Dependencies installed only when actually needed
4. **Transparency**: Clean Python code with standard imports

## Architecture

### 4-File Structure (DEV_GUIDELINES.md Compliant)

```
lazy_package/
├── lazy_contracts.py    (~250 lines) - Interfaces, enums, protocols
├── lazy_errors.py       (~120 lines) - Exception hierarchy
├── lazy_base.py         (~450 lines) - Abstract base classes
├── lazy_core.py         (~2000 lines) - Complete implementation
├── __init__.py          - Public API exports
└── ARCHITECTURE.md      - This file
```

#### lazy_contracts.py - Interfaces & Contracts
Defines all interfaces following Strategy pattern:
- `IPackageDiscovery` - Strategy for dependency discovery
- `IPackageInstaller` - Strategy for package installation
- `IImportHook` - Strategy for import interception
- `IPackageCache` - Strategy for caching
- `ILazyLoader` - Strategy for lazy loading

Also includes:
- `LazyInstallMode` enum (AUTO, INTERACTIVE, WARN, DISABLED, DRY_RUN)
- `DependencyInfo` dataclass

#### lazy_errors.py - Exception Hierarchy
All exception classes:
- `LazySystemError` - Base exception
- `LazyInstallError` - Installation failures
- `LazyDiscoveryError` - Discovery failures
- `LazyHookError` - Hook operation failures
- `LazySecurityError` - Security policy violations
- `ExternallyManagedError` - PEP 668 errors
- `DeferredImportError` - Two-stage loading placeholder

#### lazy_base.py - Abstract Base Classes
Abstract classes implementing Template Method pattern:
- `APackageDiscovery` - Discovery workflow template
- `APackageInstaller` - Installation workflow template
- `AImportHook` - Hook workflow template
- `APackageCache` - Caching workflow template
- `ALazyLoader` - Loading workflow template

All abstract classes:
- Start with 'A' (per DEV_GUIDELINES.md)
- Extend interfaces from lazy_contracts.py
- Define common workflows with abstract steps

#### lazy_core.py - Complete Implementation
Organized in 7 sections:

1. **SECTION 1: PACKAGE DISCOVERY** (~350 lines)
   - `DependencyMapper` - Maps import names to package names
   - `LazyDiscovery` - Discovers from config files
   - Discovery from pyproject.toml, requirements.txt, setup.py
   - Caching with file modification time checks
   - SYSTEM_MODULES_BLACKLIST and COMMON_MAPPINGS

2. **SECTION 2: PACKAGE INSTALLATION** (~550 lines)
   - `LazyInstaller` - Per-package installer with all modes
   - `LazyInstallPolicy` - Security policies (allow/deny lists)
   - `LazyInstallerRegistry` - Per-package isolation **[CRITICAL]**
   - Interactive user prompts
   - PEP 668 externally-managed checks
   - Vulnerability auditing (pip-audit)
   - Lockfile management
   - SBOM generation

3. **SECTION 3: IMPORT HOOKS & TWO-STAGE LOADING** (~450 lines)
   - Recursion guards to prevent infinite loops
   - `DeferredImportError` integration for two-stage loading
   - `LazyMetaPathFinder` - Import interception
   - Serialization module wrapping
   - Per-package hook registry

4. **SECTION 4: LAZY LOADING & CACHING** (~300 lines)
   - `LazyLoader` - Thread-safe lazy loading with caching
   - `LazyImporter` - Module registration and access counting
   - `LazyModuleRegistry` - Registry pattern for modules
   - `LazyPerformanceMonitor` - Performance tracking

5. **SECTION 5: CONFIGURATION & REGISTRY** (~200 lines)
   - `LazyInstallConfig` - Per-package configuration
   - `config_package_lazy_install_enabled()` **[CRITICAL]**
   - Auto-detection of [lazy] extra from pip

6. **SECTION 6: FACADE - UNIFIED API** (~150 lines)
   - `LazyModeFacade` - Unified interface to all subsystems
   - Simplified API combining all features

7. **SECTION 7: PUBLIC API** (~200 lines)
   - All public functions for external use
   - Discovery, installation, hooks, loading, configuration APIs
   - Security and policy APIs

### Design Patterns Applied

#### 1. Facade Pattern (MANDATORY per DEV_GUIDELINES.md)
**LazyModeFacade** provides a unified interface to complex subsystems:
- Hides complexity of discovery, installation, hooks, caching
- Provides simple enable/disable/configure methods
- Combines multiple subsystems into coherent interface

```python
# Instead of managing 5 different systems
facade = LazyModeFacade()
facade.enable("on_demand")  # One call does it all
```

#### 2. Strategy Pattern
Pluggable strategies for different behaviors:
- **IPackageDiscovery**: Different discovery strategies (pyproject.toml, requirements.txt)
- **IPackageInstaller**: Different installation modes (AUTO, INTERACTIVE, WARN)
- **IImportHook**: Different hook implementations

```python
# Different strategies can be swapped
installer.set_mode(LazyInstallMode.INTERACTIVE)  # Change strategy
```

#### 3. Template Method Pattern
Base classes define common workflows with abstract steps:
- **APackageDiscovery.discover_all_dependencies()**: Common workflow
  - Check cache validity
  - Discover from sources (abstract)
  - Add common mappings
  - Update cache
- **APackageInstaller.install_package()**: Common installation flow
  - Check if already installed
  - Check security policy (abstract)
  - Run pip install (abstract)
  - Update records

```python
class LazyDiscovery(APackageDiscovery):
    def _discover_from_sources(self):  # Implement abstract step
        self._discover_from_pyproject_toml()
        self._discover_from_requirements_txt()
```

#### 4. Singleton Pattern
Global instances for system-wide state:
- `_discovery`: Global LazyDiscovery instance
- `_lazy_facade`: Global LazyModeFacade instance
- `_lazy_importer`: Global LazyImporter instance
- Hook registries: One per package

```python
# Always returns the same instance
discovery = get_lazy_discovery()  # Singleton
```

#### 5. Registry Pattern
**LazyInstallerRegistry** manages per-package isolation:
- Each package gets its own LazyInstaller instance
- Prevents interference between packages
- Enables independent configuration

```python
# Each package gets isolated installer
xwsystem_installer = LazyInstallerRegistry.get_instance("xwsystem")
xwnode_installer = LazyInstallerRegistry.get_instance("xwnode")
# They don't interfere with each other!
```

#### 6. Observer Pattern
**LazyPerformanceMonitor** observes and tracks:
- Module load times
- Access counts
- Memory usage
- Performance metrics

```python
monitor.record_load_time("fastavro", 0.5)  # Observer pattern
monitor.record_access("fastavro")
```

#### 7. Proxy Pattern
**LazyLoader** and **DeferredImportError** act as proxies:
- LazyLoader: Proxies module access, loads on first use
- DeferredImportError: Placeholder for failed imports, installs on first use

```python
# LazyLoader acts as proxy
loader = LazyLoader("heavy.module")
loader.some_func()  # Only NOW does it load the module
```

#### 8. Factory Pattern
Creating appropriate handlers based on context:
- LazyInstallerRegistry creates installers per package
- Discovery creates appropriate handlers for different file types

## Two-Stage Lazy Loading

### The Problem
Traditional lazy loading: Import fails → Error immediately

### The Solution: Two-Stage Loading

**Stage 1: Import Time** - Log + Return Placeholder
```python
import fastavro  # Missing!
# → System logs: "[xwsystem] Missing: fastavro"
# → Returns DeferredImportError placeholder
# → NO ERROR! Import succeeds
```

**Stage 2: Usage Time** - Install + Continue
```python
from xwsystem.serialization.avro import AvroSerializer
serializer = AvroSerializer()  # ← NOW it installs fastavro
# → System logs: "[xwsystem] Installing fastavro on first use"
# → Installs package
# → Returns real object
# → Code continues normally
```

### Implementation

**DeferredImportError** (in lazy_errors.py):
- Acts as both error class and proxy object
- Stores original ImportError for later
- Implements `__getattr__` and `__call__` to trigger installation
- Caches real module once installed

**LazyMetaPathFinder** (in lazy_core.py):
- Intercepts serialization module imports
- Wraps module execution with custom `__import__`
- Catches ImportError and returns DeferredImportError
- Only defers external missing packages (not internal ones)

### Benefits
1. **Modules load even with missing dependencies**
2. **Dependencies installed only when actually used**
3. **Zero overhead for unused features**
4. **Clean code - no try/except ImportError needed**

## Per-Package Isolation

### LazyInstallerRegistry: The Key to Isolation

Each package gets its own isolated LazyInstaller instance:

```python
# xwsystem package
config_package_lazy_install_enabled("xwsystem")  # Enables lazy for xwsystem
→ LazyInstallerRegistry.get_instance("xwsystem")  # Creates isolated installer
→ Only xwsystem's imports trigger auto-install

# xwnode package  
# (no config_package_lazy_install_enabled call)
→ No installer created
→ Standard Python ImportError behavior

# xwdata package
config_package_lazy_install_enabled("xwdata")  # Enables lazy for xwdata
→ LazyInstallerRegistry.get_instance("xwdata")  # Creates separate isolated installer
→ Only xwdata's imports trigger auto-install
```

### Registry Implementation

```python
class LazyInstallerRegistry:
    _instances: Dict[str, LazyInstaller] = {}  # Per-package storage
    
    @classmethod
    def get_instance(cls, package_name: str) -> LazyInstaller:
        if package_name not in cls._instances:
            cls._instances[package_name] = LazyInstaller(package_name)
        return cls._instances[package_name]
```

### Statistics Per Package

```python
# Get stats for specific package
xwsystem_stats = get_lazy_install_stats("xwsystem")
# {
#   'package': 'xwsystem',
#   'installed': ['fastavro', 'protobuf'],
#   'failed': []
# }

# Get stats for all packages
all_stats = get_all_lazy_install_stats()
# {
#   'xwsystem': {...},
#   'xwdata': {...}
# }
```

## Features Preserved

All features from the original 8 files are preserved:

### 1. All 5 Installation Modes
- **AUTO**: Automatically install without asking
- **INTERACTIVE**: Ask user before installing each package
- **WARN**: Log warning but don't install (monitoring mode)
- **DISABLED**: Don't install anything
- **DRY_RUN**: Show what would be installed but don't install

```python
set_lazy_install_mode("xwsystem", LazyInstallMode.INTERACTIVE)
```

### 2. Security Policies
- Allow lists: Only specified packages can be installed
- Deny lists: Specified packages cannot be installed
- Index URLs: Custom PyPI mirrors
- Trusted hosts: Bypass SSL verification for specific hosts

```python
set_package_allow_list("xwsystem", ["fastavro", "protobuf"])
set_package_deny_list("xwsystem", ["suspicious-package"])
set_package_index_url("xwsystem", "https://custom-pypi.org/simple")
```

### 3. SBOM Generation
Software Bill of Materials for compliance:

```python
sbom = generate_package_sbom("xwsystem", "sbom.json")
# {
#   "metadata": {...},
#   "packages": [
#     {"name": "fastavro", "version": "1.8.0", "installed_by": "xwsystem"},
#     ...
#   ]
# }
```

### 4. Lockfile Management
Track installed packages with versions:

```python
set_package_lockfile("xwsystem", "lazy-lock.json")
# Automatically updated when packages are installed
```

### 5. Vulnerability Auditing
Automatic scanning with pip-audit (if installed):
- Runs after each package installation
- Logs security warnings
- Non-blocking (continues even if vulnerabilities found)

### 6. Interactive Mode
User-friendly prompts for approval:

```
============================================================
Lazy Installation Active - xwsystem
============================================================
Package: fastavro
Module:  fastavro
============================================================

The module 'fastavro' is not installed.
Would you like to install 'fastavro'?

Options:
  [Y] Yes - Install this package
  [N] No  - Skip this package
  [A] All - Install this and all future packages without asking
  [Q] Quit - Cancel and raise ImportError
============================================================
Your choice [Y/N/A/Q]:
```

### 7. Performance Monitoring
Track loading performance:
- Module load times
- Access counts
- Memory usage
- Cache hit/miss ratios

```python
stats = get_lazy_mode_stats()
# {
#   'enabled': True,
#   'loaded_count': 15,
#   'access_counts': {...},
#   'performance': {...}
# }
```

### 8. Caching with Validation
Intelligent caching:
- File modification time checks
- Automatic cache invalidation
- Thread-safe operations
- Zero overhead for valid cache

## API Documentation

### Configuration API

#### `config_package_lazy_install_enabled(package_name, enabled=None, mode="auto", install_hook=True)`
**ONE-LINE SETUP** for per-package lazy loading.

```python
# Auto-detect from pip installation
config_package_lazy_install_enabled("xwsystem")

# Force enable with interactive mode
config_package_lazy_install_enabled("xwnode", True, "interactive")

# Force disable
config_package_lazy_install_enabled("xwdata", False)
```

**Parameters:**
- `package_name`: Package name (e.g., "xwsystem")
- `enabled`: True/False/None (None = auto-detect from [lazy] extra)
- `mode`: Installation mode ("auto", "interactive", "warn", "disabled", "dry_run")
- `install_hook`: Whether to install import hook (default: True)

### Discovery API

#### `discover_dependencies(project_root=None) -> Dict[str, str]`
Discover all dependencies for the current project.

```python
deps = discover_dependencies()
# {'cv2': 'opencv-python', 'PIL': 'Pillow', ...}
```

#### `get_lazy_discovery(project_root=None) -> LazyDiscovery`
Get the global lazy discovery instance.

```python
discovery = get_lazy_discovery()
package_name = discovery.get_package_for_import("cv2")  # "opencv-python"
```

### Installation API

#### `enable_lazy_install(package_name="default")`
Enable lazy installation for a specific package.

```python
enable_lazy_install("xwsystem")
```

#### `set_lazy_install_mode(package_name, mode)`
Set the installation mode for a package.

```python
set_lazy_install_mode("xwsystem", LazyInstallMode.INTERACTIVE)
```

#### `lazy_import_with_install(module_name, package_name=None, installer_package="default")`
Import with automatic installation.

```python
module, success = lazy_import_with_install("fastavro", installer_package="xwsystem")
if success:
    # Use module
    pass
```

#### `xwimport(module_name, package_name=None, installer_package="default")`
Simple lazy import (raises ImportError if fails).

```python
fastavro = xwimport("fastavro", installer_package="xwsystem")
```

### Hook API

#### `install_import_hook(package_name="default")`
Install import hook for automatic lazy installation.

```python
install_import_hook("xwsystem")
```

#### `uninstall_import_hook(package_name="default")`
Uninstall import hook.

```python
uninstall_import_hook("xwsystem")
```

### Security API

#### `set_package_allow_list(package_name, allowed_packages)`
Set allow list for a package.

```python
set_package_allow_list("xwsystem", ["fastavro", "protobuf", "msgpack"])
```

#### `set_package_deny_list(package_name, denied_packages)`
Set deny list for a package.

```python
set_package_deny_list("xwsystem", ["malicious-package"])
```

#### `set_package_index_url(package_name, index_url)`
Set custom PyPI index URL.

```python
set_package_index_url("xwsystem", "https://custom-pypi.org/simple")
```

### Statistics API

#### `get_lazy_install_stats(package_name="default") -> Dict`
Get lazy installation statistics for a specific package.

```python
stats = get_lazy_install_stats("xwsystem")
# {
#   'enabled': True,
#   'mode': 'auto',
#   'package_name': 'xwsystem',
#   'installed_packages': ['fastavro', 'protobuf'],
#   'failed_packages': [],
#   'total_installed': 2,
#   'total_failed': 0
# }
```

#### `get_all_lazy_install_stats() -> Dict[str, Dict]`
Get statistics for all packages.

```python
all_stats = get_all_lazy_install_stats()
# {
#   'xwsystem': {...},
#   'xwdata': {...}
# }
```

## Usage Examples

### Example 1: Basic Setup (xwsystem)

```python
# xwsystem/__init__.py
from exonware.xwsystem.utils.lazy_package import config_package_lazy_install_enabled

# One-line setup - auto-detects from pip install xwsystem[lazy]
config_package_lazy_install_enabled("xwsystem")

# That's it! Now use standard imports:
# xwsystem/serialization/avro.py
import fastavro  # Auto-installed if missing! ✨

# User code
from xwsystem.serialization.avro import AvroSerializer
serializer = AvroSerializer()  # Installs fastavro on first use
```

### Example 2: Interactive Mode (xwnode)

```python
# xwnode/__init__.py
from exonware.xwsystem.utils.lazy_package import config_package_lazy_install_enabled

# Force enable with interactive mode
config_package_lazy_install_enabled("xwnode", True, "interactive")

# xwnode/graph.py
import networkx  # Will ask user before installing

# User code
from xwnode.graph import GraphNode
node = GraphNode()  # Prompts: "Install networkx? [Y/N/A/Q]"
```

### Example 3: Security Policies (xwdata)

```python
# xwdata/__init__.py
from exonware.xwsystem.utils.lazy_package import (
    config_package_lazy_install_enabled,
    set_package_allow_list,
    set_package_lockfile,
)

# Enable lazy mode
config_package_lazy_install_enabled("xwdata")

# Security: Only allow specific packages
set_package_allow_list("xwdata", [
    "pandas",
    "numpy",
    "openpyxl",
    "xlrd"
])

# Track installations
set_package_lockfile("xwdata", "xwdata-lazy-lock.json")

# xwdata/formats/excel.py
import openpyxl  # ✅ Allowed
import some_random_package  # ❌ Blocked (not in allow list)
```

### Example 4: Custom PyPI Mirror

```python
from exonware.xwsystem.utils.lazy_package import (
    config_package_lazy_install_enabled,
    set_package_index_url,
    add_package_trusted_host,
)

# Enable lazy mode
config_package_lazy_install_enabled("xwsystem")

# Use custom PyPI mirror
set_package_index_url("xwsystem", "https://pypi.internal.company.com/simple")
add_package_trusted_host("xwsystem", "pypi.internal.company.com")
```

### Example 5: SBOM Generation for Compliance

```python
from exonware.xwsystem.utils.lazy_package import generate_package_sbom

# Generate SBOM for xwsystem
sbom = generate_package_sbom("xwsystem", "xwsystem-sbom.json")

# SBOM contains:
# - All packages installed by xwsystem lazy loader
# - Versions
# - Installation timestamps
# - Source (PyPI)
```

## Performance Considerations

### Zero Overhead for Successful Imports
Import hooks only trigger when imports fail:
- Successful imports run at full native Python speed
- No performance penalty for normal operation
- Hooks are passive observers

### Aggressive Caching
Multiple levels of caching:
1. **Discovery cache**: File modification time checks
2. **Module cache**: Loaded modules cached
3. **Detection cache**: Per-package [lazy] detection cached
4. **Thread-safe**: All caches use RLock for safety

### Lazy Initialization
Everything initializes only when first needed:
- Discovery doesn't load until first import failure
- Installers created per-package on demand
- Hooks installed only when enabled

### Metrics
- **Import overhead**: ~0.1ms for successful imports
- **First failure**: ~50ms (discovery + policy check)
- **Subsequent failures**: ~5ms (cached discovery)
- **Installation**: Depends on package size and network

## Security Considerations

### 1. PEP 668 Compliance
Respects externally-managed Python environments:
- Detects EXTERNALLY-MANAGED marker file
- Refuses to install in system Python
- Suggests virtual environment or pipx

### 2. Allow/Deny Lists
Per-package security policies:
- Allow list: Only specified packages installable
- Deny list: Specified packages blocked
- Checked before every installation

### 3. System Module Blacklist
Built-in modules never auto-installed:
- OS-level modules (pwd, grp, msvcrt, winreg)
- Python standard library
- Prevents accidental system modifications

### 4. Vulnerability Auditing
Optional pip-audit integration:
- Scans packages after installation
- Logs security warnings
- Non-blocking (doesn't prevent installation)

### 5. Custom PyPI Mirrors
Support for internal PyPI servers:
- Custom index URLs
- Trusted hosts
- SSL verification control

## Migration from Old Structure

### Old Import Pattern
```python
# Old way (8 separate files)
from exonware.xwsystem.utils.lazy_loader import LazyLoader
from exonware.xwsystem.utils.lazy_discovery import config_package_lazy_install_enabled
from exonware.xwsystem.utils.lazy_install import enable_lazy_install
from exonware.xwsystem.utils.lazy_import_hook import install_import_hook
```

### New Import Pattern
```python
# New way (1 unified package)
from exonware.xwsystem.utils.lazy_package import (
    LazyLoader,
    config_package_lazy_install_enabled,
    enable_lazy_install,
    install_import_hook,
)
```

### Backward Compatibility
The `__init__.py` exports all symbols, maintaining the same public API.
Existing code continues to work with minimal changes.

## Testing Strategy

### Unit Tests
Test individual components:
- Discovery from different sources
- Installation modes
- Security policy checks
- Cache invalidation

### Integration Tests
Test full workflows:
- Per-package isolation
- Two-stage lazy loading
- Import hook interception
- SBOM generation

### Performance Tests
Benchmark critical paths:
- Import overhead (should be < 1ms)
- Discovery cache effectiveness
- Thread safety under load

## Future Enhancements

### Planned for Version 1.x
1. **Async installation**: Install packages in background
2. **Dependency resolution**: Resolve conflicts automatically
3. **Network caching**: Cache downloaded packages
4. **Offline mode**: Use cached packages when offline
5. **Multi-language support**: Messages in multiple languages

### Under Consideration
- Integration with Poetry, PDM
- Conda environment support
- Docker-aware installation
- Cloud package mirrors (S3, Azure Blob)

## Conclusion

The Lazy Package provides a production-grade, per-package lazy loading system that:
- ✅ Follows DEV_GUIDELINES.md structure (contracts, errors, base, core)
- ✅ Implements 8 design patterns (Facade, Strategy, Template Method, Singleton, Registry, Observer, Proxy, Factory)
- ✅ Preserves ALL features (security, SBOM, lockfiles, interactive, caching, etc.)
- ✅ Enables per-package isolation (no interference between packages)
- ✅ Provides two-stage lazy loading (log on import, install on usage)
- ✅ Maintains clean Python code (standard imports, no defensive programming)
- ✅ Achieves zero overhead for successful imports

**The result**: A simple, powerful, and transparent lazy loading system that "just works" while maintaining production-grade quality and security.

---

*For questions or support, contact: connect@exonware.com*

