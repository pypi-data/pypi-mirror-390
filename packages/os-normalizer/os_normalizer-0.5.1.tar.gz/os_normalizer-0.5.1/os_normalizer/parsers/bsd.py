"""BSD specific parsing logic (refactored, now parsing os-release metadata)."""

import re
from typing import Any

from os_normalizer.constants import PrecisionLevel
from os_normalizer.helpers import (
    parse_os_release,
    parse_semver_like,
    precision_from_parts,
    update_confidence,
)
from os_normalizer.models import OSData

FREEBSD_RE = re.compile(r"\bfreebsd\b", re.IGNORECASE)
OPENBSD_RE = re.compile(r"\bopenbsd\b", re.IGNORECASE)
NETBSD_RE = re.compile(r"\bnetbsd\b", re.IGNORECASE)

VARIANT_VERSION_RE = re.compile(
    r"\b(?:freebsd|openbsd|netbsd)\b\s+(\d+)(?:\.(\d+))?(?:\.(\d+))?",
    re.IGNORECASE,
)
BSD_CHANNEL_RE = re.compile(
    r"(?:[-_\s])(RELEASE|STABLE|CURRENT|RC\d*|BETA\d*|RC|BETA)\b",
    re.IGNORECASE,
)
BSD_VARIANTS = {
    "freebsd": "FreeBSD",
    "openbsd": "OpenBSD",
    "netbsd": "NetBSD",
}


def parse_bsd(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with BSD-specific details."""
    osrel = _coerce_os_release(data.get("os_release")) if isinstance(data, dict) else None
    variant = _infer_variant(text, osrel)

    # Default shells before os-release enrichment
    canonical_name = BSD_VARIANTS.get(variant, "BSD")
    p.product = canonical_name
    p.vendor = canonical_name
    p.kernel_name = variant if variant else canonical_name.lower()

    # Prefer variant-anchored version pattern; fall back to generic semver
    x, y, z = _extract_version(text)
    p.version_major, p.version_minor, p.version_patch = x, y, z

    # Channel from explicit markers/suffixes
    ch = _extract_channel(text)
    if ch:
        p.channel = ch

    # Apply os-release metadata (mirrors linux parser flow)
    if osrel:
        variant = _apply_os_release(osrel, p, variant)
        if not p.channel:
            p.channel = _extract_channel(osrel.get("VERSION"), osrel.get("PRETTY_NAME"))

    canonical_name = BSD_VARIANTS.get(variant, canonical_name)
    p.product = canonical_name
    p.vendor = canonical_name
    p.kernel_name = variant if variant else canonical_name.lower()

    if p.version_major is not None:
        p.precision = precision_from_parts(p.version_major, p.version_minor, p.version_patch, None)
    else:
        p.precision = PrecisionLevel.PRODUCT

    update_confidence(p, p.precision)
    return p


def _coerce_os_release(obj: Any) -> dict[str, Any] | None:
    if isinstance(obj, str):
        return parse_os_release(obj)
    if isinstance(obj, dict):
        return {str(k).upper(): v for k, v in obj.items()}
    return None


def _infer_variant(text: str, osrel: dict[str, Any] | None) -> str | None:
    variant = _variant_from_osrel(osrel)
    if variant:
        return variant

    tl = text.lower()
    if FREEBSD_RE.search(tl):
        return "freebsd"
    if OPENBSD_RE.search(tl):
        return "openbsd"
    if NETBSD_RE.search(tl):
        return "netbsd"
    return None


def _variant_from_osrel(osrel: dict[str, Any] | None) -> str | None:
    if not osrel:
        return None
    for key in ("ID", "NAME", "PRETTY_NAME"):
        val = osrel.get(key)
        variant = _variant_from_value(val)
        if variant:
            return variant
    return None


def _variant_from_value(value: Any) -> str | None:
    if not value:
        return None
    text = str(value).lower()
    if "freebsd" in text:
        return "freebsd"
    if "openbsd" in text:
        return "openbsd"
    if "netbsd" in text:
        return "netbsd"
    return None


def _apply_os_release(osrel: dict[str, Any], p: OSData, variant: str | None) -> str | None:
    distro_id = osrel.get("ID")
    if distro_id:
        did = str(distro_id).lower()
        p.distro = did
        variant = variant or _variant_from_value(did)

    like = osrel.get("ID_LIKE")
    if like:
        if isinstance(like, list):
            p.like_distros = [str(item).lower() for item in like]
        else:
            p.like_distros = [str(like).lower()]

    pretty = osrel.get("PRETTY_NAME") or osrel.get("NAME")
    if pretty:
        p.pretty_name = str(pretty)
        if not p.codename:
            m = re.search(r"\(([^)]+)\)", str(pretty))
            if m:
                candidate = m.group(1).strip()
                if candidate:
                    p.codename = candidate.title()

    vcode = osrel.get("VERSION_CODENAME")
    if vcode:
        p.codename = str(vcode).title()

    # Version precedence: VERSION_ID > VERSION (captures suffixes like -RELEASE)
    if not _apply_version_id(osrel.get("VERSION_ID"), p):
        _apply_version_id(osrel.get("VERSION"), p)

    # os-release name hints might refine the variant
    name_hint = osrel.get("NAME") or osrel.get("PRETTY_NAME")
    variant = variant or _variant_from_value(name_hint)

    return variant


def _apply_version_id(value: Any, p: OSData) -> bool:
    if not value:
        return False
    major, minor, patch = parse_semver_like(str(value))
    updated = False
    if major is not None:
        p.version_major = major
        updated = True
    if minor is not None:
        p.version_minor = minor
        updated = True
    if patch is not None:
        p.version_patch = patch
        updated = True
    return updated


def _extract_version(text: str) -> tuple[int | None, int | None, int | None]:
    m = VARIANT_VERSION_RE.search(text)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) else None
        patch = int(m.group(3)) if m.group(3) else None
        return major, minor, patch
    return parse_semver_like(text)


def _extract_channel(*chunks: Any) -> str | None:
    for chunk in chunks:
        if not chunk:
            continue
        text = str(chunk)
        for m in BSD_CHANNEL_RE.finditer(text):
            if _channel_preceded_by_os(text, m.start()):
                continue
            return m.group(1).upper()
    return None


def _channel_preceded_by_os(text: str, idx: int) -> bool:
    """Ignore matches where the preceding token is the literal 'os' (e.g., 'os-release')."""
    pos = idx - 1
    letters: list[str] = []
    while pos >= 0 and text[pos].isalpha():
        letters.append(text[pos].lower())
        pos -= 1
    if not letters:
        return False
    prefix = "".join(reversed(letters))
    return prefix == "os"
