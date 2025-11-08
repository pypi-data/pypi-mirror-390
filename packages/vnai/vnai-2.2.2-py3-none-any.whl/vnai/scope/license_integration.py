import logging
from typing import Optional

logger = logging.getLogger(__name__)


def check_license_status() -> Optional[bool]:
    """
    Check if user is paid using cached license status
    with graceful degradation

    Returns:
        - True if paid user
        - False if free user (or cache expired)
        - None if cannot determine
    """
    try:
        from vnai.scope.license import license_cache
        return license_cache.get_is_paid()
    except ImportError:
        logger.warning("LicenseCache not available")
        return None
    except Exception as e:
        logger.error(f"Error checking license status: {e}")
        return None


def update_license_from_vnii() -> bool:
    """
    Update license cache by checking vnii

    Returns:
        True if successfully updated, False otherwise
    """
    try:
        from vnii import lc_init
        from vnai.scope.license import license_cache

        # Call vnii license check
        license_info = lc_init(repo_name='vnstock')
        status = license_info.get('status', '').lower()

        # Determine if paid
        is_paid = 'recognized and verified' in status

        # Update cache
        license_cache.set(is_paid)

        logger.info(f"License updated: is_paid={is_paid}")
        return True
    except ImportError:
        logger.warning("vnii or lc_init not available")
        return False
    except Exception as e:
        logger.error(f"Error updating license from vnii: {e}")
        return False


# ============================================================================
# GUARDIAN INTEGRATION: Skip rate limits for paid users
# ============================================================================

_original_guardian_verify = None


def guardian_verify_with_license(
    guardian_instance,
    operation_id: str,
    resource_type: str = "default"
) -> bool:
    """
    Modified Guardian.verify() that skips rate limits for paid users

    Args:
        guardian_instance: Guardian singleton instance
        operation_id: Operation identifier
        resource_type: Type of resource being accessed

    Returns:
        True if allowed (or paid user), raises RateLimitExceeded otherwise
    """
    # Check if user is paid
    is_paid = check_license_status()

    if is_paid is True:
        # Paid user: skip rate limits
        logger.debug(
            f"Skipping rate limit for paid user: {resource_type}"
        )
        return True

    # Not paid or unknown: use normal rate limiting
    global _original_guardian_verify
    if _original_guardian_verify is None:
        _original_guardian_verify = guardian_instance.__class__.verify

    return _original_guardian_verify(
        guardian_instance, operation_id, resource_type
    )


# ============================================================================
# CONTENT MANAGER INTEGRATION: Suppress ads for paid users
# ============================================================================

_original_content_should_display = None


def content_manager_should_display_with_license(
    content_manager_instance
) -> bool:
    """
    Modified ContentManager presentation logic for paid users

    Args:
        content_manager_instance: ContentManager singleton instance

    Returns:
        True if should display ads, False for paid users (no ads)
    """
    # Check if user is paid
    is_paid = check_license_status()

    if is_paid is True:
        # Paid user: don't show ads
        logger.debug("Suppressing ads for paid user")
        return False

    # Not paid or unknown: show ads normally
    # Default behavior when user status is None or False
    return True


# ============================================================================
# INTEGRATION HELPER
# ============================================================================

def integrate_license_features() -> bool:
    """
    Integrate license-based features into Guardian and ContentManager

    Returns:
        True if integration successful
    """
    try:
        from vnai.beam.quota import guardian
        from vnai.scope.promo import ContentManager

        # Patch Guardian.verify method
        original_verify = guardian.verify

        def patched_verify(operation_id: str, resource_type: str = "default"):
            return guardian_verify_with_license(
                guardian, operation_id, resource_type
            )

        guardian.verify = patched_verify
        logger.info("Guardian.verify() patched for license support")

        # Get ContentManager instance
        content_mgr = ContentManager()

        # Patch ContentManager presentation logic
        original_present = getattr(content_mgr, 'present', None)

        def patched_present():
            if not content_manager_should_display_with_license(
                content_mgr
            ):
                logger.debug("Skipping ad display for paid user")
                return False

            if original_present and callable(original_present):
                return original_present()
            return False

        if hasattr(content_mgr, 'present'):
            content_mgr.present = patched_present
            logger.info("ContentManager.present() patched for license")

        logger.info("License-based features successfully integrated")
        return True

    except Exception as e:
        logger.error(f"Error integrating license features: {e}")
        return False


# ============================================================================
# AUTO-INTEGRATION (called on module import)
# ============================================================================

def auto_integrate():
    """Auto-integrate license features when module is imported"""
    try:
        integrate_license_features()
    except Exception as e:
        logger.warning(f"Auto-integration of license features failed: {e}")


# Run auto-integration
auto_integrate()
