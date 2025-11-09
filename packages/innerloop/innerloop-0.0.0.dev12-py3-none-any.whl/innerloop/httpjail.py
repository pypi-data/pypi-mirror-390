"""HTTP jail container detection and mode selection.

This module implements the progressive enforcement strategy for httpjail
in containerized environments, with automatic fallback:

1. Strong mode (default on bare metal) - netns + nftables
2. Server mode (default in containers) - explicit proxy on 127.0.0.1
3. Weak mode (fallback) - cooperative env vars only

The strategy document is at:
/home/user/InnerLoop/PERMISSION_ENFORCEMENT_ANALYSIS.md
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from enum import Enum
from typing import NamedTuple

logger = logging.getLogger(__name__)


class HttpJailMode(str, Enum):
    """HTTP jail enforcement modes.

    Modes are ordered by enforcement strength (strong > server > weak).
    """

    STRONG = "strong"  # netns + nftables (requires capabilities)
    SERVER = "server"  # explicit proxy on 127.0.0.1
    WEAK = "weak"  # cooperative env vars only


class HttpJailConfig(NamedTuple):
    """Configuration for httpjail wrapping."""

    mode: HttpJailMode
    bind_address: str = "127.0.0.1"
    http_port: int = 8080
    https_port: int = 8443


def detect_container() -> bool:
    """Detect if running inside a container.

    Uses heuristics:
    - Presence of /.dockerenv
    - /proc/1/cgroup contains docker|kubepods|libpod
    - /proc/1/mountinfo contains overlay

    Returns:
        True if likely running in a container, False otherwise.
    """
    # Check for /.dockerenv
    if os.path.exists("/.dockerenv"):
        logger.debug("Container detected: /.dockerenv exists")
        return True

    # Check /proc/1/cgroup for container indicators
    try:
        with open("/proc/1/cgroup") as f:
            content = f.read()
            if any(
                marker in content
                for marker in ["docker", "kubepods", "libpod"]
            ):
                logger.debug(
                    "Container detected: /proc/1/cgroup contains container marker"
                )
                return True
    except (FileNotFoundError, PermissionError):
        pass

    # Check /proc/1/mountinfo for overlay filesystem
    try:
        with open("/proc/1/mountinfo") as f:
            content = f.read()
            if "overlay" in content:
                logger.debug(
                    "Container detected: /proc/1/mountinfo contains overlay"
                )
                return True
    except (FileNotFoundError, PermissionError):
        pass

    logger.debug("No container detected")
    return False


def check_nftables_available() -> bool:
    """Check if nftables is available.

    Returns:
        True if nft binary exists and can list rulesets, False otherwise.
    """
    nft_path = shutil.which("nft")
    if not nft_path:
        logger.debug("nftables not available: nft binary not found")
        return False

    try:
        # Try to list rulesets (requires minimal permissions)
        result = subprocess.run(
            [nft_path, "list", "ruleset"],
            capture_output=True,
            timeout=2.0,
            check=False,
        )
        available = result.returncode == 0
        if available:
            logger.debug("nftables available: nft list ruleset succeeded")
        else:
            logger.debug(
                "nftables not available: nft list ruleset failed with code %d",
                result.returncode,
            )
        return available
    except (subprocess.TimeoutExpired, OSError) as e:
        logger.debug("nftables not available: %s", e)
        return False


def select_httpjail_mode(
    force_mode: HttpJailMode | None = None,
    force_weak: bool = False,
) -> HttpJailMode:
    """Select appropriate httpjail mode based on environment.

    Decision logic:
    1. If force_mode is set (via HTTPJAIL_MODE env), use it
    2. If force_weak is True (via FORCE_WEAK=1 env), use weak mode
    3. Auto-detect based on container status and capabilities:
       - In container without nftables → server mode
       - In container with nftables → try strong, fallback to server
       - Not in container with nftables → strong mode
       - Not in container without nftables → weak mode

    Args:
        force_mode: Explicitly requested mode (overrides all detection)
        force_weak: Force weak mode (for local dev)

    Returns:
        Selected HttpJailMode
    """
    # Explicit override
    if force_mode is not None:
        logger.info(
            "Using explicitly requested httpjail mode: %s", force_mode.value
        )
        return force_mode

    # Force weak mode for local dev
    if force_weak:
        logger.info("Using weak mode (FORCE_WEAK=1)")
        return HttpJailMode.WEAK

    # Auto-detect
    in_container = detect_container()
    has_nftables = check_nftables_available()

    if in_container:
        if has_nftables:
            logger.info(
                "Container detected with nftables; attempting strong mode "
                "(runtime fallback to server/weak on capability errors)"
            )
            return HttpJailMode.STRONG
        else:
            logger.info(
                "Container detected without nftables; using server mode "
                "(explicit proxy on 127.0.0.1, fallback to weak on errors)"
            )
            return HttpJailMode.SERVER
    else:
        if has_nftables:
            logger.debug("Using strong mode (bare metal with nftables)")
            return HttpJailMode.STRONG
        else:
            logger.info(
                "nftables not available; using weak mode "
                "(cooperative env vars only)"
            )
            return HttpJailMode.WEAK


def build_httpjail_command(
    base_cmd: list[str],
    js_predicate: str,
    mode: HttpJailMode,
) -> list[str]:
    """Build httpjail command with appropriate mode flags.

    Args:
        base_cmd: The command to wrap (e.g., ["opencode", "run", ...])
        js_predicate: JavaScript predicate for host filtering
        mode: Selected httpjail mode

    Returns:
        Complete command list with httpjail wrapper
    """
    if mode == HttpJailMode.STRONG:
        # Strong mode: default behavior, no special flags
        return ["httpjail", "--js", js_predicate, "--"] + base_cmd
    elif mode == HttpJailMode.SERVER:
        # Server mode: run as explicit proxy on loopback
        return ["httpjail", "--server", "--js", js_predicate, "--"] + base_cmd
    elif mode == HttpJailMode.WEAK:
        # Weak mode: cooperative env vars only
        return ["httpjail", "--weak", "--js", js_predicate, "--"] + base_cmd
    else:
        raise ValueError(f"Unknown httpjail mode: {mode}")


def get_mode_from_env() -> HttpJailMode | None:
    """Parse HTTPJAIL_MODE environment variable.

    Returns:
        HttpJailMode if valid mode is set, None otherwise
    """
    mode_str = os.environ.get("HTTPJAIL_MODE", "").lower()
    if not mode_str:
        return None

    try:
        return HttpJailMode(mode_str)
    except ValueError:
        logger.warning(
            "Invalid HTTPJAIL_MODE value: %s (valid: strong, server, weak)",
            mode_str,
        )
        return None


def should_require_httpjail() -> bool:
    """Check if httpjail is required (INNERLOOP_REQUIRE_HTTPJAIL=1).

    Returns:
        True if httpjail is required, False otherwise
    """
    return os.environ.get("INNERLOOP_REQUIRE_HTTPJAIL", "0") == "1"


def should_force_weak() -> bool:
    """Check if weak mode should be forced (FORCE_WEAK=1).

    Returns:
        True if weak mode should be forced, False otherwise
    """
    return os.environ.get("FORCE_WEAK", "0") == "1"


def setup_proxy_env(
    mode: HttpJailMode, config: HttpJailConfig
) -> dict[str, str]:
    """Set up HTTP(S)_PROXY environment variables for server/weak modes.

    Args:
        mode: Selected httpjail mode
        config: HttpJail configuration

    Returns:
        Dict of environment variables to set
    """
    env: dict[str, str] = {}

    if mode in (HttpJailMode.SERVER, HttpJailMode.WEAK):
        # Set proxy environment variables
        env["HTTP_PROXY"] = f"http://{config.bind_address}:{config.http_port}"
        env["HTTPS_PROXY"] = (
            f"http://{config.bind_address}:{config.https_port}"
        )
        env["NO_PROXY"] = "127.0.0.1,localhost"

        logger.debug(
            "Set proxy env vars: HTTP_PROXY=%s, HTTPS_PROXY=%s",
            env["HTTP_PROXY"],
            env["HTTPS_PROXY"],
        )

    return env


def is_httpjail_capability_error(stderr: str) -> bool:
    """Detect if stderr indicates httpjail failed due to missing capabilities.

    Args:
        stderr: stderr output from failed httpjail process

    Returns:
        True if error is likely due to missing capabilities (should retry with weaker mode)
    """
    # Common error patterns when capabilities are insufficient
    capability_error_patterns = [
        "unshare",  # namespace operations require CAP_SYS_ADMIN
        "permission denied",  # generic permission error
        "operation not permitted",  # EPERM from syscalls
        "namespace",  # namespace creation failures
        "CAP_",  # explicit capability errors
        "nftables",  # nftables setup failures
        "EADDRNOTAVAIL",  # bind failures in certain environments
        "bind",  # socket bind failures
    ]

    stderr_lower = stderr.lower()
    return any(
        pattern.lower() in stderr_lower
        for pattern in capability_error_patterns
    )


def get_fallback_mode(current_mode: HttpJailMode) -> HttpJailMode | None:
    """Get the next weaker httpjail mode for fallback.

    Args:
        current_mode: Current mode that failed

    Returns:
        Next weaker mode, or None if already at weakest mode
    """
    if current_mode == HttpJailMode.STRONG:
        return HttpJailMode.SERVER
    elif current_mode == HttpJailMode.SERVER:
        return HttpJailMode.WEAK
    else:
        # Already at weakest mode
        return None
