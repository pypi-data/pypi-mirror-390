# vnai/scope/device.py

"""
Device registration and management.

Handles one-time device registration on first install or version update.
Subsequent operations use cached device_id to avoid expensive system scans.
"""

import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeviceRegistry:
    """Manages device registration and reference data caching.
    
    Registers device once per version, storing reference data locally.
    Subsequent operations use cached device_id without full system scans.
    """
    
    _instance = None
    _lock = None
    
    def __new__(cls, project_dir: str | None = None):
        """Ensure singleton instance."""
        import threading
        if cls._lock is None:
            cls._lock = threading.Lock()
        
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DeviceRegistry, cls).__new__(cls)
                cls._instance._initialize(project_dir)
            return cls._instance
    
    def _initialize(self, project_dir: str | None = None) -> None:
        """Initialize device registry."""
        if project_dir is None:
            self.project_dir = Path.home() / ".vnstock"
        else:
            self.project_dir = Path(project_dir)
        
        self.id_dir = self.project_dir / 'id'
        self.registry_file = self.id_dir / 'device_registry.json'
        
        # Ensure directories exist
        self.id_dir.mkdir(exist_ok=True, parents=True)
        
        # Load existing registry if available
        self._registry = None
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self._registry = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load device registry: {e}")
                self._registry = None
    
    def is_registered(self, version: str) -> bool:
        """Check if device is registered for current version.
        
        Args:
            version: Current vnstock version (e.g., "3.2.0")
            
        Returns:
            bool: True if device registered for this version
        """
        if self._registry is None:
            return False
        
        try:
            installed_version = self._registry.get('version_installed')
            return installed_version == version
        except Exception:
            return False
    
    def register(
        self,
        device_info: dict,
        version: str
    ) -> dict:
        """Register device on first install or version update.
        
        Captures comprehensive device information including hardware,
        software packages, and environment details. Subsequent operations
        will use cached device_id instead of re-scanning the system.
        
        Args:
            device_info: System information dict from Inspector.examine()
            version: Current vnstock version
            
        Returns:
            dict: Registered device information
        """
        registry = {
            "device_id": device_info.get('machine_id'),
            "register_date": datetime.now().isoformat(),
            "version_installed": version,
            "os": device_info.get('os_name'),
            "os_platform": device_info.get('platform'),
            "python": device_info.get('python_version'),
            "arch": (
                device_info.get('platform', '').split('-')[-1]
                if device_info.get('platform') else 'unknown'
            ),
            "cpu_count": device_info.get('cpu_count'),
            "memory_gb": device_info.get('memory_gb'),
            "environment": device_info.get('environment'),
            "hosting_service": device_info.get('hosting_service'),
            # Store full reference data for later comparison
            "reference_data": {
                "commercial_usage": device_info.get(
                    'commercial_usage'
                ),
                "packages_snapshot": (
                    device_info.get('dependencies', {}).get(
                        'vnstock_family', []
                    )
                ),
                "git_info": device_info.get('git_info')
            }
        }
        
        # Write to file
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2)
            
            self._registry = registry
            logger.info(
                f"Device registered: {device_info.get('machine_id')} "
                f"(version {version})"
            )
        except Exception as e:
            logger.error(f"Failed to register device: {e}")
            raise
        
        return registry
    
    def get_device_id(self) -> str | None:
        """Get cached device_id.
        
        Returns:
            str or None: Device ID if registered, None otherwise
        """
        if self._registry is None:
            return None
        
        try:
            return self._registry.get('device_id')
        except Exception:
            return None
    
    def get_registry(self) -> dict | None:
        """Get full device registry.
        
        Returns:
            dict or None: Full registry if available
        """
        return self._registry
    
    def get_register_date(self) -> str | None:
        """Get device registration date.
        
        Returns:
            str or None: Registration date ISO string
        """
        if self._registry is None:
            return None
        
        try:
            return self._registry.get('register_date')
        except Exception:
            return None
    
    def needs_reregistration(self, current_version: str) -> bool:
        """Check if device needs re-registration for new version.
        
        Args:
            current_version: Current installed vnstock version
            
        Returns:
            bool: True if version has changed and re-registration needed
        """
        if self._registry is None:
            return True
        
        try:
            installed_version = self._registry.get('version_installed')
            return installed_version != current_version
        except Exception:
            return True
    
    def update_version(self, new_version: str) -> None:
        """Update version in registry without full re-scan.
        
        Used when vnstock version changes. The next full initialization
        will trigger a complete re-registration with system scan.
        
        Args:
            new_version: New vnstock version
        """
        if self._registry is not None:
            self._registry['version_installed'] = new_version
            self._registry['last_version_update'] = datetime.now().isoformat()
            
            try:
                with open(self.registry_file, 'w', encoding='utf-8') as f:
                    json.dump(self._registry, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to update version in registry: {e}")


# Create singleton instance
device_registry = DeviceRegistry()
