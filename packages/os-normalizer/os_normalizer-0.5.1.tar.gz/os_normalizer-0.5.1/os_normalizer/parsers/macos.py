"""macOS specific parsing logic (refactored)."""

import re
from typing import Any

from os_normalizer.constants import MACOS_ALIASES, MACOS_DARWIN_MAP, PRECISION_ORDER, PrecisionLevel
from os_normalizer.helpers import update_confidence
from os_normalizer.models import OSData

# Regex patterns used only by the macOS parser
DARWIN_RE = re.compile(
    r"\bdarwin\b[^\d\n]*?(\d+)(?:\.(\d+))?(?:\.(\d+))?\b",
    re.IGNORECASE,
)
MACOS_VER_FALLBACK_RE = re.compile(r"\bmacos\s?(\d+)(?:\.(\d+))?", re.IGNORECASE)

def parse_macos(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with macOS-specific details."""
    t = text
    tl = t.lower()

    # Base identity
    p.product = p.product or "macOS"
    p.vendor = p.vendor or "Apple"

    # 1) Alias-based version hints (e.g., "Sequoia" -> macOS 15)
    _apply_alias_hint(tl, p)

    # 2) Darwin kernel mapping to macOS version/codename
    _apply_darwin_mapping(t, p)

    # 3) Fallback: parse "macOS <ver>" from text
    _apply_version_fallback(t, p)

    # 4) Fallback: detect codename from text if still missing
    _apply_codename_fallback(tl, p)

    # Confidence boost based on precision
    update_confidence(p, p.precision)
    return p


def _apply_alias_hint(tl: str, p: OSData) -> None:
    for alias, normalized in MACOS_ALIASES.items():
        if alias in tl:
            parts = normalized.split()
            if len(parts) == 2 and parts[1].isdigit():
                p.version_major = int(parts[1])
                p.precision = _max_precision(p.precision, PrecisionLevel.MAJOR)


def _apply_darwin_mapping(t: str, p: OSData) -> None:
    m = DARWIN_RE.search(t)
    if not m:
        return
    dmaj = int(m.group(1))
    p.kernel_name = "darwin"
    p.kernel_version = ".".join([g for g in m.groups() if g])

    if dmaj in MACOS_DARWIN_MAP:
        prod, ver, code = MACOS_DARWIN_MAP[dmaj]
        p.product = prod
        if ver.isdigit():
            p.version_major = int(ver)
            p.precision = _max_precision(p.precision, PrecisionLevel.MAJOR)
        else:
            x, y, *_ = ver.split(".")
            p.version_major = int(x)
            p.version_minor = int(y)
            p.precision = _max_precision(p.precision, PrecisionLevel.MINOR)
        p.codename = code


def _apply_version_fallback(t: str, p: OSData) -> None:
    if p.version_major:
        return
    mm = MACOS_VER_FALLBACK_RE.search(t)
    if not mm:
        return
    p.version_major = int(mm.group(1))
    if mm.group(2):
        p.version_minor = int(mm.group(2))
        p.precision = _max_precision(p.precision, PrecisionLevel.MINOR)
    else:
        p.precision = _max_precision(p.precision, PrecisionLevel.MAJOR)


def _apply_codename_fallback(tl: str, p: OSData) -> None:
    if p.codename:
        return
    for dmaj, (_, ver, code) in MACOS_DARWIN_MAP.items():
        if code.lower() in tl:
            p.codename = code
            # Provide at least major version from the map
            if isinstance(ver, str) and ver.isdigit():
                p.version_major = int(ver)
                p.precision = _max_precision(p.precision, PrecisionLevel.MAJOR)
            elif isinstance(ver, str) and "." in ver:
                x, *_ = ver.split(".")
                if x.isdigit():
                    p.version_major = int(x)
                    p.precision = _max_precision(p.precision, PrecisionLevel.MAJOR)
            break


def _max_precision(current: PrecisionLevel, new_label: PrecisionLevel) -> PrecisionLevel:
    if not isinstance(current, PrecisionLevel):
        current = PrecisionLevel(current)
    return new_label if PRECISION_ORDER.get(new_label, 0) > PRECISION_ORDER.get(current, 0) else current
