"""Version information for the ragora package."""

import re

__version__ = "1.2.0"

# Parse version according to PEP 440
# Handles formats like: 1.2.0, 1.2.0rc1, 1.2.0-rc1, 1.2.0a1, 1.2.0b1, 1.2.0.dev1
_version_pattern = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"  # Base version (major.minor.patch)
    r"(?:[-.]?(?P<prerelease_type>rc|a|alpha|b|beta|dev)[-.]?(?P<prerelease_num>\d+))?"  # Optional prerelease
    r"(?:.*)?$"  # Allow any trailing content
)

def _parse_version(version_str: str) -> tuple:
    """Parse version string into a tuple compatible with PEP 440."""
    match = _version_pattern.match(version_str)
    if not match:
        # Fallback: try simple split for edge cases
        parts = version_str.split(".")[:3]
        try:
            return tuple(map(int, parts))
        except ValueError:
            return tuple([int(p) if p.isdigit() else 0 for p in parts[:3]])
    
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    
    # Check for prerelease identifier
    prerelease_type = match.group("prerelease_type")
    prerelease_num = match.group("prerelease_num")
    
    if prerelease_type and prerelease_num:
        # Normalize prerelease type (rc, a/alpha, b/beta, dev)
        if prerelease_type in ("a", "alpha"):
            prerelease_type = "alpha"
        elif prerelease_type in ("b", "beta"):
            prerelease_type = "beta"

        
        return (major, minor, patch, prerelease_type + prerelease_num)
    else:
        return (major, minor, patch)

__version_info__ = _parse_version(__version__)
