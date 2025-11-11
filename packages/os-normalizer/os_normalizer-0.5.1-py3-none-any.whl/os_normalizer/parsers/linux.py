"""Linux specific parsing logic (refactored)."""

import re
from typing import Any, Optional

from os_normalizer.constants import PrecisionLevel
from os_normalizer.helpers import parse_os_release, update_confidence
from os_normalizer.models import OSData

# Regex patterns used only by the Linux parser
KERNEL_RE = re.compile(
    r"\b(kernel|uname)\b.*?\b(\d+\.\d+(?:\.\d+)?(?:-\S+)?)",
    re.IGNORECASE,
)
LINUX_VER_FALLBACK_RE = re.compile(
    r"\bLinux\b[^\n]*?\b(\d+\.\d+(?:\.\d+)?(?:-[A-Za-z0-9._-]+)?)\b",
    re.IGNORECASE,
)


def parse_linux(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with Linux-specific details."""
    p.kernel_name = "linux"

    osrel = _coerce_os_release(data.get("os_release")) if isinstance(data, dict) else None

    # 1) Kernel version extraction
    p.kernel_version = _extract_kernel_version(text)

    # 2) Apply os-release information when present
    if osrel:
        _apply_os_release(osrel, p)
    else:
        p.product = p.product or "Linux"
        p.precision = PrecisionLevel.FAMILY

    update_confidence(p, p.precision)
    return p


def _coerce_os_release(obj: Any) -> dict[str, Any] | None:
    if isinstance(obj, str):
        return parse_os_release(obj)
    if isinstance(obj, dict):
        return {k.upper(): v for k, v in obj.items()}
    return None


def _extract_kernel_version(text: str) -> str | None:
    m = KERNEL_RE.search(text)
    if m:
        return m.group(2)
    m2 = LINUX_VER_FALLBACK_RE.search(text)
    if m2:
        return m2.group(1)
    return None


def _apply_os_release(osrel: dict[str, Any], p: OSData) -> None:
    distro_id = osrel.get("ID")
    if distro_id:
        p.distro = str(distro_id).lower()

    like = osrel.get("ID_LIKE")
    if like:
        p.like_distros = [s.lower() for s in like] if isinstance(like, list) else [str(like).lower()]

    p.pretty_name = osrel.get("PRETTY_NAME") or osrel.get("NAME")

    if not p.codename and p.pretty_name:
        # Fallback: try to extract codename from parenthetical in pretty name (e.g. "Debian ... (buster)")
        m = re.search(r"\(([^)]+)\)", str(p.pretty_name))
        if m:
            candidate = m.group(1).strip()
            if candidate:
                p.codename = candidate.title()

    _apply_version_id(osrel.get("VERSION_ID"), p)

    vcode = osrel.get("VERSION_CODENAME")
    if vcode:
        p.codename = str(vcode).title()

    if p.pretty_name and "LTS" in str(p.pretty_name).upper():
        p.channel = "LTS"

    p.vendor = _vendor_for_distro(p.distro) if p.distro else p.vendor

    name = osrel.get("NAME")
    p.product = (
        (name if name else (p.distro or "Linux")).replace('"', "") if isinstance(name, str) else (p.distro or "Linux")
    )

    # Precision from version parts
    if p.version_patch is not None:
        p.precision = PrecisionLevel.PATCH
    elif p.version_minor is not None:
        p.precision = PrecisionLevel.MINOR
    elif p.version_major is not None:
        p.precision = PrecisionLevel.MAJOR
    else:
        p.precision = PrecisionLevel.FAMILY


def _apply_version_id(vid: Any, p: OSData) -> None:
    if not vid:
        return
    parts = re.split(r"[.]+", str(vid))
    if len(parts) >= 1 and parts[0].isdigit():
        p.version_major = int(parts[0])
    if len(parts) >= 2 and parts[1].isdigit():
        p.version_minor = int(parts[1])
    if len(parts) >= 3 and parts[2].isdigit():
        p.version_patch = int(parts[2])


def _vendor_for_distro(distro: str | None) -> str | None:
    vendor_by_distro = {
        "ubuntu": "Canonical",
        "debian": "Debian",
        "rhel": "Red Hat",
        "rocky": "Rocky",
        "almalinux": "AlmaLinux",
        "centos": "Red Hat",
        "amzn": "Amazon",
        "amazon": "Amazon",
        "sles": "SUSE",
        "opensuse": "SUSE",
        "arch": "Arch",
        "fedora": "Fedora Project",
    }
    return vendor_by_distro.get(distro) if distro else None
