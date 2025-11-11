"""Netgear firmware parsing."""

import re

from os_normalizer.constants import OSFamily, PrecisionLevel
from os_normalizer.helpers import update_confidence
from os_normalizer.models import OSData

NETGEAR_RE = re.compile(r"\bnetgear\b|\bfirmware\b", re.IGNORECASE)
NETGEAR_VER_RE = re.compile(r"\bV(\d+\.\d+\.\d+(?:\.\d+)?(?:_\d+\.\d+\.\d+)?)\b", re.IGNORECASE)
NETGEAR_MODEL_RE = re.compile(r"\b([RN][0-9]{3,4}[A-Z]?)\b", re.IGNORECASE)


def parse_netgear(text: str, p: OSData) -> OSData:
    p.vendor = "Netgear"
    p.product = "Firmware"
    if not isinstance(p.family, OSFamily):
        p.family = OSFamily(p.family) if p.family in OSFamily._value2member_map_ else None
    p.family = p.family or OSFamily.NETWORK
    p.kernel_name = "firmware"

    vm = NETGEAR_VER_RE.search(text)
    if vm:
        v = vm.group(1)
        nums = re.findall(r"\d+", v)
        if nums:
            p.version_major = int(nums[0])
        if len(nums) >= 2:
            p.version_minor = int(nums[1])
        if len(nums) >= 3:
            p.version_patch = int(nums[2])
        p.version_build = v
        p.precision = (
            PrecisionLevel.PATCH
            if p.version_patch is not None
            else (PrecisionLevel.MINOR if p.version_minor is not None else PrecisionLevel.MAJOR)
        )

    mdl = NETGEAR_MODEL_RE.search(text)
    if mdl:
        p.hw_model = mdl.group(1)

    update_confidence(p, PrecisionLevel.MINOR if p.precision == PrecisionLevel.MAJOR else p.precision)
    return p
