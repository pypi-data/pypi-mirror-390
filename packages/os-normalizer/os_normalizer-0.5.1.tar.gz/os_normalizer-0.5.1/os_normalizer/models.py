"""Data model definitions for OS fingerprinting."""

from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses import fields as dataclass_fields
from enum import Enum
from typing import Any

from .constants import OSFamily, PrecisionLevel


@dataclass
class OSData:
    """Structured representation of a parsed operating system."""

    # Core identity
    family: OSFamily | None = None  # windows, linux, macos, ios, android, bsd, solaris, esxi, network-os
    vendor: str | None = None  # Microsoft, Apple, Canonical, Cisco, Juniper, Fortinet, Huawei, Netgear…
    product: str | None = None  # Windows 11, Ubuntu, macOS, IOS XE, Junos, FortiOS, VRP, Firmware
    edition: str | None = None  # Pro/Enterprise/LTSC; universalk9/ipbase; etc.
    codename: str | None = None  # Sequoia; Ubuntu codename; Cisco train
    channel: str | None = None  # LTS/Beta/GA/R3-S3 etc.

    # Versions
    version_major: int | None = None
    version_minor: int | None = None
    version_patch: int | None = None
    version_build: str | None = None  # Windows build; network image tag

    # Kernel / image details
    kernel_name: str | None = None
    kernel_version: str | None = None
    arch: str | None = None
    distro: str | None = None
    like_distros: list[str] = field(default_factory=list)
    pretty_name: str | None = None

    # Network device extras
    hw_model: str | None = None
    build_id: str | None = None

    # Meta information
    precision: PrecisionLevel = PrecisionLevel.UNKNOWN  # family|product|major|minor|patch|build
    confidence: float = 0.0
    evidence: dict[str, Any] = field(default_factory=dict)

    # Canonical key for deduplication / indexing
    os_key: str | None = field(default=None, compare=False)

    def __str__(self) -> str:  # pragma: no cover - formatting helper
        parts: list[str] = []

        if self.family == OSFamily.WINDOWS:
            return _format_windows(self)

        # Prefer vendor + product; fallback to pretty_name; then family
        name_bits = [x for x in (self.vendor, self.product) if x]
        if name_bits:
            parts.append(" ".join(name_bits))
        elif self.pretty_name:
            parts.append(self.pretty_name)
        else:
            if isinstance(self.family, OSFamily):
                parts.append(self.family.value)
            else:
                parts.append(self.family or "Unknown OS")

        # Version string (major[.minor[.patch]]) and optional build
        ver_chunks: list[str] = []
        if self.version_major is not None:
            ver = str(self.version_major)
            if self.version_minor is not None:
                ver += f".{self.version_minor}"
                if self.version_patch is not None:
                    ver += f".{self.version_patch}"
            ver_chunks.append(ver)
        if self.version_build:
            ver_chunks.append(f"build {self.version_build}")
        if ver_chunks:
            parts.append(" ".join(ver_chunks))

        # Edition (e.g., Enterprise, LTSC)
        if self.edition:
            parts.append(self.edition)

        # Codename and/or channel in parentheses
        codchan = ", ".join([x for x in (self.codename, self.channel) if x])
        if codchan:
            parts.append(f"({codchan})")

        # Architecture
        if self.arch:
            parts.append(self.arch)

        # Kernel info
        kernel_bits = " ".join([x for x in (self.kernel_name, self.kernel_version) if x])
        if kernel_bits:
            parts.append(f"[kernel: {kernel_bits}]")

        # Hardware model (common for network devices)
        if self.hw_model:
            parts.append(f"[hw: {self.hw_model}]")

        # Separate build identifier if distinct from version_build
        if self.build_id and self.build_id != self.version_build:
            parts.append(f"[build: {self.build_id}]")

        # Precision/confidence summary
        if self.precision and self.precision != PrecisionLevel.UNKNOWN:
            label = self.precision.value if isinstance(self.precision, PrecisionLevel) else str(self.precision)
            parts.append(f"{{{label}:{self.confidence:.2f}}}")
        elif self.confidence:
            parts.append(f"{{{self.confidence:.2f}}}")

        return " ".join(parts)

    def __repr__(self) -> str:  # pragma: no cover - formatting helper
        # Delegate to __str__ for concise, human-friendly debug output
        return f"OSData({str(self)})"

    def full(self, none_str="<None>") -> str:  # pragma: no cover - formatting helper
        """Return all fields in a neat two-column, aligned layout.

        Example:
        family        : linux
        vendor        : Canonical
        ...
        If a field is None, prints "<None>" or none_val.
        """
        # Collect (name, value) pairs in declared order
        rows: list[tuple[str, str]] = []
        for f in dataclass_fields(self):
            name = f.name
            val = getattr(self, name)
            if val is None:
                sval = none_str
            elif name == "confidence" and isinstance(val, (int, float)):
                sval = f"{float(val):.2f}"
            elif isinstance(val, Enum):
                sval = val.value
            elif isinstance(val, list):
                sval = ", ".join(str(x) for x in val)
            elif isinstance(val, dict):
                # Shallow, compact dict repr with sorted keys for stability
                items = ", ".join(f"{k}={val[k]!r}" for k in sorted(val))
                sval = "{" + items + "}"
            else:
                sval = str(val)
            rows.append((name, sval))

        width = max(len(name) for name, _ in rows) if rows else 0
        lines = [f"{name:<{width}} : {sval}" for name, sval in rows]
        return "\n".join(lines)


def _format_windows(p: OSData) -> str:
    parts = [
        p.vendor,
        p.product,
        p.edition,
        p.codename,
        f"({p.kernel_version})" if p.kernel_version != f"{p.version_major}.{p.version_minor}" else "",
        f"{p.version_major}.{p.version_minor}.{p.version_build}",
        p.arch,
    ]
    return " ".join(part for part in parts if part)


if __name__ == "__main__":
    x = OSData(
        family=OSFamily.LINUX,
        vendor="Fedora Project",
        product="Fedora Linux",
        version_major=33,
        kernel_name="linux",
        kernel_version="5.4.0-70-generic",
        distro="fedora",
        like_distros=[],
        pretty_name="Fedora Linux",
        precision=PrecisionLevel.MAJOR,
        confidence=0.7,
        evidence={"hit": "linux"},
    )
    print("Normal:", x, "\nFull:", x.full(none_str=""), sep="\n", end="\n\n")
