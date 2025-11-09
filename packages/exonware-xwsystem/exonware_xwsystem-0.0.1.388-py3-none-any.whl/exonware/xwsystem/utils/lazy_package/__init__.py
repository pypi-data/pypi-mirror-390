"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_package/__init__.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 10-Oct-2025

Lazy Package - Unified Lazy Loading System

This package provides per-package lazy loading with automatic installation
of missing dependencies. It consolidates all lazy loading functionality into
a clean, well-structured module following DEV_GUIDELINES.md.

Design Patterns:
- Facade: Unified API (LazySystemFacade, LazyModeFacade)
- Strategy: Pluggable discovery/installation/caching strategies
- Template Method: Base classes define common workflows
- Singleton: Global instances for system-wide state
- Registry: Per-package isolation (LazyInstallerRegistry)
- Observer: Performance monitoring
- Proxy: Deferred loading (LazyLoader, DeferredImportError)
- Factory: Handler creation

Core Goal: Per-Package Lazy Loading
Each package (xwsystem, xwnode, xwdata) can independently enable lazy mode.
Only packages installed with [lazy] extra get auto-installation.

Quick Start:
    # In your package's __init__.py
    from exonware.xwsystem.utils.lazy_package import config_package_lazy_install_enabled
    config_package_lazy_install_enabled("yourpackage")  # Auto-detect from pip install

Usage:
    # Then just use normal Python imports!
    import fastavro  # Missing? Auto-installed! ✨
    import pandas    # Missing? Auto-installed! ✨
"""

# Import all from submodules
from .lazy_contracts import (
    # Enums
    LazyInstallMode,
    PathType,
    # Dataclasses
    DependencyInfo,
    # Interfaces
    IPackageDiscovery,
    IPackageInstaller,
    IImportHook,
    IPackageCache,
    ILazyLoader,
)

from .lazy_errors import (
    # Exceptions
    LazySystemError,
    LazyInstallError,
    LazyDiscoveryError,
    LazyHookError,
    LazySecurityError,
    ExternallyManagedError,
    DeferredImportError,
)

from .lazy_base import (
    # Abstract base classes
    APackageDiscovery,
    APackageInstaller,
    AImportHook,
    APackageCache,
    ALazyLoader,
)

from .lazy_core import (
    # Core classes
    DependencyMapper,
    LazyDiscovery,
    LazyInstaller,
    LazyInstallPolicy,
    LazyInstallerRegistry,
    LazyImportHook,
    LazyMetaPathFinder,
    LazyLoader,
    LazyImporter,
    LazyModuleRegistry,
    LazyPerformanceMonitor,
    LazyInstallConfig,
    LazyModeFacade,
    
    # Discovery functions
    get_lazy_discovery,
    discover_dependencies,
    export_dependency_mappings,
    
    # Install functions
    enable_lazy_install,
    disable_lazy_install,
    is_lazy_install_enabled,
    set_lazy_install_mode,
    get_lazy_install_mode,
    install_missing_package,
    install_and_import,
    get_lazy_install_stats,
    get_all_lazy_install_stats,
    lazy_import_with_install,
    xwimport,
    
    # Hook functions
    install_import_hook,
    uninstall_import_hook,
    is_import_hook_installed,
    
    # Lazy loading functions
    enable_lazy_imports,
    disable_lazy_imports,
    is_lazy_import_enabled,
    lazy_import,
    register_lazy_module,
    preload_module,
    get_lazy_module,
    get_loading_stats,
    preload_frequently_used,
    get_lazy_import_stats,
    
    # Lazy mode facade functions
    enable_lazy_mode,
    disable_lazy_mode,
    is_lazy_mode_enabled,
    get_lazy_mode_stats,
    configure_lazy_mode,
    preload_modules,
    optimize_lazy_mode,
    
    # Configuration
    config_package_lazy_install_enabled,
    
    # Security & Policy
    set_package_allow_list,
    set_package_deny_list,
    add_to_package_allow_list,
    add_to_package_deny_list,
    set_package_index_url,
    set_package_extra_index_urls,
    add_package_trusted_host,
    set_package_lockfile,
    generate_package_sbom,
    check_externally_managed_environment,
)

# Version info
__version__ = "0.0.1.382"
__author__ = "Eng. Muhammad AlShehri"
__email__ = "connect@exonware.com"
__company__ = "eXonware.com"

# Export all
__all__ = [
    # Enums
    'LazyInstallMode',
    'PathType',
    
    # Dataclasses
    'DependencyInfo',
    
    # Interfaces
    'IPackageDiscovery',
    'IPackageInstaller',
    'IImportHook',
    'IPackageCache',
    'ILazyLoader',
    
    # Exceptions
    'LazySystemError',
    'LazyInstallError',
    'LazyDiscoveryError',
    'LazyHookError',
    'LazySecurityError',
    'ExternallyManagedError',
    'DeferredImportError',
    
    # Abstract base classes
    'APackageDiscovery',
    'APackageInstaller',
    'AImportHook',
    'APackageCache',
    'ALazyLoader',
    
    # Core classes
    'DependencyMapper',
    'LazyDiscovery',
    'LazyInstaller',
    'LazyInstallPolicy',
    'LazyInstallerRegistry',
    'LazyImportHook',
    'LazyMetaPathFinder',
    'LazyLoader',
    'LazyImporter',
    'LazyModuleRegistry',
    'LazyPerformanceMonitor',
    'LazyInstallConfig',
    'LazyModeFacade',
    
    # Discovery functions
    'get_lazy_discovery',
    'discover_dependencies',
    'export_dependency_mappings',
    
    # Install functions
    'enable_lazy_install',
    'disable_lazy_install',
    'is_lazy_install_enabled',
    'set_lazy_install_mode',
    'get_lazy_install_mode',
    'install_missing_package',
    'install_and_import',
    'get_lazy_install_stats',
    'get_all_lazy_install_stats',
    'lazy_import_with_install',
    'xwimport',
    
    # Hook functions
    'install_import_hook',
    'uninstall_import_hook',
    'is_import_hook_installed',
    
    # Lazy loading functions
    'enable_lazy_imports',
    'disable_lazy_imports',
    'is_lazy_import_enabled',
    'lazy_import',
    'register_lazy_module',
    'preload_module',
    'get_lazy_module',
    'get_loading_stats',
    'preload_frequently_used',
    'get_lazy_import_stats',
    
    # Lazy mode facade functions
    'enable_lazy_mode',
    'disable_lazy_mode',
    'is_lazy_mode_enabled',
    'get_lazy_mode_stats',
    'configure_lazy_mode',
    'preload_modules',
    'optimize_lazy_mode',
    
    # Configuration
    'config_package_lazy_install_enabled',
    
    # Security & Policy
    'set_package_allow_list',
    'set_package_deny_list',
    'add_to_package_allow_list',
    'add_to_package_deny_list',
    'set_package_index_url',
    'set_package_extra_index_urls',
    'add_package_trusted_host',
    'set_package_lockfile',
    'generate_package_sbom',
    'check_externally_managed_environment',
]

