"""Mobile device specific parsing logic."""

import re
from typing import Any

from os_normalizer.constants import OSFamily, PrecisionLevel
from os_normalizer.helpers import (
    parse_semver_like,
    precision_from_parts,
    update_confidence,
)
from os_normalizer.models import OSData


def parse_mobile(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with mobile device-specific details."""
    t = text.lower()

    # Detect if it's HarmonyOS before other mobile platforms to avoid vendor overlaps
    if OSFamily.HARMONYOS.value in t:
        p.product = "HarmonyOS"
        p.vendor = "Huawei"
        m = re.search(r"\b(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?\b", text)
        if m:
            p.version_major = int(m.group(1))
            p.version_minor = int(m.group(2)) if m.group(2) else None
            p.version_patch = int(m.group(3)) if m.group(3) else None
            p.version_build = m.group(4) if m.group(4) else None
    # Detect if it's iOS or Android
    elif OSFamily.IOS.value in t or "ipados" in t:
        p.product = "iOS/iPadOS"
        p.vendor = "Apple"
    elif OSFamily.ANDROID.value in t:
        p.product = "Android"
        p.vendor = "Google"
    else:
        # Default for unknown mobile OS
        p.product = "Mobile OS"
        p.vendor = None

    # Extract version info using semver-like parsing
    if p.version_major is None:
        x, y, z = parse_semver_like(t)
        p.version_major, p.version_minor, p.version_patch = x, y, z

    p.precision = (
        precision_from_parts(p.version_major, p.version_minor, p.version_patch, p.version_build)
        if p.version_major is not None
        else PrecisionLevel.PRODUCT
    )

    # Boost confidence based on precision
    update_confidence(p, p.precision)

    return p
