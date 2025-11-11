"""Solaris specific parsing logic."""

from __future__ import annotations

import re
from typing import Any

from os_normalizer.constants import PrecisionLevel
from os_normalizer.helpers import precision_from_parts, update_confidence
from os_normalizer.models import OSData

SUNOS_UNAME_RE = re.compile(
    r"SunOS\s+\S+\s+(\d+(?:\.\d+)+)(?:\s+(\d+(?:\.\d+){1,4}))?",
    re.IGNORECASE,
)
SOLARIS_RELEASE_RE = re.compile(
    r"(?:Oracle\s+)?Solaris\s+(\d+(?:\.\d+){0,4})",
    re.IGNORECASE,
)
GENERIC_BUILD_RE = re.compile(r"\bGeneric_(\S+)", re.IGNORECASE)


def parse_solaris(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with Solaris-specific details."""
    # Baseline identity
    p.vendor = p.vendor or "Oracle"
    p.product = p.product or "Oracle Solaris"
    p.kernel_name = "sunos"

    kernel_version: str | None = None
    release_version: str | None = None

    # Extract version information from uname-style lines
    uname_match = SUNOS_UNAME_RE.search(text)
    if uname_match:
        kernel_version = uname_match.group(1)
        release_version = uname_match.group(2) or release_version

    # /etc/release style information
    release_match = SOLARIS_RELEASE_RE.search(text)
    if release_match:
        release_version = release_match.group(1)

    # Normalise kernel version token if present
    if kernel_version:
        p.kernel_version = kernel_version

    # Use the release token if available; fall back to kernel version
    version_source = release_version or kernel_version

    version_build: str | None = None
    major: int | None = None
    minor: int | None = None
    patch: int | None = None

    if version_source:
        major, minor, patch, version_build = _split_solaris_version(version_source)

    # Collect Generic_ build tags and prefer non-empty value
    build_match = GENERIC_BUILD_RE.search(text)
    if build_match:
        version_build = version_build or build_match.group(1)

    if major is not None:
        p.version_major = major
    if minor is not None:
        p.version_minor = minor
    if patch is not None:
        p.version_patch = patch
    if version_build:
        p.version_build = version_build

    if version_source:
        p.precision = precision_from_parts(p.version_major, p.version_minor, p.version_patch, p.version_build)
    else:
        p.precision = PrecisionLevel.PRODUCT

    update_confidence(p, p.precision)
    return p


def _split_solaris_version(version: str) -> tuple[int | None, int | None, int | None, str | None]:
    """Convert Solaris version tokens into (major, minor, patch, build)."""
    parts = [int(token) for token in re.findall(r"\d+", version)]
    if not parts:
        return None, None, None, None

    if parts[0] == 5 and len(parts) >= 2:
        # SunOS 5.x maps to Solaris x
        major = parts[1]
        remainder = parts[2:]
    else:
        major = parts[0]
        remainder = parts[1:]

    minor = remainder[0] if len(remainder) >= 1 else None
    patch = remainder[1] if len(remainder) >= 2 else None
    extra = remainder[2:] if len(remainder) >= 3 else []
    build = ".".join(str(x) for x in extra) if extra else None
    return major, minor, patch, build
