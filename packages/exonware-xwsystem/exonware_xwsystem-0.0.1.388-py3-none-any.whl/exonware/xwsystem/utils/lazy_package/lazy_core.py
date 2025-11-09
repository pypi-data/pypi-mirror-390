"""
#exonware/xwsystem/src/exonware/xwsystem/utils/lazy_package/lazy_core.py

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.388
Generation Date: 10-Oct-2025

Lazy Loading System - Core Implementation

This module consolidates all lazy loading functionality into a single implementation
following DEV_GUIDELINES.md structure. It provides per-package lazy loading with:
- Automatic dependency discovery
- Secure package installation
- Import hooks for two-stage loading
- Performance monitoring and caching
- SBOM generation and lockfile management

Design Patterns Applied:
- Facade: LazySystemFacade provides unified API
- Strategy: Pluggable discovery/installation strategies
- Template Method: Base classes define workflows
- Singleton: Global instances for system-wide state
- Registry: Per-package isolation
- Observer: Performance monitoring
- Proxy: Deferred loading

Core Goal: Per-Package Lazy Loading
- Each package (xwsystem, xwnode, xwdata) can independently enable lazy mode
- Only packages installed with [lazy] extra get auto-installation
- Logs missing imports per package
- Installs on first actual usage (two-stage loading)
"""

import os
import re
import json
import toml
import sys
import subprocess
import importlib
import importlib.util
import builtins
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from types import ModuleType

from .lazy_contracts import DependencyInfo, LazyInstallMode
from .lazy_errors import (
    LazySystemError,
    LazyInstallError,
    LazyDiscoveryError,
    ExternallyManagedError,
    DeferredImportError,
)
from .lazy_base import (
    APackageDiscovery,
    APackageInstaller,
    AImportHook,
    ALazyLoader,
)
from ...config.logging_setup import get_logger

logger = get_logger("xwsystem.utils.lazy_package")


# =============================================================================
# SECTION 1: PACKAGE DISCOVERY (~350 lines)
# =============================================================================

class DependencyMapper:
    """
    Maps import names to package names using dynamic discovery.
    Optimized with caching to avoid repeated file I/O.
    """
    
    __slots__ = ('_discovery', '_package_import_mapping', '_import_package_mapping', '_cached', '_lock')
    
    def __init__(self):
        """Initialize dependency mapper."""
        self._discovery = None  # Lazy init to avoid circular imports
        self._package_import_mapping = {}
        self._import_package_mapping = {}
        self._cached = False
        self._lock = threading.RLock()
    
    def _get_discovery(self):
        """Get discovery instance (lazy init)."""
        if self._discovery is None:
            self._discovery = get_lazy_discovery()
        return self._discovery
    
    def _ensure_mappings_cached(self) -> None:
        """Ensure mappings are cached (lazy initialization)."""
        if self._cached:
            return
        
        with self._lock:
            if self._cached:
                return
            
            discovery = self._get_discovery()
            self._package_import_mapping = discovery.get_package_import_mapping()
            self._import_package_mapping = discovery.get_import_package_mapping()
            self._cached = True
    
    def get_package_name(self, import_name: str) -> Optional[str]:
        """Get package name from import name."""
        if import_name in LazyDiscovery.SYSTEM_MODULES_BLACKLIST:
            logger.debug(f"Module '{import_name}' is in system blacklist, skipping auto-install")
            return None
        
        self._ensure_mappings_cached()
        return self._import_package_mapping.get(import_name, import_name)
    
    def get_import_names(self, package_name: str) -> List[str]:
        """Get all possible import names for a package."""
        self._ensure_mappings_cached()
        return self._package_import_mapping.get(package_name, [package_name])
    
    def get_package_import_mapping(self) -> Dict[str, List[str]]:
        """Get complete package to import names mapping."""
        self._ensure_mappings_cached()
        return self._package_import_mapping.copy()
    
    def get_import_package_mapping(self) -> Dict[str, str]:
        """Get complete import to package name mapping."""
        self._ensure_mappings_cached()
        return self._import_package_mapping.copy()


class LazyDiscovery(APackageDiscovery):
    """
    Discovers dependencies from project configuration sources.
    Implements caching with file modification time checks.
    """
    
    # System/built-in modules that should NEVER be auto-installed
    SYSTEM_MODULES_BLACKLIST = {
        'pwd', 'grp', 'spwd', 'crypt', 'nis', 'syslog', 'termios', 'tty', 'pty',
        'fcntl', 'resource', 'msvcrt', 'winreg', 'winsound', '_winapi',
        'rpython', 'rply', 'rnc2rng', '_dbm',
        'sys', 'os', 'io', 'time', 'datetime', 'json', 'csv', 'math',
        'random', 're', 'collections', 'itertools', 'functools', 'operator',
        'pathlib', 'shutil', 'glob', 'tempfile', 'pickle', 'copy', 'types',
        'typing', 'abc', 'enum', 'dataclasses', 'contextlib', 'warnings',
        'logging', 'threading', 'multiprocessing', 'subprocess', 'queue',
        'socket', 'select', 'signal', 'asyncio', 'concurrent', 'email',
        'http', 'urllib', 'xml', 'html', 'sqlite3', 'base64', 'hashlib',
        'hmac', 'secrets', 'ssl', 'binascii', 'struct', 'array', 'weakref',
        'gc', 'inspect', 'traceback', 'atexit', 'codecs', 'locale', 'gettext',
        'argparse', 'optparse', 'configparser', 'fileinput', 'stat', 'platform',
        'unittest', 'doctest', 'pdb', 'profile', 'cProfile', 'timeit', 'trace',
    }
    
    # Common import name to package name mappings
    COMMON_MAPPINGS = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'Pillow': 'Pillow',
        'yaml': 'PyYAML',
        'sklearn': 'scikit-learn',
        'bs4': 'beautifulsoup4',
        'dateutil': 'python-dateutil',
        'requests_oauthlib': 'requests-oauthlib',
        'google': 'google-api-python-client',
        'jwt': 'PyJWT',
        'crypto': 'pycrypto',
        'Crypto': 'pycrypto',
        'MySQLdb': 'mysqlclient',
        'psycopg2': 'psycopg2-binary',
        'bson': 'pymongo',
        'lxml': 'lxml',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'plotly': 'plotly',
        'django': 'Django',
        'flask': 'Flask',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pytest': 'pytest',
        'black': 'black',
        'isort': 'isort',
        'mypy': 'mypy',
        'psutil': 'psutil',
        'colorama': 'colorama',
        'pytz': 'pytz',
        'aiofiles': 'aiofiles',
        'watchdog': 'watchdog',
        'wand': 'Wand',
        'exifread': 'ExifRead',
        'piexif': 'piexif',
        'rawpy': 'rawpy',
        'imageio': 'imageio',
        'scipy': 'scipy',
        'scikit-image': 'scikit-image',
        'opencv-python': 'opencv-python',
        'opencv-contrib-python': 'opencv-contrib-python',
    }
    
    def _discover_from_sources(self) -> None:
        """Discover dependencies from all sources."""
        self._discover_from_pyproject_toml()
        self._discover_from_requirements_txt()
        self._discover_from_setup_py()
        self._discover_from_custom_config()
    
    def _is_cache_valid(self) -> bool:
        """Check if cached dependencies are still valid."""
        if not self._cache_valid or not self._cached_dependencies:
            return False
        
        config_files = [
            self.project_root / 'pyproject.toml',
            self.project_root / 'requirements.txt',
            self.project_root / 'setup.py',
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    current_mtime = config_file.stat().st_mtime
                    cached_mtime = self._file_mtimes.get(str(config_file), 0)
                    if current_mtime > cached_mtime:
                        return False
                except:
                    return False
        
        return True
    
    def _update_file_mtimes(self) -> None:
        """Update file modification times for cache validation."""
        config_files = [
            self.project_root / 'pyproject.toml',
            self.project_root / 'requirements.txt',
            self.project_root / 'setup.py',
        ]
        for config_file in config_files:
            if config_file.exists():
                try:
                    self._file_mtimes[str(config_file)] = config_file.stat().st_mtime
                except:
                    pass
    
    def _discover_from_pyproject_toml(self) -> None:
        """Discover dependencies from pyproject.toml."""
        pyproject_path = self.project_root / 'pyproject.toml'
        if not pyproject_path.exists():
            return
        
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                data = toml.load(f)
            
            dependencies = []
            if 'project' in data and 'dependencies' in data['project']:
                dependencies.extend(data['project']['dependencies'])
            
            if 'project' in data and 'optional-dependencies' in data['project']:
                for group_name, group_deps in data['project']['optional-dependencies'].items():
                    dependencies.extend(group_deps)
            
            if 'build-system' in data and 'requires' in data['build-system']:
                dependencies.extend(data['build-system']['requires'])
            
            for dep in dependencies:
                self._parse_dependency_string(dep, 'pyproject.toml')
            
            self._discovery_sources.append('pyproject.toml')
        except Exception as e:
            logger.warning(f"Could not parse pyproject.toml: {e}")
    
    def _discover_from_requirements_txt(self) -> None:
        """Discover dependencies from requirements.txt."""
        requirements_path = self.project_root / 'requirements.txt'
        if not requirements_path.exists():
            return
        
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self._parse_dependency_string(line, 'requirements.txt')
            
            self._discovery_sources.append('requirements.txt')
        except Exception as e:
            logger.warning(f"Could not parse requirements.txt: {e}")
    
    def _discover_from_setup_py(self) -> None:
        """Discover dependencies from setup.py."""
        setup_path = self.project_root / 'setup.py'
        if not setup_path.exists():
            return
        
        try:
            with open(setup_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            install_requires_match = re.search(
                r'install_requires\s*=\s*\[(.*?)\]', 
                content, 
                re.DOTALL
            )
            if install_requires_match:
                deps_str = install_requires_match.group(1)
                deps = re.findall(r'["\']([^"\']+)["\']', deps_str)
                for dep in deps:
                    self._parse_dependency_string(dep, 'setup.py')
            
            self._discovery_sources.append('setup.py')
        except Exception as e:
            logger.warning(f"Could not parse setup.py: {e}")
    
    def _discover_from_custom_config(self) -> None:
        """Discover dependencies from custom configuration files."""
        config_files = [
            'dependency-mappings.json',
            'lazy-dependencies.json',
            'dependencies.json'
        ]
        
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, dict):
                        for import_name, package_name in data.items():
                            self.discovered_dependencies[import_name] = DependencyInfo(
                                import_name=import_name,
                                package_name=package_name,
                                source=config_file,
                                category='custom'
                            )
                    
                    self._discovery_sources.append(config_file)
                except Exception as e:
                    logger.warning(f"Could not parse {config_file}: {e}")
    
    def _parse_dependency_string(self, dep_str: str, source: str) -> None:
        """Parse a dependency string and extract dependency information."""
        dep_str = re.sub(r'[>=<!=~]+.*', '', dep_str)
        dep_str = re.sub(r'\[.*\]', '', dep_str)
        dep_str = dep_str.strip()
        
        if not dep_str:
            return
        
        import_name = dep_str
        package_name = dep_str
        
        if dep_str in self.COMMON_MAPPINGS:
            package_name = self.COMMON_MAPPINGS[dep_str]
        elif dep_str in self.COMMON_MAPPINGS.values():
            for imp_name, pkg_name in self.COMMON_MAPPINGS.items():
                if pkg_name == dep_str:
                    import_name = imp_name
                    break
        
        self.discovered_dependencies[import_name] = DependencyInfo(
            import_name=import_name,
            package_name=package_name,
            source=source,
            category='discovered'
        )
    
    def _add_common_mappings(self) -> None:
        """Add common mappings that might not be in dependency files."""
        for import_name, package_name in self.COMMON_MAPPINGS.items():
            if import_name not in self.discovered_dependencies:
                self.discovered_dependencies[import_name] = DependencyInfo(
                    import_name=import_name,
                    package_name=package_name,
                    source='common_mappings',
                    category='common'
                )
    
    def get_package_for_import(self, import_name: str) -> Optional[str]:
        """Get package name for a given import name."""
        mapping = self.discover_all_dependencies()
        return mapping.get(import_name)
    
    def get_imports_for_package(self, package_name: str) -> List[str]:
        """Get all possible import names for a package."""
        mapping = self.get_package_import_mapping()
        return mapping.get(package_name, [package_name])
    
    def get_package_import_mapping(self) -> Dict[str, List[str]]:
        """Get mapping of package names to their possible import names."""
        self.discover_all_dependencies()
        
        package_to_imports = {}
        for import_name, dep_info in self.discovered_dependencies.items():
            package_name = dep_info.package_name
            
            if package_name not in package_to_imports:
                package_to_imports[package_name] = [package_name]
            
            if import_name != package_name:
                if import_name not in package_to_imports[package_name]:
                    package_to_imports[package_name].append(import_name)
        
        return package_to_imports
    
    def get_import_package_mapping(self) -> Dict[str, str]:
        """Get mapping of import names to package names."""
        self.discover_all_dependencies()
        return {import_name: dep_info.package_name for import_name, dep_info in self.discovered_dependencies.items()}
    
    def export_to_json(self, file_path: str) -> None:
        """Export discovered dependencies to JSON file."""
        data = {
            'dependencies': {name: info.package_name for name, info in self.discovered_dependencies.items()},
            'sources': self.get_discovery_sources(),
            'total_count': len(self.discovered_dependencies)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# Global discovery instance
_discovery = None
_discovery_lock = threading.RLock()

def get_lazy_discovery(project_root: Optional[str] = None) -> LazyDiscovery:
    """Get the global lazy discovery instance."""
    global _discovery
    if _discovery is None:
        with _discovery_lock:
            if _discovery is None:
                _discovery = LazyDiscovery(project_root)
    return _discovery


def discover_dependencies(project_root: Optional[str] = None) -> Dict[str, str]:
    """Discover all dependencies for the current project."""
    discovery = get_lazy_discovery(project_root)
    return discovery.discover_all_dependencies()


def export_dependency_mappings(file_path: str, project_root: Optional[str] = None) -> None:
    """Export discovered dependency mappings to a JSON file."""
    discovery = get_lazy_discovery(project_root)
    discovery.export_to_json(file_path)


# =============================================================================
# SECTION 2: PACKAGE INSTALLATION (~550 lines)
# =============================================================================

def _is_externally_managed() -> bool:
    """Check if Python environment is externally managed (PEP 668)."""
    marker_file = Path(sys.prefix) / "EXTERNALLY-MANAGED"
    return marker_file.exists()


def _check_pip_audit_available() -> bool:
    """Check if pip-audit is available for vulnerability scanning."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return 'pip-audit' in result.stdout
    except Exception:
        return False


class LazyInstallPolicy:
    """
    Security and policy configuration for lazy installation.
    Per-package allow/deny lists, index URLs, and security settings.
    """
    __slots__ = ()
    
    _allow_lists: Dict[str, Set[str]] = {}
    _deny_lists: Dict[str, Set[str]] = {}
    _index_urls: Dict[str, str] = {}
    _extra_index_urls: Dict[str, List[str]] = {}
    _trusted_hosts: Dict[str, List[str]] = {}
    _require_hashes: Dict[str, bool] = {}
    _verify_ssl: Dict[str, bool] = {}
    _lockfile_paths: Dict[str, str] = {}
    _lock = threading.RLock()
    
    @classmethod
    def set_allow_list(cls, package_name: str, allowed_packages: List[str]) -> None:
        """Set allow list for a package (only these can be installed)."""
        with cls._lock:
            cls._allow_lists[package_name] = set(allowed_packages)
            logger.info(f"Set allow list for {package_name}: {len(allowed_packages)} packages")
    
    @classmethod
    def set_deny_list(cls, package_name: str, denied_packages: List[str]) -> None:
        """Set deny list for a package (these cannot be installed)."""
        with cls._lock:
            cls._deny_lists[package_name] = set(denied_packages)
            logger.info(f"Set deny list for {package_name}: {len(denied_packages)} packages")
    
    @classmethod
    def add_to_allow_list(cls, package_name: str, allowed_package: str) -> None:
        """Add single package to allow list."""
        with cls._lock:
            if package_name not in cls._allow_lists:
                cls._allow_lists[package_name] = set()
            cls._allow_lists[package_name].add(allowed_package)
    
    @classmethod
    def add_to_deny_list(cls, package_name: str, denied_package: str) -> None:
        """Add single package to deny list."""
        with cls._lock:
            if package_name not in cls._deny_lists:
                cls._deny_lists[package_name] = set()
            cls._deny_lists[package_name].add(denied_package)
    
    @classmethod
    def is_package_allowed(cls, installer_package: str, target_package: str) -> Tuple[bool, str]:
        """Check if target_package can be installed by installer_package."""
        with cls._lock:
            if installer_package in cls._deny_lists:
                if target_package in cls._deny_lists[installer_package]:
                    return False, f"Package '{target_package}' is in deny list"
            
            if installer_package in cls._allow_lists:
                if target_package not in cls._allow_lists[installer_package]:
                    return False, f"Package '{target_package}' not in allow list"
            
            return True, "OK"
    
    @classmethod
    def set_index_url(cls, package_name: str, index_url: str) -> None:
        """Set PyPI index URL for a package."""
        with cls._lock:
            cls._index_urls[package_name] = index_url
            logger.info(f"Set index URL for {package_name}: {index_url}")
    
    @classmethod
    def set_extra_index_urls(cls, package_name: str, urls: List[str]) -> None:
        """Set extra index URLs for a package."""
        with cls._lock:
            cls._extra_index_urls[package_name] = urls
            logger.info(f"Set {len(urls)} extra index URLs for {package_name}")
    
    @classmethod
    def add_trusted_host(cls, package_name: str, host: str) -> None:
        """Add trusted host for a package."""
        with cls._lock:
            if package_name not in cls._trusted_hosts:
                cls._trusted_hosts[package_name] = []
            cls._trusted_hosts[package_name].append(host)
    
    @classmethod
    def get_pip_args(cls, package_name: str) -> List[str]:
        """Get pip install arguments for a package based on policy."""
        args = []
        
        with cls._lock:
            if package_name in cls._index_urls:
                args.extend(['--index-url', cls._index_urls[package_name]])
            
            if package_name in cls._extra_index_urls:
                for url in cls._extra_index_urls[package_name]:
                    args.extend(['--extra-index-url', url])
            
            if package_name in cls._trusted_hosts:
                for host in cls._trusted_hosts[package_name]:
                    args.extend(['--trusted-host', host])
            
            if cls._require_hashes.get(package_name, False):
                args.append('--require-hashes')
            
            if not cls._verify_ssl.get(package_name, True):
                args.append('--no-verify-ssl')
        
        return args
    
    @classmethod
    def set_lockfile_path(cls, package_name: str, path: str) -> None:
        """Set lockfile path for a package."""
        with cls._lock:
            cls._lockfile_paths[package_name] = path
    
    @classmethod
    def get_lockfile_path(cls, package_name: str) -> Optional[str]:
        """Get lockfile path for a package."""
        with cls._lock:
            return cls._lockfile_paths.get(package_name)


class LazyInstaller(APackageInstaller):
    """
    Lazy installer that automatically installs missing packages on import failure.
    Each instance is isolated per package to prevent interference.
    """
    
    __slots__ = APackageInstaller.__slots__ + ('_dependency_mapper', '_auto_approve_all')
    
    def __init__(self, package_name: str = 'default'):
        """Initialize lazy installer for a specific package."""
        super().__init__(package_name)
        self._dependency_mapper = DependencyMapper()
        self._auto_approve_all = False
    
    def _ask_user_permission(self, package_name: str, module_name: str) -> bool:
        """Ask user for permission to install a package."""
        if self._auto_approve_all:
            return True
        
        print(f"\n{'='*60}")
        print(f"Lazy Installation Active - {self._package_name}")
        print(f"{'='*60}")
        print(f"Package: {package_name}")
        print(f"Module:  {module_name}")
        print(f"{'='*60}")
        print(f"\nThe module '{module_name}' is not installed.")
        print(f"Would you like to install '{package_name}'?")
        print(f"\nOptions:")
        print(f"  [Y] Yes - Install this package")
        print(f"  [N] No  - Skip this package")
        print(f"  [A] All - Install this and all future packages without asking")
        print(f"  [Q] Quit - Cancel and raise ImportError")
        print(f"{'='*60}")
        
        while True:
            try:
                choice = input("Your choice [Y/N/A/Q]: ").strip().upper()
                
                if choice in ('Y', 'YES', ''):
                    return True
                elif choice in ('N', 'NO'):
                    return False
                elif choice in ('A', 'ALL'):
                    self._auto_approve_all = True
                    return True
                elif choice in ('Q', 'QUIT'):
                    raise KeyboardInterrupt("User cancelled installation")
                else:
                    print(f"Invalid choice '{choice}'. Please enter Y, N, A, or Q.")
            except (EOFError, KeyboardInterrupt):
                print("\n❌ Installation cancelled by user")
                return False
    
    def install_package(self, package_name: str, module_name: str = None) -> bool:
        """Install a package using pip."""
        with self._lock:
            if package_name in self._installed_packages:
                return True
            
            if package_name in self._failed_packages:
                return False
            
            if self._mode == LazyInstallMode.DISABLED:
                logger.info(f"Lazy installation disabled for {self._package_name}, skipping {package_name}")
                return False
            
            if self._mode == LazyInstallMode.WARN:
                logger.warning(f"[WARN] Package '{package_name}' is missing but WARN mode is active - not installing")
                print(f"[WARN] ({self._package_name}): Package '{package_name}' is missing (not installed in WARN mode)")
                return False
            
            if self._mode == LazyInstallMode.DRY_RUN:
                print(f"[DRY RUN] ({self._package_name}): Would install package '{package_name}'")
                return False
            
            if self._mode == LazyInstallMode.INTERACTIVE:
                if not self._ask_user_permission(package_name, module_name or package_name):
                    logger.info(f"User declined installation of {package_name}")
                    self._failed_packages.add(package_name)
                    return False
            
            # Security checks
            if _is_externally_managed():
                logger.error(f"Cannot install {package_name}: Environment is externally managed (PEP 668)")
                print(f"\n[ERROR] This Python environment is externally managed (PEP 668)")
                print(f"Package '{package_name}' cannot be installed in this environment.")
                print(f"\nSuggested solutions:")
                print(f"  1. Create a virtual environment:")
                print(f"     python -m venv .venv")
                print(f"     .venv\\Scripts\\activate  # Windows")
                print(f"     source .venv/bin/activate  # Linux/macOS")
                print(f"  2. Use pipx for isolated installs:")
                print(f"     pipx install {package_name}")
                print(f"  3. Override with --break-system-packages (NOT RECOMMENDED)\n")
                self._failed_packages.add(package_name)
                return False
            
            allowed, reason = LazyInstallPolicy.is_package_allowed(self._package_name, package_name)
            if not allowed:
                logger.error(f"Cannot install {package_name}: {reason}")
                print(f"\n[SECURITY] Package '{package_name}' blocked: {reason}\n")
                self._failed_packages.add(package_name)
                return False
            
            # Proceed with installation
            try:
                logger.info(f"Installing package: {package_name}")
                print(f"\n[INSTALL] Installing {package_name}...")
                
                pip_args = [sys.executable, '-m', 'pip', 'install']
                policy_args = LazyInstallPolicy.get_pip_args(self._package_name)
                if policy_args:
                    pip_args.extend(policy_args)
                    logger.debug(f"Using policy args: {policy_args}")
                
                pip_args.append(package_name)
                
                result = subprocess.run(
                    pip_args,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                self._installed_packages.add(package_name)
                print(f"[OK] Successfully installed: {package_name}\n")
                logger.info(f"Successfully installed: {package_name}")
                
                if _check_pip_audit_available():
                    self._run_vulnerability_audit(package_name)
                
                self._update_lockfile(package_name)
                
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {package_name}: {e.stderr}")
                print(f"[FAIL] Failed to install {package_name}\n")
                self._failed_packages.add(package_name)
                return False
            except Exception as e:
                logger.error(f"Unexpected error installing {package_name}: {e}")
                print(f"[ERROR] Unexpected error: {e}\n")
                self._failed_packages.add(package_name)
                return False
    
    def _run_vulnerability_audit(self, package_name: str) -> None:
        """Run vulnerability audit on installed package using pip-audit."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip_audit', '-r', '-', '--format', 'json'],
                input=package_name,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Vulnerability audit passed for {package_name}")
            else:
                try:
                    audit_data = json.loads(result.stdout)
                    if audit_data.get('vulnerabilities'):
                        logger.warning(f"[SECURITY] Vulnerabilities found in {package_name}: {audit_data}")
                        print(f"[SECURITY WARNING] Package '{package_name}' has known vulnerabilities")
                        print(f"Run 'pip-audit' for details")
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse audit results for {package_name}")
        except subprocess.TimeoutExpired:
            logger.warning(f"Vulnerability audit timed out for {package_name}")
        except Exception as e:
            logger.debug(f"Vulnerability audit skipped for {package_name}: {e}")
    
    def _update_lockfile(self, package_name: str) -> None:
        """Update lockfile with newly installed package."""
        lockfile_path = LazyInstallPolicy.get_lockfile_path(self._package_name)
        if not lockfile_path:
            return
        
        try:
            version = self._get_installed_version(package_name)
            if not version:
                return
            
            lockfile_path = Path(lockfile_path)
            if lockfile_path.exists():
                with open(lockfile_path, 'r', encoding='utf-8') as f:
                    lockdata = json.load(f)
            else:
                lockdata = {
                    "metadata": {
                        "generated_by": f"xwsystem-lazy-{self._package_name}",
                        "version": "1.0"
                    },
                    "packages": {}
                }
            
            lockdata["packages"][package_name] = {
                "version": version,
                "installed_at": datetime.now().isoformat(),
                "installer": self._package_name
            }
            
            lockfile_path.parent.mkdir(parents=True, exist_ok=True)
            with open(lockfile_path, 'w', encoding='utf-8') as f:
                json.dump(lockdata, f, indent=2)
            
            logger.info(f"Updated lockfile: {lockfile_path}")
        except Exception as e:
            logger.warning(f"Failed to update lockfile: {e}")
    
    def _get_installed_version(self, package_name: str) -> Optional[str]:
        """Get installed version of a package."""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        return line.split(':', 1)[1].strip()
        except Exception as e:
            logger.debug(f"Could not get version for {package_name}: {e}")
        return None
    
    def generate_sbom(self) -> Dict:
        """Generate Software Bill of Materials (SBOM) for installed packages."""
        sbom = {
            "metadata": {
                "format": "xwsystem-sbom",
                "version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "installer_package": self._package_name
            },
            "packages": []
        }
        
        for pkg in self._installed_packages:
            version = self._get_installed_version(pkg)
            sbom["packages"].append({
                "name": pkg,
                "version": version or "unknown",
                "installed_by": self._package_name,
                "source": "pypi"
            })
        
        return sbom
    
    def export_sbom(self, output_path: str) -> bool:
        """Export SBOM to file."""
        try:
            sbom = self.generate_sbom()
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sbom, f, indent=2)
            
            logger.info(f"Exported SBOM to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export SBOM: {e}")
            return False
    
    def is_package_installed(self, package_name: str) -> bool:
        """Check if a package is already installed."""
        return package_name in self._installed_packages
    
    def install_and_import(self, module_name: str, package_name: str = None) -> Tuple[Optional[ModuleType], bool]:
        """Install package and import module."""
        if not self.is_enabled():
            return None, False
        
        if package_name is None:
            package_name = self._dependency_mapper.get_package_name(module_name)
            if package_name is None:
                logger.debug(f"Module '{module_name}' is a system/built-in module, not installing")
                return None, False
        
        try:
            module = importlib.import_module(module_name)
            return module, True
        except ImportError:
            pass
        
        if self.install_package(package_name, module_name):
            try:
                module = importlib.import_module(module_name)
                return module, True
            except ImportError as e:
                logger.error(f"Still cannot import {module_name} after installing {package_name}: {e}")
                return None, False
        
        return None, False
    
    def _check_security_policy(self, package_name: str) -> Tuple[bool, str]:
        """Check security policy for package."""
        return LazyInstallPolicy.is_package_allowed(self._package_name, package_name)
    
    def _run_pip_install(self, package_name: str, args: List[str]) -> bool:
        """Run pip install with arguments."""
        try:
            pip_args = [sys.executable, '-m', 'pip', 'install'] + args + [package_name]
            result = subprocess.run(
                pip_args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False


class LazyInstallerRegistry:
    """Registry to manage separate lazy installer instances per package."""
    _instances: Dict[str, LazyInstaller] = {}
    _lock = threading.RLock()
    
    @classmethod
    def get_instance(cls, package_name: str = 'default') -> LazyInstaller:
        """Get or create a lazy installer instance for a package."""
        with cls._lock:
            if package_name not in cls._instances:
                cls._instances[package_name] = LazyInstaller(package_name)
            return cls._instances[package_name]
    
    @classmethod
    def get_all_instances(cls) -> Dict[str, LazyInstaller]:
        """Get all lazy installer instances."""
        with cls._lock:
            return cls._instances.copy()


# =============================================================================
# SECTION 3: IMPORT HOOKS & TWO-STAGE LOADING (~450 lines)
# =============================================================================

# Global import tracking cache - Prevents infinite loops
_import_in_progress: Dict[Tuple[int, str], bool] = {}
_import_cache_lock = threading.RLock()
_importing = threading.local()

def _is_import_in_progress(module_name: str) -> bool:
    """Check if a module import is currently in progress for this thread."""
    thread_id = threading.get_ident()
    key = (thread_id, module_name)
    with _import_cache_lock:
        return key in _import_in_progress

def _mark_import_started(module_name: str) -> None:
    """Mark a module import as started for this thread."""
    thread_id = threading.get_ident()
    key = (thread_id, module_name)
    with _import_cache_lock:
        _import_in_progress[key] = True

def _mark_import_finished(module_name: str) -> None:
    """Mark a module import as finished for this thread."""
    thread_id = threading.get_ident()
    key = (thread_id, module_name)
    with _import_cache_lock:
        _import_in_progress.pop(key, None)


class LazyImportHook(AImportHook):
    """
    Import hook that intercepts ImportError and auto-installs packages.
    Performance optimized with zero overhead for successful imports.
    """
    
    __slots__ = AImportHook.__slots__
    
    def handle_import_error(self, module_name: str) -> Optional[Any]:
        """Handle ImportError by attempting to install and re-import."""
        if not self._enabled:
            return None
        
        try:
            module, success = lazy_import_with_install(
                module_name, 
                installer_package=self._package_name
            )
            return module if success else None
        except:
            return None
    
    def install_hook(self) -> None:
        """Install the import hook into sys.meta_path."""
        install_import_hook(self._package_name)
    
    def uninstall_hook(self) -> None:
        """Uninstall the import hook from sys.meta_path."""
        uninstall_import_hook(self._package_name)
    
    def is_installed(self) -> bool:
        """Check if hook is installed."""
        return is_import_hook_installed(self._package_name)


class LazyMetaPathFinder:
    """
    Custom meta path finder that intercepts failed imports.
    Performance optimized - only triggers when import would fail anyway.
    """
    
    __slots__ = ('_package_name', '_enabled')
    
    def __init__(self, package_name: str = 'default'):
        """Initialize meta path finder."""
        self._package_name = package_name
        self._enabled = True
    
    def find_module(self, fullname: str, path: Optional[str] = None):
        """Find module - returns None to let standard import continue."""
        return None
    
    def find_spec(self, fullname: str, path: Optional[str] = None, target=None):
        """Find module spec - intercepts imports to enable two-stage lazy loading."""
        if not self._enabled:
            return None
        
        if _is_import_in_progress(fullname):
            logger.debug(f"[RECURSION GUARD] Import '{fullname}' already in progress, skipping hook")
            return None
        
        # Two-stage lazy loading for serialization modules
        if fullname.startswith('exonware.xwsystem.serialization.'):
            module_suffix = fullname[len('exonware.xwsystem.serialization.'):]
            
            if module_suffix and '.' not in module_suffix:
                logger.info(f"[HOOK] Candidate for wrapping: {fullname}")
                
                _mark_import_started(fullname)
                try:
                    if getattr(_importing, 'active', False):
                        logger.debug(f"[HOOK] Recursion guard active, skipping {fullname}")
                        return None
                    
                    try:
                        logger.debug(f"[HOOK] Looking for spec: {fullname}")
                        spec = importlib.util.find_spec(fullname)
                        if spec is not None:
                            logger.debug(f"[HOOK] Spec found, trying normal import: {fullname}")
                            _importing.active = True
                            try:
                                __import__(fullname)
                                logger.info(f"✓ [HOOK] Module {fullname} imported successfully, no wrapping needed")
                                return None
                            finally:
                                _importing.active = False
                    except ImportError as e:
                        logger.info(f"⚠ [HOOK] Module {fullname} has missing dependencies, wrapping: {e}")
                        wrapped_spec = self._wrap_serialization_module(fullname)
                        if wrapped_spec is not None:
                            logger.info(f"✓ [HOOK] Successfully wrapped: {fullname}")
                            return wrapped_spec
                        logger.warning(f"✗ [HOOK] Failed to wrap: {fullname}")
                    except (ModuleNotFoundError,) as e:
                        logger.debug(f"[HOOK] Module {fullname} not found, skipping wrap: {e}")
                        pass
                    except Exception as e:
                        logger.warning(f"[HOOK] Error checking module {fullname}: {e}")
                finally:
                    _mark_import_finished(fullname)
            
            return None
        
        # Only handle top-level packages
        if '.' in fullname:
            return None
        
        _mark_import_started(fullname)
        try:
            try:
                if not is_lazy_install_enabled(self._package_name):
                    return None
                
                module, success = lazy_import_with_install(
                    fullname,
                    installer_package=self._package_name
                )
                
                if success and module:
                    return importlib.util.find_spec(fullname)
                
            except Exception as e:
                logger.debug(f"Lazy import hook failed for {fullname}: {e}")
            
            return None
        finally:
            _mark_import_finished(fullname)
    
    def _wrap_serialization_module(self, fullname: str):
        """Wrap serialization module loading to defer missing dependencies."""
        logger.info(f"[STAGE 1] Starting wrap of module: {fullname}")
        
        try:
            logger.debug(f"[STAGE 1] Getting spec for: {fullname}")
            spec = importlib.util.find_spec(fullname)
            if not spec or not spec.loader:
                logger.warning(f"[STAGE 1] No spec or loader for: {fullname}")
                return None
            
            logger.debug(f"[STAGE 1] Creating module from spec: {fullname}")
            module = importlib.util.module_from_spec(spec)
            
            deferred_imports = {}
            
            logger.debug(f"[STAGE 1] Setting up import wrapper for: {fullname}")
            original_import = builtins.__import__
            
            def capture_import_errors(name, *args, **kwargs):
                """Intercept imports and defer ONLY external missing packages."""
                logger.debug(f"[STAGE 1] capture_import_errors: Trying to import '{name}' in {fullname}")
                
                if _is_import_in_progress(name):
                    logger.debug(f"[STAGE 1] Import '{name}' already in progress, using original_import")
                    return original_import(name, *args, **kwargs)
                
                _mark_import_started(name)
                try:
                    result = original_import(name, *args, **kwargs)
                    logger.debug(f"[STAGE 1] ✓ Successfully imported '{name}'")
                    return result
                except ImportError as e:
                    logger.debug(f"[STAGE 1] ✗ Import failed for '{name}': {e}")
                    
                    if name.startswith('exonware.') or name.startswith('xwsystem.'):
                        logger.info(f"[STAGE 1] Letting internal import '{name}' fail normally (internal package)")
                        raise
                    
                    if '.' in name:
                        logger.info(f"[STAGE 1] Letting submodule '{name}' fail normally (has dots)")
                        raise
                    
                    logger.info(f"⏳ [STAGE 1] DEFERRING missing external package '{name}' in {fullname}")
                    deferred = DeferredImportError(name, e, self._package_name)
                    deferred_imports[name] = deferred
                    return deferred
                finally:
                    _mark_import_finished(name)
            
            logger.debug(f"[STAGE 1] Executing module with import wrapper: {fullname}")
            builtins.__import__ = capture_import_errors
            try:
                spec.loader.exec_module(module)
                logger.debug(f"[STAGE 1] Module execution completed: {fullname}")
                
                if deferred_imports:
                    logger.info(f"✓ [STAGE 1] Module {fullname} loaded with {len(deferred_imports)} deferred imports: {list(deferred_imports.keys())}")
                    self._wrap_module_classes(module, deferred_imports)
                else:
                    logger.info(f"✓ [STAGE 1] Module {fullname} loaded with NO deferred imports (all dependencies available)")
                
            finally:
                logger.debug(f"[STAGE 1] Restoring original __import__")
                builtins.__import__ = original_import
            
            logger.debug(f"[STAGE 1] Registering module in sys.modules: {fullname}")
            sys.modules[fullname] = module
            logger.info(f"✓ [STAGE 1] Successfully wrapped and registered: {fullname}")
            return spec
            
        except Exception as e:
            logger.debug(f"Could not wrap {fullname}: {e}")
            return None
    
    def _wrap_module_classes(self, module, deferred_imports: Dict):
        """Wrap classes in a module that depend on deferred imports."""
        logger.debug(f"[STAGE 1] Wrapping classes in {module.__name__} (deferred: {list(deferred_imports.keys())})")
        wrapped_count = 0
        
        for name, obj in list(module.__dict__.items()):
            if isinstance(obj, type):
                for dep_name in deferred_imports.keys():
                    module_file = getattr(module, '__file__', '')
                    if dep_name.lower() in name.lower() or dep_name.lower() in module_file.lower():
                        logger.debug(f"[STAGE 1] Class '{name}' depends on '{dep_name}', wrapping...")
                        wrapped = self._create_lazy_class_wrapper(obj, deferred_imports[dep_name])
                        module.__dict__[name] = wrapped
                        wrapped_count += 1
                        logger.info(f"✓ [STAGE 1] Wrapped class '{name}' in {module.__name__}")
                        break
        
        logger.info(f"[STAGE 1] Wrapped {wrapped_count} classes in {module.__name__}")
    
    def _create_lazy_class_wrapper(self, original_class, deferred_import: DeferredImportError):
        """Create a wrapper class that installs dependencies when instantiated."""
        class LazyClassWrapper:
            """Lazy wrapper that installs dependencies on first instantiation."""
            
            def __init__(self, *args, **kwargs):
                """Install dependency and create real instance."""
                deferred_import._try_install_and_import()
                
                real_module = importlib.reload(sys.modules[original_class.__module__])
                real_class = getattr(real_module, original_class.__name__)
                
                real_instance = real_class(*args, **kwargs)
                self.__class__ = real_class
                self.__dict__ = real_instance.__dict__
            
            def __repr__(self):
                return f"<Lazy{original_class.__name__}: will install dependencies on init>"
        
        LazyClassWrapper.__name__ = f"Lazy{original_class.__name__}"
        LazyClassWrapper.__qualname__ = f"Lazy{original_class.__qualname__}"
        LazyClassWrapper.__module__ = original_class.__module__
        LazyClassWrapper.__doc__ = original_class.__doc__
        
        return LazyClassWrapper


# Registry of installed hooks per package
_installed_hooks: Dict[str, LazyMetaPathFinder] = {}
_hook_lock = threading.RLock()


def install_import_hook(package_name: str = 'default') -> None:
    """Install performant import hook for automatic lazy installation."""
    global _installed_hooks
    
    logger.info(f"[HOOK INSTALL] Installing import hook for package: {package_name}")
    
    with _hook_lock:
        if package_name in _installed_hooks:
            logger.info(f"[HOOK INSTALL] Import hook already installed for {package_name}")
            return
        
        logger.debug(f"[HOOK INSTALL] Creating LazyMetaPathFinder for {package_name}")
        hook = LazyMetaPathFinder(package_name)
        
        logger.debug(f"[HOOK INSTALL] Current sys.meta_path has {len(sys.meta_path)} entries")
        sys.meta_path.insert(0, hook)
        _installed_hooks[package_name] = hook
        
        logger.info(f"✅ [HOOK INSTALL] Lazy import hook installed for {package_name} (now {len(sys.meta_path)} meta_path entries)")


def uninstall_import_hook(package_name: str = 'default') -> None:
    """Uninstall import hook for a package."""
    global _installed_hooks
    
    with _hook_lock:
        if package_name in _installed_hooks:
            hook = _installed_hooks[package_name]
            try:
                sys.meta_path.remove(hook)
            except ValueError:
                pass
            del _installed_hooks[package_name]
            logger.info(f"Lazy import hook uninstalled for {package_name}")


def is_import_hook_installed(package_name: str = 'default') -> bool:
    """Check if import hook is installed for a package."""
    return package_name in _installed_hooks


# =============================================================================
# SECTION 4: LAZY LOADING & CACHING (~300 lines)
# =============================================================================

class LazyLoader(ALazyLoader):
    """
    Thread-safe lazy loader for modules with caching.
    Implements Proxy pattern for deferred module loading.
    """
    
    def load_module(self, module_path: str = None) -> ModuleType:
        """Thread-safe module loading with caching."""
        if module_path is None:
            module_path = self._module_path
        
        if self._cached_module is not None:
            return self._cached_module
        
        with self._lock:
            if self._cached_module is not None:
                return self._cached_module
            
            if self._loading:
                raise ImportError(f"Circular import detected for {module_path}")
            
            try:
                self._loading = True
                logger.debug(f"Lazy loading module: {module_path}")
                
                self._cached_module = importlib.import_module(module_path)
                
                logger.debug(f"Successfully loaded: {module_path}")
                return self._cached_module
                
            except Exception as e:
                logger.error(f"Failed to load module {module_path}: {e}")
                raise ImportError(f"Failed to load {module_path}: {e}") from e
            finally:
                self._loading = False
    
    def unload_module(self, module_path: str) -> None:
        """Unload a module from cache."""
        with self._lock:
            if module_path == self._module_path:
                self._cached_module = None
    
    def __getattr__(self, name: str) -> Any:
        """Get attribute from lazily loaded module."""
        module = self.load_module()
        try:
            return getattr(module, name)
        except AttributeError:
            raise AttributeError(
                f"module '{self._module_path}' has no attribute '{name}'"
            )
    
    def __dir__(self) -> list:
        """Return available attributes from loaded module."""
        module = self.load_module()
        return dir(module)


class LazyImporter:
    """
    Lazy importer that defers heavy module imports until first access.
    """
    
    __slots__ = ('_enabled', '_lazy_modules', '_loaded_modules', '_lock', '_access_counts')
    
    def __init__(self):
        """Initialize lazy importer."""
        self._enabled = False
        self._lazy_modules: Dict[str, str] = {}
        self._loaded_modules: Dict[str, ModuleType] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def enable(self) -> None:
        """Enable lazy imports."""
        with self._lock:
            self._enabled = True
            logger.info("Lazy imports enabled")
    
    def disable(self) -> None:
        """Disable lazy imports."""
        with self._lock:
            self._enabled = False
            logger.info("Lazy imports disabled")
    
    def is_enabled(self) -> bool:
        """Check if lazy imports are enabled."""
        return self._enabled
    
    def register_lazy_module(self, module_name: str, module_path: str = None) -> None:
        """Register a module for lazy loading."""
        with self._lock:
            if module_path is None:
                module_path = module_name
            
            self._lazy_modules[module_name] = module_path
            self._access_counts[module_name] = 0
            logger.debug(f"Registered lazy module: {module_name} -> {module_path}")
    
    def import_module(self, module_name: str, package_name: str = None) -> Any:
        """Import a module with lazy loading."""
        with self._lock:
            if not self._enabled:
                return importlib.import_module(module_name)
            
            if module_name in self._loaded_modules:
                self._access_counts[module_name] += 1
                return self._loaded_modules[module_name]
            
            if module_name in self._lazy_modules:
                module_path = self._lazy_modules[module_name]
                
                try:
                    actual_module = importlib.import_module(module_path)
                    self._loaded_modules[module_name] = actual_module
                    self._access_counts[module_name] += 1
                    
                    logger.debug(f"Lazy loaded module: {module_name}")
                    return actual_module
                    
                except ImportError as e:
                    logger.error(f"Failed to lazy load {module_name}: {e}")
                    raise
            else:
                return importlib.import_module(module_name)
    
    def preload_module(self, module_name: str) -> bool:
        """Preload a registered lazy module."""
        with self._lock:
            if module_name not in self._lazy_modules:
                logger.warning(f"Module {module_name} not registered for lazy loading")
                return False
            
            try:
                self.import_module(module_name)
                logger.info(f"Preloaded module: {module_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to preload {module_name}: {e}")
                return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lazy import statistics."""
        with self._lock:
            return {
                'enabled': self._enabled,
                'registered_modules': list(self._lazy_modules.keys()),
                'loaded_modules': list(self._loaded_modules.keys()),
                'access_counts': self._access_counts.copy(),
                'total_registered': len(self._lazy_modules),
                'total_loaded': len(self._loaded_modules)
            }


class LazyModuleRegistry:
    """
    Registry for managing lazy-loaded modules with performance tracking.
    """
    
    __slots__ = ('_modules', '_load_times', '_lock', '_access_counts')
    
    def __init__(self):
        """Initialize the registry."""
        self._modules: Dict[str, LazyLoader] = {}
        self._load_times: Dict[str, float] = {}
        self._access_counts: Dict[str, int] = {}
        self._lock = threading.RLock()
    
    def register_module(self, name: str, module_path: str) -> None:
        """Register a module for lazy loading."""
        with self._lock:
            if name in self._modules:
                logger.warning(f"Module '{name}' already registered, overwriting")
            
            self._modules[name] = LazyLoader(module_path)
            self._access_counts[name] = 0
            logger.debug(f"Registered lazy module: {name} -> {module_path}")
    
    def get_module(self, name: str) -> LazyLoader:
        """Get a lazy-loaded module."""
        with self._lock:
            if name not in self._modules:
                raise KeyError(f"Module '{name}' not registered")
            
            self._access_counts[name] += 1
            return self._modules[name]
    
    def preload_frequently_used(self, threshold: int = 5) -> None:
        """Preload modules that are accessed frequently."""
        with self._lock:
            for name, count in self._access_counts.items():
                if count >= threshold:
                    try:
                        _ = self._modules[name].load_module()
                        logger.info(f"Preloaded frequently used module: {name}")
                    except Exception as e:
                        logger.warning(f"Failed to preload {name}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        with self._lock:
            loaded_count = sum(
                1 for loader in self._modules.values() 
                if loader.is_loaded()
            )
            
            return {
                'total_registered': len(self._modules),
                'loaded_count': loaded_count,
                'unloaded_count': len(self._modules) - loaded_count,
                'access_counts': self._access_counts.copy(),
                'load_times': self._load_times.copy(),
            }
    
    def clear_cache(self) -> None:
        """Clear all cached modules."""
        with self._lock:
            for name, loader in self._modules.items():
                loader.unload_module(loader._module_path)
            logger.info("Cleared all cached modules")


class LazyPerformanceMonitor:
    """Performance monitor for lazy loading operations."""
    
    __slots__ = ('_load_times', '_access_counts', '_memory_usage')
    
    def __init__(self):
        """Initialize performance monitor."""
        self._load_times = {}
        self._access_counts = {}
        self._memory_usage = {}
    
    def record_load_time(self, module: str, load_time: float) -> None:
        """Record module load time."""
        self._load_times[module] = load_time
    
    def record_access(self, module: str) -> None:
        """Record module access."""
        self._access_counts[module] = self._access_counts.get(module, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            'load_times': self._load_times.copy(),
            'access_counts': self._access_counts.copy(),
            'memory_usage': self._memory_usage.copy()
        }


# Global instances
_lazy_importer = LazyImporter()
_global_registry = LazyModuleRegistry()


def enable_lazy_imports() -> None:
    """Enable lazy imports."""
    _lazy_importer.enable()


def disable_lazy_imports() -> None:
    """Disable lazy imports."""
    _lazy_importer.disable()


def is_lazy_import_enabled() -> bool:
    """Check if lazy imports are enabled."""
    return _lazy_importer.is_enabled()


def lazy_import(module_name: str, package_name: str = None) -> Any:
    """Import a module with lazy loading."""
    return _lazy_importer.import_module(module_name, package_name)


def register_lazy_module(module_name: str, module_path: str = None) -> None:
    """Register a module for lazy loading."""
    _lazy_importer.register_lazy_module(module_name, module_path)
    _global_registry.register_module(module_name, module_path or module_name)


def preload_module(module_name: str) -> bool:
    """Preload a registered lazy module."""
    return _lazy_importer.preload_module(module_name)


def get_lazy_module(name: str) -> LazyLoader:
    """Get a lazy-loaded module from the global registry."""
    return _global_registry.get_module(name)


def get_loading_stats() -> Dict[str, Any]:
    """Get loading statistics from the global registry."""
    return _global_registry.get_stats()


def preload_frequently_used(threshold: int = 5) -> None:
    """Preload frequently used modules from the global registry."""
    _global_registry.preload_frequently_used(threshold)


def get_lazy_import_stats() -> Dict[str, Any]:
    """Get lazy import statistics."""
    return _lazy_importer.get_stats()


# =============================================================================
# SECTION 5: CONFIGURATION & REGISTRY (~200 lines)
# =============================================================================

# Performance optimization: Cache detection results per package
_lazy_detection_cache: Dict[str, bool] = {}
_lazy_detection_lock = threading.RLock()

# Performance optimization: Module-level constant for mode enum conversion
_MODE_ENUM_MAP = {
    "auto": LazyInstallMode.AUTO,
    "interactive": LazyInstallMode.INTERACTIVE,
    "warn": LazyInstallMode.WARN,
    "disabled": LazyInstallMode.DISABLED,
    "dry_run": LazyInstallMode.DRY_RUN,
}


def _detect_lazy_installation(package_name: str) -> bool:
    """
    Detect if the package was installed with [lazy] extra.
    Optimized with per-package caching to avoid repeated detection.
    """
    with _lazy_detection_lock:
        if package_name in _lazy_detection_cache:
            return _lazy_detection_cache[package_name]
    
    # Method 1: Check via pkg_resources
    try:
        import pkg_resources
        
        package_names_to_try = [
            f"exonware-{package_name}",
            package_name,
            f"exonware.{package_name}"
        ]
        
        for pkg_name in package_names_to_try:
            try:
                dist = pkg_resources.get_distribution(pkg_name)
                if hasattr(dist, 'extras'):
                    if 'lazy' in dist.extras:
                        logger.info(f"✅ Detected [lazy] extra for {package_name}")
                        with _lazy_detection_lock:
                            _lazy_detection_cache[package_name] = True
                        return True
                        
            except pkg_resources.DistributionNotFound:
                continue
                
    except ImportError:
        logger.debug("pkg_resources not available, trying alternative methods")
    
    # Method 2: Check via importlib.metadata (Python 3.8+)
    try:
        if sys.version_info >= (3, 8):
            from importlib import metadata
            
            package_names_to_try = [
                f"exonware-{package_name}",
                package_name,
            ]
            
            for pkg_name in package_names_to_try:
                try:
                    dist = metadata.distribution(pkg_name)
                    if dist.requires:
                        for req in dist.requires:
                            if 'extra == "lazy"' in req or 'extra == \'lazy\'' in req:
                                dep_name = req.split(';')[0].strip().split('[')[0].strip()
                                try:
                                    metadata.distribution(dep_name)
                                    logger.info(f"✅ Detected [lazy] dependencies for {package_name}")
                                    with _lazy_detection_lock:
                                        _lazy_detection_cache[package_name] = True
                                    return True
                                except:
                                    pass
                except Exception:
                    continue
    except Exception as e:
        logger.debug(f"importlib.metadata check failed: {e}")
    
    # Method 3: Check environment variable
    env_var = f"{package_name.upper()}_LAZY_INSTALL"
    env_value = os.environ.get(env_var, '').lower()
    if env_value in ('true', '1', 'yes', 'on'):
        logger.info(f"✅ Detected lazy via environment variable {env_var}")
        with _lazy_detection_lock:
            _lazy_detection_cache[package_name] = True
        return True
    
    # Default: lazy installation is NOT enabled
    result = False
    logger.info(f"❌ No [lazy] extra detected for {package_name}")
    
    with _lazy_detection_lock:
        _lazy_detection_cache[package_name] = result
    
    return result


class LazyInstallConfig:
    """Global configuration for lazy installation per package."""
    _configs: Dict[str, bool] = {}
    _modes: Dict[str, str] = {}
    _initialized: Dict[str, bool] = {}
    
    @classmethod
    def set(cls, package_name: str, enabled: bool, mode: str = "auto", install_hook: bool = True) -> None:
        """Enable or disable lazy installation for a specific package."""
        package_key = package_name.lower()
        
        cls._configs[package_key] = enabled
        cls._modes[package_key] = mode
        
        if enabled and not cls._initialized.get(package_key):
            cls._initialize_package(package_key, enabled, mode, install_hook=install_hook)
    
    @classmethod
    def _initialize_package(cls, package_key: str, enabled: bool, mode: str, install_hook: bool = True) -> None:
        """Initialize lazy installation for a specific package."""
        if enabled:
            try:
                enable_lazy_install(package_key)
                
                mode_enum = _MODE_ENUM_MAP.get(mode.lower(), LazyInstallMode.AUTO)
                set_lazy_install_mode(package_key, mode_enum)
                
                if install_hook:
                    install_import_hook(package_key)
                    logger.info(f"✅ Lazy installation initialized for {package_key} (mode: {mode}, hook: installed)")
                else:
                    logger.info(f"✅ Lazy installation initialized for {package_key} (mode: {mode}, hook: deferred)")
                
                cls._initialized[package_key] = True
            except ImportError as e:
                logger.warning(f"⚠️ Could not enable lazy install for {package_key}: {e}")
        else:
            try:
                disable_lazy_install(package_key)
                cls._initialized[package_key] = True
                logger.info(f"❌ Lazy installation disabled for {package_key}")
            except ImportError:
                pass
    
    @classmethod
    def is_enabled(cls, package_name: str) -> bool:
        """Check if lazy installation is enabled for a package."""
        return cls._configs.get(package_name.lower(), False)
    
    @classmethod
    def get_mode(cls, package_name: str) -> str:
        """Get the lazy installation mode for a package."""
        return cls._modes.get(package_name.lower(), "auto")


def config_package_lazy_install_enabled(
    package_name: str, 
    enabled: bool = None,
    mode: str = "auto",
    install_hook: bool = True
) -> None:
    """
    Simple one-line configuration for package lazy installation.
    
    Args:
        package_name: Package name (e.g., "xwsystem", "xwnode", "xwdata")
        enabled: True to enable, False to disable, None to auto-detect from pip installation
        mode: Installation mode - "auto", "interactive", "disabled", "dry_run"
        install_hook: Whether to install the import hook (default: True)
    
    Examples:
        # Auto-detect from installation
        config_package_lazy_install_enabled("xwsystem")
        
        # Force enable
        config_package_lazy_install_enabled("xwnode", True, "interactive")
        
        # Force disable
        config_package_lazy_install_enabled("xwdata", False)
    """
    if enabled is None:
        enabled = _detect_lazy_installation(package_name)
    
    LazyInstallConfig.set(package_name, enabled, mode, install_hook=install_hook)


# =============================================================================
# SECTION 6: FACADE - UNIFIED API (~150 lines)
# =============================================================================

class LazyModeFacade:
    """
    Main facade for lazy mode operations in xwsystem.
    Provides a unified interface for lazy loading functionality.
    """
    
    __slots__ = ('_enabled', '_strategy', '_config', '_performance_monitor')
    
    def __init__(self):
        """Initialize lazy mode facade."""
        self._enabled = False
        self._strategy = None
        self._config = {}
        self._performance_monitor = None
    
    def enable(self, strategy: str = "on_demand", **kwargs) -> None:
        """Enable lazy mode with specified strategy."""
        self._enabled = True
        self._strategy = strategy
        self._config.update(kwargs)
        
        logger.info(f"Lazy mode enabled with strategy: {strategy}")
        
        if self._config.get('enable_monitoring', True):
            self._performance_monitor = LazyPerformanceMonitor()
    
    def disable(self) -> None:
        """Disable lazy mode and cleanup resources."""
        self._enabled = False
        self._strategy = None
        
        if self._config.get('clear_cache_on_disable', True):
            _global_registry.clear_cache()
        
        logger.info("Lazy mode disabled")
    
    def is_enabled(self) -> bool:
        """Check if lazy mode is currently enabled."""
        return self._enabled
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lazy mode performance statistics."""
        stats = _global_registry.get_stats()
        stats.update({
            'enabled': self._enabled,
            'strategy': self._strategy,
            'config': self._config.copy()
        })
        
        if self._performance_monitor:
            stats['performance'] = self._performance_monitor.get_stats()
        
        return stats
    
    def configure(self, **kwargs) -> None:
        """Configure lazy mode settings."""
        self._config.update(kwargs)
        logger.debug(f"Lazy mode configuration updated: {kwargs}")
    
    def preload(self, modules: List[str]) -> None:
        """Preload specified modules."""
        for module_name in modules:
            try:
                loader = _global_registry.get_module(module_name)
                _ = loader.load_module()
                logger.info(f"Preloaded module: {module_name}")
            except KeyError:
                logger.warning(f"Module not registered: {module_name}")
            except Exception as e:
                logger.error(f"Failed to preload {module_name}: {e}")
    
    def optimize(self) -> None:
        """Run optimization based on current usage patterns."""
        if not self._enabled:
            return
        
        threshold = self._config.get('preload_threshold', 5)
        _global_registry.preload_frequently_used(threshold)
        
        logger.info("Lazy mode optimization completed")


# Global lazy mode facade instance
_lazy_facade = LazyModeFacade()


def enable_lazy_mode(strategy: str = "on_demand", **kwargs) -> None:
    """Enable lazy mode with specified strategy."""
    _lazy_facade.enable(strategy, **kwargs)


def disable_lazy_mode() -> None:
    """Disable lazy mode and cleanup resources."""
    _lazy_facade.disable()


def is_lazy_mode_enabled() -> bool:
    """Check if lazy mode is currently enabled."""
    return _lazy_facade.is_enabled()


def get_lazy_mode_stats() -> Dict[str, Any]:
    """Get lazy mode performance statistics."""
    return _lazy_facade.get_stats()


def configure_lazy_mode(**kwargs) -> None:
    """Configure lazy mode settings."""
    _lazy_facade.configure(**kwargs)


def preload_modules(modules: List[str]) -> None:
    """Preload specified modules."""
    _lazy_facade.preload(modules)


def optimize_lazy_mode() -> None:
    """Run optimization based on current usage patterns."""
    _lazy_facade.optimize()


# =============================================================================
# SECTION 7: PUBLIC API - SIMPLE FUNCTIONS (~200 lines)
# =============================================================================

def enable_lazy_install(package_name: str = 'default') -> None:
    """Enable lazy installation for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    installer.enable()


def disable_lazy_install(package_name: str = 'default') -> None:
    """Disable lazy installation for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    installer.disable()


def is_lazy_install_enabled(package_name: str = 'default') -> bool:
    """Check if lazy installation is enabled for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    return installer.is_enabled()


def set_lazy_install_mode(package_name: str, mode: LazyInstallMode) -> None:
    """Set the lazy installation mode for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    installer.set_mode(mode)


def get_lazy_install_mode(package_name: str = 'default') -> LazyInstallMode:
    """Get the lazy installation mode for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    return installer.get_mode()


def install_missing_package(package_name: str, installer_package: str = 'default') -> bool:
    """Install a missing package."""
    installer = LazyInstallerRegistry.get_instance(installer_package)
    return installer.install_package(package_name)


def install_and_import(
    module_name: str, 
    package_name: str = None,
    installer_package: str = 'default'
) -> Tuple[Optional[ModuleType], bool]:
    """Install package and import module."""
    installer = LazyInstallerRegistry.get_instance(installer_package)
    return installer.install_and_import(module_name, package_name)


def get_lazy_install_stats(package_name: str = 'default') -> Dict[str, Any]:
    """Get lazy installation statistics for a specific package."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    return installer.get_stats()


def get_all_lazy_install_stats() -> Dict[str, Dict[str, Any]]:
    """Get lazy installation statistics for all packages."""
    all_instances = LazyInstallerRegistry.get_all_instances()
    return {name: inst.get_stats() for name, inst in all_instances.items()}


def lazy_import_with_install(
    module_name: str, 
    package_name: str = None,
    installer_package: str = 'default'
) -> Tuple[Optional[ModuleType], bool]:
    """
    Lazy import with automatic installation.
    
    This function attempts to import a module, and if it fails due to ImportError,
    it automatically installs the corresponding package using pip before retrying.
    """
    installer = LazyInstallerRegistry.get_instance(installer_package)
    return installer.install_and_import(module_name, package_name)


def xwimport(
    module_name: str, 
    package_name: str = None,
    installer_package: str = 'default'
) -> Any:
    """
    Simple lazy import with automatic installation.
    
    This function either returns the imported module or raises an ImportError.
    """
    module, available = lazy_import_with_install(module_name, package_name, installer_package)
    if not available:
        raise ImportError(f"Module {module_name} is not available and could not be installed")
    return module


# Security & Policy APIs
def set_package_allow_list(package_name: str, allowed_packages: List[str]) -> None:
    """Set allow list for a package (only these packages can be installed)."""
    LazyInstallPolicy.set_allow_list(package_name, allowed_packages)


def set_package_deny_list(package_name: str, denied_packages: List[str]) -> None:
    """Set deny list for a package (these packages cannot be installed)."""
    LazyInstallPolicy.set_deny_list(package_name, denied_packages)


def add_to_package_allow_list(package_name: str, allowed_package: str) -> None:
    """Add single package to allow list."""
    LazyInstallPolicy.add_to_allow_list(package_name, allowed_package)


def add_to_package_deny_list(package_name: str, denied_package: str) -> None:
    """Add single package to deny list."""
    LazyInstallPolicy.add_to_deny_list(package_name, denied_package)


def set_package_index_url(package_name: str, index_url: str) -> None:
    """Set PyPI index URL for a package."""
    LazyInstallPolicy.set_index_url(package_name, index_url)


def set_package_extra_index_urls(package_name: str, urls: List[str]) -> None:
    """Set extra index URLs for a package."""
    LazyInstallPolicy.set_extra_index_urls(package_name, urls)


def add_package_trusted_host(package_name: str, host: str) -> None:
    """Add trusted host for a package."""
    LazyInstallPolicy.add_trusted_host(package_name, host)


def set_package_lockfile(package_name: str, lockfile_path: str) -> None:
    """Set lockfile path for a package to track installed dependencies."""
    LazyInstallPolicy.set_lockfile_path(package_name, lockfile_path)


def generate_package_sbom(package_name: str = 'default', output_path: str = None) -> Dict:
    """Generate Software Bill of Materials (SBOM) for installed packages."""
    installer = LazyInstallerRegistry.get_instance(package_name)
    sbom = installer.generate_sbom()
    
    if output_path:
        installer.export_sbom(output_path)
    
    return sbom


def check_externally_managed_environment() -> bool:
    """Check if current Python environment is externally managed (PEP 668)."""
    return _is_externally_managed()


# =============================================================================
# EXPORT ALL
# =============================================================================

__all__ = [
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

