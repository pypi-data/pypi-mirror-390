import copy
from collections.abc import Iterable
from dataclasses import fields, replace
from datetime import UTC, datetime
from typing import Any

from os_normalizer.constants import PRECISION_ORDER, OSFamily, PrecisionLevel
from os_normalizer.cpe import build_cpe23
from os_normalizer.helpers import extract_arch_from_text, precision_from_parts, update_confidence
from os_normalizer.models import OSData
from os_normalizer.parsers.bsd import parse_bsd
from os_normalizer.parsers.esxi import parse_esxi
from os_normalizer.parsers.linux import parse_linux
from os_normalizer.parsers.macos import parse_macos
from os_normalizer.parsers.mobile import parse_mobile
from os_normalizer.parsers.network import parse_network
from os_normalizer.parsers.solaris import parse_solaris
from os_normalizer.parsers.windows import parse_windows


# ============================================================
# Family detection (orchestrator logic)
# ============================================================
def detect_family(text: str, data: dict[str, Any]) -> tuple[OSFamily | None, float, dict[str, Any]]:
    t = text.lower()
    ev = {}
    if OSFamily.HARMONYOS.value in t:
        ev["hit"] = OSFamily.HARMONYOS
        return OSFamily.HARMONYOS, 0.6, ev
    # Obvious network signals first
    if any(
        x in t
        for x in [
            "cisco",
            "nx-os",
            "ios xe",
            "ios-xe",
            "junos",
            "fortios",
            "fortigate",
            "huawei",
            "vrp",
            "netgear",
            "firmware v",
        ]
    ):
        # Special handling for 'ios' - if it's just 'ios' without 'cisco', treat as mobile, not network
        if f"{OSFamily.IOS.value} " in t and "cisco" not in t:
            ev["hit"] = OSFamily.IOS
            return OSFamily.IOS, 0.6, ev

        ev["hit"] = OSFamily.NETWORK
        return OSFamily.NETWORK, 0.7, ev
    # VMware ESXi
    if "vmkernel" in t or "vmware esxi" in t or " esxi" in t or t.startswith("esxi"):
        ev["hit"] = OSFamily.ESXI
        return OSFamily.ESXI, 0.65, ev
    # Solaris / SunOS
    if "sunos" in t or "solaris" in t:
        ev["hit"] = OSFamily.SOLARIS
        return OSFamily.SOLARIS, 0.65, ev
    # Linux
    if OSFamily.LINUX.value in t or any(
        k in data for k in ("ID", "ID_LIKE", "PRETTY_NAME", "VERSION_ID", "VERSION_CODENAME")
    ):
        ev["hit"] = OSFamily.LINUX
        return OSFamily.LINUX, 0.6, ev
    # Windows
    if (
        OSFamily.WINDOWS.value in t
        or "nt " in t
        or t.startswith("win")
        or data.get("os", "").lower() == OSFamily.WINDOWS.value
    ):
        ev["hit"] = OSFamily.WINDOWS
        return OSFamily.WINDOWS, 0.6, ev
    # Apple
    if OSFamily.MACOS.value in t or "os x" in t or "darwin" in t:
        ev["hit"] = OSFamily.MACOS
        return OSFamily.MACOS, 0.6, ev
    if OSFamily.IOS.value in t or "ipados" in t:
        ev["hit"] = OSFamily.IOS
        return OSFamily.IOS, 0.6, ev
    # Android
    if OSFamily.ANDROID.value in t:
        ev["hit"] = OSFamily.ANDROID
        return OSFamily.ANDROID, 0.6, ev
    # BSD
    if "freebsd" in t or "openbsd" in t or "netbsd" in t:
        ev["hit"] = OSFamily.BSD
        return OSFamily.BSD, 0.6, ev
    return None, 0.0, ev


def normalize_os(text: str, data: dict | None = None) -> OSData:
    text = text.strip()
    data = data or {}
    t = text.lower()

    p = OSData()

    # Family detection
    fam, base_conf, ev = detect_family(t, data)
    p.family = fam
    p.confidence = max(p.confidence, base_conf)
    p.evidence.update(ev)

    if fam == OSFamily.NETWORK:
        p = parse_network(text, data, p)
    elif fam == OSFamily.WINDOWS:
        p = parse_windows(text, data, p)
    elif fam == OSFamily.MACOS:
        p = parse_macos(text, data, p)
    elif fam == OSFamily.LINUX:
        p = parse_linux(text, data, p)
    elif fam == OSFamily.SOLARIS:
        p = parse_solaris(text, data, p)
    elif fam == OSFamily.ESXI:
        p = parse_esxi(text, data, p)
    elif fam in (OSFamily.ANDROID, OSFamily.IOS, OSFamily.HARMONYOS):
        p = parse_mobile(text, data, p)
    elif fam == OSFamily.BSD:
        p = parse_bsd(text, data, p)
    else:
        p.precision = PrecisionLevel.UNKNOWN

    # Fallback arch from text if not already set elsewhere
    if not p.arch:
        p.arch = extract_arch_from_text(text)

    # Populate canonical os_key as CPE 2.3
    try:
        p.os_key = build_cpe23(p)
    except Exception:
        # Be resilient: leave unset on any unexpected error
        p.os_key = None

    return p


def choose_best_fact(candidates: list[OSData]) -> OSData:
    if not candidates:
        raise ValueError("No candidates")
    return sorted(
        candidates,
        key=lambda c: (PRECISION_ORDER.get(_ensure_precision_enum(c.precision), 0), c.confidence),
        reverse=True,
    )[0]


# ============================================================
# Merge/update APIs
# ============================================================


def _score(p: OSData) -> tuple[int, float]:
    return (PRECISION_ORDER.get(_ensure_precision_enum(p.precision), 0), p.confidence)


def _ensure_precision_enum(value: PrecisionLevel | str | None) -> PrecisionLevel:
    if isinstance(value, PrecisionLevel):
        return value
    if value is None:
        return PrecisionLevel.UNKNOWN
    try:
        return PrecisionLevel(str(value))
    except ValueError:
        return PrecisionLevel.UNKNOWN


def _union_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def merge_os(a: OSData, b: OSData, policy: str = "auto") -> OSData:
    """Merge two OSData objects into a new one.

    Default policy 'auto' keeps the base object with higher (precision, confidence)
    and fills missing details from the other. Conflicts are recorded under
    evidence['conflicts'] and evidence['alt'].
    """
    base, other = (a, b) if _score(a) >= _score(b) else (b, a)
    r = replace(base)

    # Ensure evidence containers exist
    r.evidence = dict(r.evidence or {})
    conflicts = dict(r.evidence.get("conflicts", {}))
    alts = dict(r.evidence.get("alt", {}))

    def fill(field: str) -> None:
        av = getattr(r, field)
        bv = getattr(other, field)
        if av is None and bv is not None:
            setattr(r, field, bv)
        elif bv is not None and av is not None and av != bv:
            # Conflict: keep current, store alternative
            alts[field] = bv
            conflicts[field] = [av, bv]

    # Identity & descriptive fields
    for f in (
        "family",
        "vendor",
        "product",
        "edition",
        "codename",
        "channel",
        "distro",
        "pretty_name",
        "kernel_name",
        "kernel_version",
        "arch",
        "hw_model",
        "build_id",
    ):
        fill(f)

    # kernel_version: prefer longer/more specific token when both present
    if base.kernel_version and other.kernel_version and len(other.kernel_version) > len(base.kernel_version):
        r.kernel_version = other.kernel_version

    # like_distros union
    if other.like_distros:
        r.like_distros = _union_unique([*(r.like_distros or []), *other.like_distros])

    # Version components: fill missing; record conflicts if both present and differ
    def choose_versions(x: OSData, y: OSData) -> tuple[str | None, int | None, int | None, int | None]:
        build = x.version_build or y.version_build
        maj = x.version_major if x.version_major is not None else y.version_major
        minr = x.version_minor if x.version_minor is not None else y.version_minor
        pat = x.version_patch if x.version_patch is not None else y.version_patch
        for name, xa, ya in (
            ("version_build", x.version_build, y.version_build),
            ("version_major", x.version_major, y.version_major),
            ("version_minor", x.version_minor, y.version_minor),
            ("version_patch", x.version_patch, y.version_patch),
        ):
            if xa is not None and ya is not None and xa != ya:
                conflicts[name] = [xa, ya]
        return build, maj, minr, pat

    vb, vmaj, vmin, vpat = choose_versions(base, other)
    r.version_build, r.version_major, r.version_minor, r.version_patch = vb, vmaj, vmin, vpat

    # Merge evidence (shallow)
    if other.evidence:
        r.evidence.update(other.evidence)

    # Precision & confidence: recompute based on version parts
    new_prec = precision_from_parts(r.version_major, r.version_minor, r.version_patch, r.version_build)
    if new_prec == PrecisionLevel.PRODUCT and not r.product:
        new_prec = PrecisionLevel.FAMILY if r.family else PrecisionLevel.UNKNOWN
    r.precision = new_prec
    r.confidence = max(a.confidence, b.confidence)
    update_confidence(r, r.precision)

    # Attach conflicts/alternates
    if conflicts:
        r.evidence["conflicts"] = conflicts
    if alts:
        r.evidence["alt"] = alts

    # Refresh CPE key
    try:
        r.os_key = build_cpe23(r)
    except Exception:
        r.os_key = None

    return r


def update_os(
    existing: OSData, text: str | None = None, data: dict | None = None, policy: str = "auto", inplace: bool = False
) -> OSData:
    """Parse new input, merge into existing OSData, and return the result.

    Set inplace=True to mutate the existing instance.
    """
    incoming = normalize_os(text or "", data or {}) if (text or data) else OSData()
    merged = merge_os(existing, incoming, policy=policy)
    if inplace:
        # Generic copy of dataclass fields with shallow copy for common containers
        for f in fields(OSData):
            val = getattr(merged, f.name)
            if isinstance(val, (dict, list, set)):
                val = copy.copy(val)
            setattr(existing, f.name, val)
        return existing
    return merged


if __name__ == "__main__":
    now = datetime.now(tz=UTC)
    samples = [
        {
            "text": "Windows NT 10.0 build 22631 Enterprise x64",
        },
        {
            "text": "Darwin 24.0.0; macOS Sequoia arm64",
        },
        {
            "text": "Linux host 5.15.0-122-generic x86_64",
            "data": {
                "os_release": 'NAME="Ubuntu"\nID=ubuntu\nVERSION_ID="22.04.4"\nVERSION_CODENAME=jammy\nPRETTY_NAME="Ubuntu 22.04.4 LTS"',
            },
        },
        {
            "text": "Cisco IOS XE Software, Version 17.9.4a (Amsterdam) C9300-24T, universalk9, c9300-universalk9.17.09.04a.SPA.bin",
        },
        {
            "text": "FortiGate-100F v7.2.7 build1600 (GA) FGT_7.2.7-build1600",
        },
        {
            "text": "Cisco Nexus Operating System (NX-OS) Software nxos.9.3.5.bin N9K-C93180YC-FX",
        },
        {
            "text": "Junos: 20.4R3-S3 jinstall-ex-4300-20.4R3-S3.tgz EX4300-48T",
        },
        {
            "text": "Huawei VRP V800R012C00SPC500 S5720-28X-SI-AC",
        },
        {
            "text": "NETGEAR Firmware V1.0.9.88_10.2.88 R7000",
        },
        {
            "text": "Darwin Mac-Studio.local 24.6.0 Darwin Kernel Version 24.6.0: Mon Jul 14 11:30:40 PDT 2025; root:xnu-11417.140.69~1/RELEASE_ARM64_T6041 arm64",
        },
    ]

    for s in samples:
        parsed = normalize_os(text=s.get("text"), data=s.get("data"))
        print("----", s.get("text"))
        print(parsed)
        print()
