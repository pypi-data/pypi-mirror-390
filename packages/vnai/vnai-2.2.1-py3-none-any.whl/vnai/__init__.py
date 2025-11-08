# vnai/__init__.py
# Main entry point for vnai package

import os
import pathlib
import json
import time
import threading
import functools
from datetime import datetime

# Import core functionality
from vnai.beam.quota import guardian, optimize
from vnai.beam.metrics import collector, capture
from vnai.beam.pulse import monitor
from vnai.flow.relay import conduit
from vnai.flow.queue import buffer
from vnai.scope.profile import inspector
from vnai.scope.state import tracker, record
import vnai.scope.promo
from vnai.scope.promo import present

# Constants for terms and conditions
TC_VAR = "ACCEPT_TC"
TC_VAL = "tôi đồng ý"
TC_PATH = pathlib.Path.home() / ".vnstock" / "id" / "terms_agreement.txt"

TERMS_AND_CONDITIONS = """
Khi tiếp tục sử dụng Vnstock, bạn xác nhận rằng bạn đã đọc, hiểu và đồng ý với Chính sách quyền riêng tư và Điều khoản, điều kiện về giấy phép sử dụng Vnstock.

Chi tiết:
- Giấy phép sử dụng phần mềm: https://vnstocks.com/docs/tai-lieu/giay-phep-su-dung
- Chính sách quyền riêng tư: https://vnstocks.com/docs/tai-lieu/chinh-sach-quyen-rieng-tu
"""

class Core:
    """Core functionality for system optimization"""
    
    def __init__(self):
        """Initialize core"""
        self.initialized = False
        self.webhook_url = None
        self.init_time = datetime.now().isoformat()
        self.home_dir = pathlib.Path.home()
        self.project_dir = self.home_dir / ".vnstock"
        self.id_dir = self.project_dir / 'id'
        self.terms_file_path = TC_PATH
        self.system_info = None
        
        # Create necessary directories
        self.project_dir.mkdir(exist_ok=True)
        self.id_dir.mkdir(exist_ok=True)
        
        # Auto-initialize
        self.initialize()

    def initialize(self):
        """Initialize the system"""
        if self.initialized:
            return True
            
        # Check terms acceptance
        if not self._check_terms():
            self._accept_terms()
            
        # Set up vnstock environment
        from vnai.scope.profile import inspector
        inspector.setup_vnstock_environment()
        
        # === Phase 2: Device Registration (Optimization) ===
        try:
            from vnai.scope.device import device_registry
            # Get vnstock version for re-registration detection
            vnstock_version = getattr(__import__('vnstock'),
                                      '__version__', '0.0.1')

            # Check if device needs registration
            if device_registry.needs_reregistration(vnstock_version):
                # Full system scan only on registration/version change
                system_info = inspector.examine()
                device_registry.register(system_info, vnstock_version)
                # Store for later use
                self.system_info = system_info
            else:
                # Use cached device_id (no system scan)
                self.system_info = device_registry.get_registry()
        except Exception as e:
            # Fallback: Do full system scan if device registry fails
            import logging
            logger = logging.getLogger(__name__)
            msg = f"Device registration failed: {e}. Using fallback."
            logger.warning(msg)
            self.system_info = inspector.examine()
        # === End Phase 2 ===
        
        # Display content during initialization
        from vnai.scope.promo import ContentManager
        manager = ContentManager()
        # Chỉ hiện ads nếu chắc chắn là free user
        is_paid = manager.is_paid_user is False
        if is_paid and getattr(manager, 'license_checked', False):
            present()
        
        # Record initialization
        record("initialization", {"timestamp": datetime.now().isoformat()})
        
        # Queue system data with optimal structure
        conduit.queue({
            "type": "system_info",
            "data": {
                "commercial": inspector.detect_commercial_usage(),
                "packages": inspector.scan_packages()
            }
        }, priority="high")
        
        self.initialized = True
        return True

    def _check_terms(self):
        """Check if terms have been accepted"""
        return os.path.exists(self.terms_file_path)

    def _accept_terms(self):
        """Record terms acceptance"""
        # Get system information
        system_info = inspector.examine()
        
        # Auto-accept terms
        if TC_VAR in os.environ and os.environ[TC_VAR] == TC_VAL:
            os.environ[TC_VAR] = TC_VAL
        else:
            # For non-interactive environments, accept by default
            os.environ[TC_VAR] = TC_VAL
        
        # Store the acceptance with hardware info
        now = datetime.now()
        machine_id = system_info['machine_id']
        user_msg = (
            f"Người dùng có mã nhận dạng {machine_id} "
            f"đã chấp nhận "
        )
        signed_agreement = (
            f"{user_msg}"
            f"điều khoản & điều kiện sử dụng Vnstock lúc {now}\n"
            f"---\n\n"
            f"THÔNG TIN THIẾT BỊ: {json.dumps(system_info, indent=2)}\n\n"
            f"Đính kèm bản sao nội dung bạn đã đọc, "
            f"hiểu rõ và đồng ý dưới đây:\n"
            f"{TERMS_AND_CONDITIONS}"
        )
        
        # Store the acceptance
        with open(self.terms_file_path, "w", encoding="utf-8") as f:
            f.write(signed_agreement)
        
        # Create the environment.json file that vnstock expects
        env_file = self.id_dir / "environment.json"
        env_data = {
            "accepted_agreement": True,
            "timestamp": now.isoformat(),
            "machine_id": machine_id
        }
        
        with open(env_file, "w") as f:
            json.dump(env_data, f)
        
        return True

    def status(self):
        """Get system status"""
        return {
            "initialized": self.initialized,
            "health": monitor.report(),
            "metrics": tracker.get_metrics()
            # Environment information available via self.system_info
        }
    
    def configure_privacy(self, level="standard"):
        """Configure privacy settings"""
        from vnai.scope.state import tracker
        return tracker.setup_privacy(level)


# Create singleton instance
core = Core()


# Backward support
def tc_init():
    return core.initialize()


def setup():
    """Setup vnai"""
    return core.initialize()


def optimize_execution(resource_type="default"):
    """Decorator for optimizing function execution"""
    return optimize(resource_type)


def agg_execution(resource_type="default"):
    """Decorator for aggregating function execution"""
    opts = optimize(resource_type, ad_cooldown=1500,
                    content_trigger_threshold=100000)
    return opts


def measure_performance(module_type="function"):
    """Decorator for measuring function performance"""
    return capture(module_type)


def accept_license_terms(terms_text=None):
    """Accept license terms and conditions"""
    if terms_text is None:
        terms_text = TERMS_AND_CONDITIONS

    # Get system information
    system_info = inspector.examine()

    # Record acceptance
    terms_file_path = (
        pathlib.Path.home() / ".vnstock" / "id" /
        "terms_agreement.txt"
    )
    os.makedirs(os.path.dirname(terms_file_path), exist_ok=True)
    
    with open(terms_file_path, "w", encoding="utf-8") as f:
        f.write(f"Terms accepted at {datetime.now().isoformat()}\n")
        f.write(f"System: {json.dumps(system_info)}\n\n")
        f.write(terms_text)
    
    return True


def accept_vnstock_terms():
    """Accept vnstock terms and create necessary files"""
    # Get system information
    from vnai.scope.profile import inspector
    system_info = inspector.examine()
    
    # Create necessary directories
    home_dir = pathlib.Path.home()
    project_dir = home_dir / ".vnstock"
    project_dir.mkdir(exist_ok=True)
    id_dir = project_dir / 'id'
    id_dir.mkdir(exist_ok=True)
    
    # Create environment.json file that vnstock looks for
    env_file = id_dir / "environment.json"
    env_data = {
        "accepted_agreement": True,
        "timestamp": datetime.now().isoformat(),
        "machine_id": system_info['machine_id']
    }
    
    try:
        with open(env_file, "w") as f:
            json.dump(env_data, f)
        print("Vnstock terms accepted successfully.")
        return True
    except Exception as e:
        print(f"Error accepting terms: {e}")
        return False


def configure_privacy(level="standard"):
    """Configure privacy level for analytics data"""
    from vnai.scope.state import tracker
    return tracker.setup_privacy(level)


def check_commercial_usage():
    """Check if running in commercial environment"""
    from vnai.scope.profile import inspector
    return inspector.detect_commercial_usage()


def authenticate_for_persistence():
    """Authenticate to Google Drive for persistent settings (Colab)"""
    from vnai.scope.profile import inspector
    return inspector.get_or_create_user_id()
