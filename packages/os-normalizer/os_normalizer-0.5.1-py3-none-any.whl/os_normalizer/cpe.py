"""CPE 2.3 generation utilities for OSData.

This aims for pragmatic correctness for common operating systems based on
the fields present in OSData. Exact dictionary matching for all vendors
is out of scope; instead we provide a curated mapping for popular OSes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from os_normalizer.constants import OSFamily, WINDOWS_BUILD_MAP

if TYPE_CHECKING:
    from .models import OSData

_ESCAPE_CHARS = set("\\: ?*(){}[]!\"#$%&'+,/:;<=>@^`|~")


def _escape(s: str | None) -> str:
    if s is None:
        return "*"
    if s == "":
        return "-"
    if s in ("*", "-"):
        # Wildcard or N/A tokens are used verbatim in CPE
        return s
    out = []
    for ch in s:
        if ch in _ESCAPE_CHARS:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def _map_vendor_product(p: OSData) -> tuple[str, str, str]:
    """Return (vendor_token, product_token, strategy).

    strategy controls version/update selection rules.
    """
    raw_family = p.family
    family = (
        raw_family
        if isinstance(raw_family, OSFamily)
        else OSFamily._value2member_map_.get(str(raw_family).lower())
        if raw_family
        else None
    )
    vendor = (p.vendor or "").lower() if p.vendor else None
    product = (p.product or "").lower() if p.product else ""

    # Windows
    if family == OSFamily.WINDOWS:
        vtok = "microsoft"
        prod_map = {
            "windows 7": "windows_7",
            "windows 8.1": "windows_8.1",
            "windows 8": "windows_8",
            "windows 10": "windows_10",
            "windows 11": "windows_11",
            "windows server 2008": "windows_server_2008",
            "windows server 2008 r2": "windows_server_2008_r2",
            "windows server 2012": "windows_server_2012",
            "windows server 2012 r2": "windows_server_2012_r2",
            "windows server 2016": "windows_server_2016",
            "windows server 2019": "windows_server_2019",
            "windows server 2022": "windows_server_2022",
        }
        base = prod_map.get(product, "windows")
        if base in ("windows_10", "windows_11"):
            token = _windows_channel_token(p)
            if token:
                base = f"{base}_{token}"
        return vtok, base, "windows"

    # macOS
    if family == OSFamily.MACOS:
        return "apple", "macos", "macos"

    # Linux distros (use distro when present)
    if family == OSFamily.LINUX:
        d = (p.distro or "").lower()
        if d == "ubuntu":
            return "canonical", "ubuntu_linux", "ubuntu"
        if d == "debian":
            return "debian", "debian_linux", "debian"
        if d in ("rhel", "redhat", "red_hat"):
            return "redhat", "enterprise_linux", "rhel"
        if d in ("sles", "suse", "opensuse"):
            # Simplify to SLES when ID is sles; otherwise opensuse
            if d == "sles":
                return "suse", "linux_enterprise_server", "sles"
            return "suse", "opensuse", "opensuse"
        if d == "fedora":
            return "fedoraproject", "fedora", "fedora"
        if d in ("amzn", "amazon"):
            return "amazon", "amazon_linux", "amazon"
        # Generic Linux fallback
        return vendor or "linux", product or "linux", "linux"

    # BSDs
    if family == OSFamily.BSD:
        if product and "freebsd" in product:
            return "freebsd", "freebsd", "freebsd"
        if product and "openbsd" in product:
            return "openbsd", "openbsd", "openbsd"
        if product and "netbsd" in product:
            return "netbsd", "netbsd", "netbsd"
        return vendor or "bsd", product or "bsd", "bsd"

    if family == OSFamily.SOLARIS:
        return "oracle", "solaris", "solaris"

    if family == OSFamily.ESXI:
        return "vmware", "esxi", "esxi"

    # Network OS
    if family == OSFamily.NETWORK:
        if vendor == "cisco":
            if product and ("ios xe" in product or "ios-xe" in product):
                return "cisco", "ios_xe", "ios_xe"
            if product and ("nx-os" in product or "nxos" in product):
                return "cisco", "nx-os", "nx_os"
        if vendor == "juniper":
            return "juniper", "junos", "junos"
        if vendor == "fortinet":
            return "fortinet", "fortios", "fortios"
        if vendor == "huawei":
            return "huawei", "vrp", "vrp"
        if vendor == "netgear":
            return "netgear", "firmware", "firmware"
        return vendor or "network", (product or "firmware").replace(" ", "_"), "firmware"

    # Mobile
    if family == OSFamily.ANDROID:
        return "google", "android", OSFamily.ANDROID.value
    if family == OSFamily.IOS:
        return "apple", "iphone_os", OSFamily.IOS.value
    if family == OSFamily.HARMONYOS:
        return "huawei", "harmonyos", OSFamily.HARMONYOS.value

    # Fallback
    family_value = family.value if family else (str(raw_family).lower() if raw_family else "unknown")
    return (
        vendor or family_value or "unknown",
        (product or family_value).replace(" ", "_"),
        family_value,
    )


def _fmt_version(p: OSData, strategy: str) -> tuple[str, str, str]:
    """Return (version, update, edition) strings per strategy."""
    maj, minr, pat = p.version_major, p.version_minor, p.version_patch
    build = p.version_build
    edition = (p.edition or "").lower() if p.edition else None

    if strategy == "windows":
        patch = p.version_patch
        if p.version_major is not None and p.version_minor is not None:
            base = f"{p.version_major}.{p.version_minor}"
            if p.version_build:
                ver = f"{base}.{p.version_build}"
                if patch not in (None, 0):
                    ver = f"{ver}.{patch}"
            else:
                ver = base
                if patch not in (None, 0):
                    ver = f"{ver}.{patch}"
        elif p.version_build:
            ver = p.version_build
            if patch not in (None, 0):
                ver = f"{ver}.{patch}"
        else:
            ver = p.kernel_version or "*"
        return ver, "*", "*"

    if strategy == "ubuntu":
        if maj is not None and minr is not None:
            ver = f"{maj}.{minr:02d}"
        elif maj is not None:
            ver = f"{maj}.00"
        else:
            ver = "*"
        return ver, "*", "*"

    if strategy in ("debian", "rhel", "sles", "opensuse", "fedora", "amazon"):
        if maj is not None and minr is not None and strategy in ("opensuse",):
            ver = f"{maj}.{minr}"
        elif maj is not None:
            ver = str(maj)
        else:
            ver = "*"
        return ver, "*", "*"

    if strategy == "macos":
        ver = f"{maj}.{minr if minr is not None else 0}" if maj is not None else "*"
        return ver, "*", "*"

    if strategy in ("ios_xe", "nx_os", "junos"):
        # Prefer build if present; else compose from parts
        if build:
            ver = build.lower()
        elif maj is not None:
            if minr is not None and pat is not None:
                ver = f"{maj}.{minr}.{pat}"
            elif minr is not None:
                ver = f"{maj}.{minr}"
            else:
                ver = f"{maj}"
        else:
            ver = "*"
        return ver, "*", (edition or "*")

    if strategy in ("solaris", "esxi"):
        if maj is not None:
            ver = str(maj)
            if minr is not None:
                ver = f"{ver}.{minr}"
                if pat is not None:
                    ver = f"{ver}.{pat}"
        else:
            ver = "*"
        update = build or "*"
        return ver, update, "*"

    if strategy == "fortios":
        if maj is not None and minr is not None and pat is not None:
            ver = f"{maj}.{minr}.{pat}"
        elif build:
            # Fallback if only build available
            ver = build.split("+")[0]
        else:
            ver = "*"
        return ver, "*", "*"

    if strategy in ("vrp", "firmware"):
        if build:
            ver = build
        elif maj is not None:
            if minr is not None and pat is not None:
                ver = f"{maj}.{minr}.{pat}"
            elif minr is not None:
                ver = f"{maj}.{minr}"
            else:
                ver = f"{maj}"
        else:
            ver = "*"
        return ver, "*", "*"

    if strategy == "harmonyos":
        if maj is not None:
            if minr is not None and pat is not None:
                ver = f"{maj}.{minr}.{pat}"
            elif minr is not None:
                ver = f"{maj}.{minr}"
            else:
                ver = f"{maj}"
        else:
            ver = "*"
        update = build or "*"
        return ver, update, "*"

    # Generic fallback
    if build:
        ver = build
    elif maj is not None:
        if minr is not None and pat is not None:
            ver = f"{maj}.{minr}.{pat}"
        elif minr is not None:
            ver = f"{maj}.{minr}"
        else:
            ver = f"{maj}"
    else:
        ver = "*"
    return ver, "*", "*"


def _windows_channel_token(p: OSData) -> str | None:
    known_tokens = {
        "24h2",
        "23h2",
        "22h2",
        "21h2",
        "21h1",
        "20h2",
        "2004",
        "1909",
        "1903",
        "1809",
        "1803",
        "1709",
        "1703",
        "1607",
        "1511",
        "1507",
    }

    kv = (p.kernel_version or "").lower()
    if kv in known_tokens:
        return kv

    vb = p.version_build
    if vb and vb.isdigit():
        build = int(vb)
        for lo, hi, _product, marketing in WINDOWS_BUILD_MAP:
            if lo <= build <= hi and marketing:
                token = marketing.split('/')[-1].lower()
                if token:
                    return token

    return None


def _cpe_target_hw(arch: str | None) -> str:
    if not arch:
        return "*"
    a = arch.lower()
    if a in ("x86_64", "amd64"):
        return "x64"
    if a in ("x86", "i386", "i686"):
        return "x86"
    if a in ("arm64", "aarch64"):
        return "arm64"
    if a.startswith("arm"):
        return "arm"
    return a


def build_cpe23(p: OSData) -> str:
    """Build a cpe:2.3 string from an OSData instance."""
    part = "o"
    vendor, product, strategy = _map_vendor_product(p)
    version, update, edition = _fmt_version(p, strategy)

    # Always lower-case vendor/product tokens; keep version/update as-is case except we lowered some above
    vendor_token = _escape(vendor.lower())
    product_token = _escape(product.lower())
    version_token = _escape(version)
    update_token = _escape(update)
    edition_token = _escape(edition)

    fields = [
        "cpe:2.3",
        part,
        vendor_token,
        product_token,
        version_token,
        update_token,
        edition_token,
        "*",  # language
        "*",  # sw_edition
        "*",  # target_sw
        _escape(_cpe_target_hw(getattr(p, "arch", None))),  # target_hw
        "*",  # other
    ]
    return ":".join(fields)
