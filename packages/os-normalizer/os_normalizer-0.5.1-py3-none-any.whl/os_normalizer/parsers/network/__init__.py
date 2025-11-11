"""Vendor-specific network OS parsers.

Each module exposes a vendor detection regex (or set) and a `parse_*`
function that mutates and returns an OSData instance.
"""

from .cisco import (
    CISCO_IOS_RE,
    CISCO_IOS_XE_RE,
    CISCO_NXOS_RE,
    parse_cisco,
)
from .juniper import JUNOS_RE, parse_juniper
from .fortinet import FORTI_RE, parse_fortinet
from .huawei import HUAWEI_RE, parse_huawei
from .netgear import NETGEAR_RE, parse_netgear

from os_normalizer.constants import OSFamily, PrecisionLevel
from os_normalizer.models import OSData

__all__ = [
    # Cisco
    "CISCO_IOS_RE",
    "CISCO_IOS_XE_RE",
    "CISCO_NXOS_RE",
    "parse_cisco",
    # Juniper
    "JUNOS_RE",
    "parse_juniper",
    # Fortinet
    "FORTI_RE",
    "parse_fortinet",
    # Huawei
    "HUAWEI_RE",
    "parse_huawei",
    # Netgear
    "NETGEAR_RE",
    "parse_netgear",
    # Orchestrator
    "parse_network",
]


def parse_network(text: str, data: dict | None, p: OSData) -> OSData:
    """Detect vendor and delegate to the correct parser."""
    tl = text.lower()
    if "cisco" in tl or CISCO_IOS_XE_RE.search(text) or CISCO_IOS_RE.search(text) or CISCO_NXOS_RE.search(text):
        return parse_cisco(text, p)
    if JUNOS_RE.search(text):
        return parse_juniper(text, p)
    if FORTI_RE.search(text):
        return parse_fortinet(text, p)
    if HUAWEI_RE.search(text):
        return parse_huawei(text, p)
    if NETGEAR_RE.search(text):
        return parse_netgear(text, p)

    # Unknown network vendor; keep coarse
    p.vendor = p.vendor or "Unknown-Network"
    p.product = p.product or "Network OS"
    if not isinstance(p.family, OSFamily):
        p.family = OSFamily(p.family) if p.family in OSFamily._value2member_map_ else None
    p.family = p.family or OSFamily.NETWORK
    p.precision = PrecisionLevel.FAMILY
    return p
