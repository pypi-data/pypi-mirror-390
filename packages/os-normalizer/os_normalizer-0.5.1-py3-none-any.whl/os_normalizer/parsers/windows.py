"""Windows specific parsing logic."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from os_normalizer.constants import (
    WINDOWS_BUILD_MAP,
    WINDOWS_NT_CLIENT_MAP,
    WINDOWS_NT_SERVER_MAP,
    WINDOWS_PRODUCT_PATTERNS,
    WINDOWS_SERVER_BUILD_MAP,
    PrecisionLevel,
)
from os_normalizer.helpers import extract_arch_from_text, update_confidence

if TYPE_CHECKING:
    from os_normalizer.models import OSData

VERSION_PATTERN = re.compile(r"\b(\d+)\.(\d+)\.(\d+)(?:\.(\d+))?\b")
NT_PATTERN = re.compile(r"\bnt\s*(\d+)(?:\.(\d+))?", re.IGNORECASE)
BUILD_PATTERN = re.compile(r"\bbuild\s*(?:number\s*)?[:=\s-]*?(\d{3,5})\b", re.IGNORECASE)
KERNEL_PATTERN = re.compile(r"\bkernel\s*[:=\s-]*?(\d+)(?:\.(\d+))?", re.IGNORECASE)
SP_PATTERN = re.compile(r"\bsp(\d)\b", re.IGNORECASE)

EDITION_KEYWORDS: list[tuple[str, str]] = [
    ("iot enterprise", "Enterprise"),
    ("enterprise", "Enterprise"),
    ("education", "Education"),
    ("datacenter", "Datacenter"),
    ("standard", "Standard"),
    ("professional", "Professional"),
    (" pro ", "Professional"),
    (" home ", "Home"),
]


@dataclass(frozen=True)
class ProductDefaults:
    version_major: int | None = None
    version_minor: int | None = None
    version_patch: int | None = None
    version_build: str | None = None
    kernel_version: str | None = None


PRODUCT_DEFAULTS: dict[str, ProductDefaults] = {
    "Windows NT 4.0": ProductDefaults(4, 0, None, "1381", "4.0"),
    "Windows 98": ProductDefaults(4, 10, None, "1998", "4.10"),
    "Windows ME": ProductDefaults(4, 90, None, "3000", "4.9"),
    "Windows 2000": ProductDefaults(5, 0, None, "2195", "5.0"),
    "Windows XP": ProductDefaults(5, 1, None, "2600", "5.1"),
    "Windows Vista": ProductDefaults(6, 0, None, "6000", "6.0"),
    "Windows Vista SP1": ProductDefaults(6, 0, None, "6001", "6.0"),
    "Windows Vista SP2": ProductDefaults(6, 0, None, "6002", "6.0"),
    "Windows 7": ProductDefaults(6, 1, None, "7601", "6.1"),
    "Windows 7 SP1": ProductDefaults(6, 1, None, "7601", "6.1"),
    "Windows 7 SP2": ProductDefaults(6, 1, None, "7601", "6.1"),
    "Windows 8": ProductDefaults(6, 2, None, "9200", "6.2"),
    "Windows 8.1": ProductDefaults(6, 3, None, "9600", "6.3"),
    "Windows 10": ProductDefaults(10, 0, None, None, None),
    "Windows 11": ProductDefaults(10, 0, None, None, None),
    "Windows Server 2003": ProductDefaults(5, 2, None, "3790", "5.2"),
    "Windows Server 2008": ProductDefaults(6, 0, None, "6002", "6.0"),
    "Windows Server 2008 R2": ProductDefaults(6, 1, None, "7600", "6.1"),
    "Windows Server 2008 R2 SP1": ProductDefaults(6, 1, None, "7601", "6.1"),
    "Windows Server 2012": ProductDefaults(6, 2, None, "9200", "6.2"),
    "Windows Server 2012 R2": ProductDefaults(6, 3, None, "9600", "6.3"),
    "Windows Server 2016": ProductDefaults(10, 0, None, None, None),
    "Windows Server 2019": ProductDefaults(10, 0, None, None, None),
    "Windows Server 2022": ProductDefaults(10, 0, None, None, None),
    "Windows Server 2025": ProductDefaults(10, 0, None, None, None),
}


@dataclass
class VersionState:
    """Intermediate container for NT/build details discovered in the banner."""

    nt_major: int | None = None
    nt_minor: int | None = None
    build: str | None = None
    patch: int | None = None
    channel: str | None = None
    explicit: bool = False


def parse_windows(text: str, data: dict[str, Any], p: OSData) -> OSData:
    """Populate an OSData instance with Windows-specific details."""
    tl = text.lower()

    p.vendor = "Microsoft"
    p.kernel_name = "nt"
    p.arch = extract_arch_from_text(tl)
    p.edition = _detect_edition(tl)

    product = _detect_product(tl)
    server_hint = _initial_server_hint(tl, product)
    state = _extract_version_state(tl)
    product, server_hint = _apply_build_context(state, product, server_hint)
    p.product = _finalize_product_label(tl, product, state, server_hint) or "Windows"

    defaults = PRODUCT_DEFAULTS.get(p.product or "")
    _apply_version_numbers(p, defaults, state)
    _set_kernel_version(p, defaults, state)
    _finalize_precision_and_confidence(p, state)

    if defaults is None and not state.explicit:
        p.kernel_name = None

    return p


def _detect_product(text: str) -> str | None:
    for product, patterns in WINDOWS_PRODUCT_PATTERNS:
        for token in patterns:
            if token in text:
                return product
    return None


def _initial_server_hint(tl: str, product: str | None) -> bool:
    """Return True when the banner or product implies a Windows Server build."""
    return "server" in tl or (product is not None and "server" in product.lower())


def _extract_version_state(text: str) -> VersionState:
    """Collect NT version, build, and patch information from the banner."""
    state = VersionState()

    best = _select_best_version(text)
    if best:
        state.nt_major, state.nt_minor, state.build, state.patch = best
        state.explicit = True

    nt_match = NT_PATTERN.search(text)
    if nt_match:
        maj = int(nt_match.group(1))
        minr = int(nt_match.group(2)) if nt_match.group(2) else 0
        if state.nt_major is None:
            state.nt_major = maj
            state.nt_minor = minr
        else:
            state.nt_minor = state.nt_minor if state.nt_minor is not None else minr
        state.explicit = True

    if state.nt_major is None:
        kernel_match = KERNEL_PATTERN.search(text)
        if kernel_match:
            state.nt_major = int(kernel_match.group(1))
            state.nt_minor = int(kernel_match.group(2)) if kernel_match.group(2) else 0
            state.explicit = True

    if state.build is None:
        build_match = BUILD_PATTERN.search(text)
        if build_match:
            state.build = str(int(build_match.group(1)))
            state.explicit = True

    return state


def _apply_build_context(state: VersionState, product: str | None, server_hint: bool) -> tuple[str | None, bool]:
    """Use build numbers to infer product/channel metadata and refine server hint."""
    build_num = int(state.build) if state.build and state.build.isdigit() else None
    if build_num is None:
        return product, server_hint

    product_from_build, channel, is_server_build = _lookup_build(build_num, server_hint)
    if product_from_build and (not product or _build_inference_should_replace(product, product_from_build)):
        product = product_from_build
    if is_server_build:
        server_hint = True
    state.channel = channel
    return product, server_hint


def _finalize_product_label(tl: str, product: str | None, state: VersionState, server_hint: bool) -> str | None:
    """Resolve the most precise product name available for the banner."""
    if product is None and state.nt_major is not None and state.nt_minor is not None:
        product = _product_from_nt(state.nt_major, state.nt_minor, server_hint)

    if product:
        sp_match = SP_PATTERN.search(tl)
        if sp_match and "windows 7" in product.lower():
            product = f"Windows 7 SP{sp_match.group(1)}"

    return product


def _apply_version_numbers(p: OSData, defaults: ProductDefaults | None, state: VersionState) -> None:
    """Move version components from the parse state into the OSData payload."""
    def pick(explicit: Any, fallback: Any) -> Any:
        return explicit if explicit is not None else fallback

    p.version_major = pick(state.nt_major, defaults.version_major if defaults else None)
    p.version_minor = pick(state.nt_minor, defaults.version_minor if defaults else None)
    p.version_patch = pick(state.patch, defaults.version_patch if defaults else None)
    p.version_build = pick(state.build, defaults.version_build if defaults else None)


def _set_kernel_version(p: OSData, defaults: ProductDefaults | None, state: VersionState) -> None:
    """Populate kernel_version using explicit tokens, build channel, or defaults."""
    kernel_version: str | None = None
    if (
        state.explicit
        and state.channel
        and (state.nt_major is None or state.nt_major >= 10)
        and (defaults is None or defaults.kernel_version is None)
    ):
        kernel_version = state.channel
    elif state.explicit and state.nt_major is not None:
        if state.nt_minor is not None:
            kernel_version = f"{state.nt_major}.{state.nt_minor}"
        elif state.nt_major >= 10 and state.channel:
            kernel_version = state.channel
    if kernel_version is None and defaults and defaults.kernel_version:
        kernel_version = defaults.kernel_version
    if kernel_version:
        p.kernel_version = kernel_version


def _finalize_precision_and_confidence(p: OSData, state: VersionState) -> None:
    """Derive precision/confidence and record evidence for explicit NT versions."""
    p.precision = _derive_precision(p.version_major, p.version_minor, p.version_patch, p.version_build)

    if (
        p.precision == PrecisionLevel.PRODUCT
        and p.version_major is None
        and p.version_minor is None
        and p.version_patch is None
        and p.version_build is None
    ):
        p.precision = PrecisionLevel.FAMILY

    if state.explicit and state.nt_major is not None:
        norm_major = min(10, state.nt_major)
        norm_minor = state.nt_minor if state.nt_minor is not None else 0
        p.evidence["nt_version"] = f"{norm_major}.{norm_minor}"

    update_confidence(p, p.precision)


def _detect_edition(tl: str) -> str | None:
    for token, label in EDITION_KEYWORDS:
        if token.strip() in {"pro", "home"}:
            pattern = rf"\b{token.strip()}\b"
            if re.search(pattern, tl):
                return label
        elif token in tl:
            return label
    return None


def _select_best_version(text: str) -> tuple[int, int, str | None, int | None] | None:
    best: tuple[int, int, str | None, int | None] | None = None
    best_score = -1
    for match in VERSION_PATTERN.finditer(text):
        major, minor, build, patch = match.groups()
        score = 2 if patch is not None else 1
        if score > best_score:
            best_score = score
            bpatch = int(patch) if patch is not None else None
            best = (int(major), int(minor), str(int(build)), bpatch)
    return best


def _lookup_build(build_num: int, server_hint: bool) -> tuple[str | None, str | None, bool]:
    candidate: tuple[str | None, str | None, bool] = (None, None, False)
    tables_to_try: list[tuple[int, int, str, str]] = []
    if server_hint:
        tables_to_try.extend(WINDOWS_SERVER_BUILD_MAP)
    tables_to_try.extend(WINDOWS_BUILD_MAP)
    for start, end, prod, channel in tables_to_try:
        if start <= build_num <= end:
            is_server = prod.lower().startswith("windows server")
            candidate = (prod, channel, is_server)
            break
    return candidate


def _build_inference_should_replace(existing: str, inferred: str) -> bool:
    """Return True when build metadata should override a detected product label."""
    existing_lower = existing.lower()
    inferred_lower = inferred.lower()

    if existing_lower == inferred_lower:
        return False
    if inferred_lower.startswith(existing_lower):
        return False
    return True


def _product_from_nt(major: int, minor: int, server_hint: bool) -> str | None:
    key = (major, minor)
    if server_hint and key in WINDOWS_NT_SERVER_MAP:
        return WINDOWS_NT_SERVER_MAP[key]
    return WINDOWS_NT_CLIENT_MAP.get(key)


def _derive_precision(
    major: int | None,
    minor: int | None,
    patch: int | None,
    build: str | None,
) -> PrecisionLevel:
    if build:
        return PrecisionLevel.BUILD
    if patch is not None and patch != 0:
        return PrecisionLevel.PATCH
    if minor is not None:
        return PrecisionLevel.MINOR
    if major is not None:
        return PrecisionLevel.MAJOR
    return PrecisionLevel.PRODUCT
