"""Utility functions shared across the OS fingerprinting package."""

import re
from typing import Any

from .constants import ARCH_SYNONYMS, ARCHITECTURE_TOKENS, PrecisionLevel
from .models import OSData


def norm_arch(s: str | None) -> str | None:
    """Normalise an architecture string using ARCH_SYNONYMS."""
    if not s:
        return None
    a = s.strip().lower()
    return ARCH_SYNONYMS.get(a, a)


def parse_semver_like(text: str) -> tuple[int | None, int | None, int | None]:
    """Extract up to three integer components from a version-like string.

    Returns (major, minor, patch) where missing parts are None.
    """
    m = re.search(r"\b(\d+)(?:\.(\d+))?(?:\.(\d+))?\b", text)
    if not m:
        return None, None, None
    major = int(m.group(1))
    minor = int(m.group(2)) if m.group(2) else None
    patch = int(m.group(3)) if m.group(3) else None
    return major, minor, patch


def precision_from_parts(
    major: int | None,
    minor: int | None,
    patch: int | None,
    build: str | None,
) -> PrecisionLevel:
    """Derive a precision label from version components."""
    if build:
        return PrecisionLevel.BUILD
    if patch is not None:
        return PrecisionLevel.PATCH
    if minor is not None:
        return PrecisionLevel.MINOR
    if major is not None:
        return PrecisionLevel.MAJOR
    return PrecisionLevel.PRODUCT


def canonical_key(p: OSData) -> str:
    """Generate a deterministic key for an OSData instance.

    The function expects the object to have vendor, product, version_* and edition fields.
    """
    vendor = (p.vendor or "-").lower()
    product = (p.product or "-").lower()
    version = ".".join([str(x) for x in [p.version_major, p.version_minor, p.version_patch] if x is not None]) or "-"
    edition = (p.edition or "-").lower()
    codename = (p.codename or "-").lower()
    return f"{vendor}:{product}:{version}:{edition}:{codename}"


# Regex for extracting an architecture token from free-form text
_ARCH_PATTERN = "|".join(
    sorted((re.escape(token) for token in ARCHITECTURE_TOKENS), key=len, reverse=True)
)
ARCH_TEXT_RE = re.compile(rf"\b({_ARCH_PATTERN})\b", re.IGNORECASE)


def extract_arch_from_text(text: str) -> str | None:
    """Fallback architecture extraction from arbitrary text."""
    m = ARCH_TEXT_RE.search(text)
    if not m:
        return None
    raw = m.group(1).lower()
    return ARCH_SYNONYMS.get(raw, raw)


def parse_os_release(blob_text: str) -> dict[str, Any]:
    """Parse the contents of an /etc/os-release style file.

    Returns a dict with selected keys (ID, ID_LIKE, PRETTY_NAME, VERSION_ID, VERSION_CODENAME).
    """
    out: dict[str, Any] = {}
    for line in blob_text.splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#") or "=" not in clean:
            continue
        k, v = clean.split("=", 1)
        k = k.strip().upper()
        if k == "ID_LIKE":
            out[k] = [s.strip().lower() for s in re.split(r"[ ,]+", v.strip("\"'").strip()) if s]
        else:
            out[k] = v.strip("\"'")
    return out


def update_confidence(p: OSData, precision: PrecisionLevel | str) -> None:
    """Boost confidence based on the determined precision level.

    The mapping mirrors the original ad-hoc values used throughout the monolithic file.
    """
    if isinstance(precision, PrecisionLevel):
        level = precision
    else:
        try:
            level = PrecisionLevel(str(precision))
        except ValueError:
            level = PrecisionLevel.UNKNOWN

    boost_map = {
        PrecisionLevel.BUILD: 0.85,
        PrecisionLevel.PATCH: 0.80,
        PrecisionLevel.MINOR: 0.75,
        PrecisionLevel.MAJOR: 0.70,
        PrecisionLevel.PRODUCT: 0.60,
    }
    p.confidence = max(p.confidence, boost_map.get(level, 0.5))
