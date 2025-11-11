"""VMware ESXi specific parsing logic."""

from __future__ import annotations

import re
from typing import Any

from os_normalizer.constants import PrecisionLevel
from os_normalizer.helpers import parse_semver_like, precision_from_parts, update_confidence
from os_normalizer.models import OSData

ESXI_PRODUCT_RE = re.compile(
    r"VMware\s+ESXi\s+(\d+(?:\.\d+){1,3})(?:\s+(?:build|Build)\s*[-#]?(\d+))?",
    re.IGNORECASE,
)
VMKERNEL_RE = re.compile(
    r"VMkernel\s+\S+\s+(\d+(?:\.\d+){1,3})(?:\s+#(\d+))?",
    re.IGNORECASE,
)
ESXCLI_VERSION_RE = re.compile(r"^Version:\s*(\d+(?:\.\d+){1,3})\s*$", re.IGNORECASE | re.MULTILINE)
ESXCLI_BUILD_RE = re.compile(r"^Build:\s*(\d+)\s*$", re.IGNORECASE | re.MULTILINE)
ESXCLI_UPDATE_RE = re.compile(r"^Update:\s*(.+?)\s*$", re.IGNORECASE | re.MULTILINE)


def parse_esxi(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with ESXi-specific details."""
    p.vendor = p.vendor or "VMware"
    p.product = p.product or "VMware ESXi"
    p.kernel_name = "vmkernel"

    version: str | None = None
    build: str | None = None
    channel: str | None = None

    prod_match = ESXI_PRODUCT_RE.search(text)
    if prod_match:
        version = prod_match.group(1)
        build = prod_match.group(2) or build

    kernel_match = VMKERNEL_RE.search(text)
    if kernel_match:
        version = version or kernel_match.group(1)
        build = build or kernel_match.group(2)

    version_line = ESXCLI_VERSION_RE.search(text)
    if version_line and not version:
        version = version_line.group(1)

    build_line = ESXCLI_BUILD_RE.search(text)
    if build_line and not build:
        build = build_line.group(1)

    update_line = ESXCLI_UPDATE_RE.search(text)
    if update_line:
        channel = update_line.group(1).strip()

    if build:
        p.version_build = build

    if channel:
        # Normalise "3" -> "Update 3", but keep existing text if already descriptive
        if channel.isdigit():
            p.channel = f"Update {channel}"
        elif channel.lower().startswith("update"):
            p.channel = channel
        else:
            p.channel = channel

    if version:
        p.kernel_version = version
        major, minor, patch = parse_semver_like(version)
        if major is not None:
            p.version_major = major
        if minor is not None:
            p.version_minor = minor
        if patch is not None:
            p.version_patch = patch
        p.precision = precision_from_parts(p.version_major, p.version_minor, p.version_patch, p.version_build)
    else:
        p.precision = PrecisionLevel.PRODUCT

    update_confidence(p, p.precision)
    return p
