"""
Auto-detection and configuration of LD_PRELOAD mode.

This module automatically detects if libsfnettee.so is available in the package
and sets the LD_PRELOAD environment variable if it's not already set. This enables
LD_PRELOAD mode automatically without requiring manual configuration.
"""

import os
import sys


def _auto_enable_ld_preload() -> bool:
    """
    Automatically enable LD_PRELOAD mode if libsfnettee.so is available.

    This function:
    1. Checks if LD_PRELOAD is already set with libsfnettee.so
    2. If not, searches for libsfnettee.so in the sf_veritas package
    3. If found, sets LD_PRELOAD environment variable
    4. Returns True if LD_PRELOAD mode is active, False otherwise

    This allows the library to automatically use LD_PRELOAD mode when available,
    without requiring manual configuration in docker-compose or entrypoint scripts.

    Returns:
        True if LD_PRELOAD mode is active (either already set or newly enabled)
        False if libsfnettee.so is not available
    """
    # Check if LD_PRELOAD is already set with libsfnettee.so
    current_ld_preload = os.getenv("LD_PRELOAD", "")
    if "libsfnettee.so" in current_ld_preload or "_sfteepreload" in current_ld_preload:
        if os.getenv("SF_DEBUG", "false").lower() == "true":
            sys.stderr.write(f"[sf_veritas] LD_PRELOAD already set: {current_ld_preload}\n")
            sys.stderr.flush()
        return True

    # Check for SF_TEE_PRELOAD_ONLY flag (forces LD_PRELOAD mode)
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        if os.getenv("SF_DEBUG", "false").lower() == "true":
            sys.stderr.write("[sf_veritas] LD_PRELOAD mode forced via SF_TEE_PRELOAD_ONLY\n")
            sys.stderr.flush()
        return True

    # Find libsfnettee.so in the sf_veritas package
    try:
        # Get the directory containing this module (avoid circular import)
        package_dir = os.path.dirname(os.path.abspath(__file__))
        libsfnettee_path = os.path.join(package_dir, "libsfnettee.so")

        # Check if the file exists
        if os.path.isfile(libsfnettee_path):
            # Set LD_PRELOAD environment variable
            if current_ld_preload:
                # Append to existing LD_PRELOAD (space-separated)
                os.environ["LD_PRELOAD"] = f"{current_ld_preload} {libsfnettee_path}"
            else:
                os.environ["LD_PRELOAD"] = libsfnettee_path

            if os.getenv("SF_DEBUG", "false").lower() == "true":
                sys.stderr.write(f"[sf_veritas] Auto-enabled LD_PRELOAD mode: {libsfnettee_path}\n")
                sys.stderr.flush()

            return True
        else:
            if os.getenv("SF_DEBUG", "false").lower() == "true":
                sys.stderr.write(f"[sf_veritas] libsfnettee.so not found at {libsfnettee_path}, using Python patches\n")
                sys.stderr.flush()
            return False

    except Exception as e:
        # If anything fails, just fall back to Python patches
        if os.getenv("SF_DEBUG", "false").lower() == "true":
            sys.stderr.write(f"[sf_veritas] Failed to auto-enable LD_PRELOAD: {e}, using Python patches\n")
            sys.stderr.flush()
        return False


# Auto-enable LD_PRELOAD mode when this module is imported
# This happens before any patches are applied, ensuring all code paths
# see the correct LD_PRELOAD setting
# _LD_PRELOAD_ACTIVE = _auto_enable_ld_preload()
_LD_PRELOAD_ACTIVE = False
