"""Huawei VRP parsing."""

import re

from os_normalizer.constants import OSFamily, PrecisionLevel
from os_normalizer.helpers import update_confidence
from os_normalizer.models import OSData

HUAWEI_RE = re.compile(r"\bhuawei\b|\bvrp\b", re.IGNORECASE)
HUAWEI_VER_RE = re.compile(r"\bV(\d{3})R(\d{3})C(\d+)(SPC\d+)?\b", re.IGNORECASE)
HUAWEI_RAWVER_RE = re.compile(r"\bV\d{3}R\d{3}C\d+(?:SPC\d+)?\b", re.IGNORECASE)
HUAWEI_MODEL_RE = re.compile(r"\b(S\d{4}-\d{2}[A-Z-]+|CE\d{4}[A-Z-]*|AR\d{3,4}[A-Z-]*)\b", re.IGNORECASE)


def parse_huawei(text: str, p: OSData) -> OSData:
    p.vendor = "Huawei"
    p.product = "VRP"
    if not isinstance(p.family, OSFamily):
        p.family = OSFamily(p.family) if p.family in OSFamily._value2member_map_ else None
    p.family = p.family or OSFamily.NETWORK
    p.kernel_name = "vrp"

    raw = HUAWEI_RAWVER_RE.search(text)
    if raw:
        p.version_build = raw.group(0)

    vm = HUAWEI_VER_RE.search(text)
    if vm:
        maj, r, _c = vm.group(1), vm.group(2), vm.group(3)
        p.version_major = int(maj)
        p.version_minor = int(r)
        p.precision = PrecisionLevel.MINOR

    mdl = HUAWEI_MODEL_RE.search(text)
    if mdl:
        p.hw_model = mdl.group(1)

    p.build_id = p.version_build or p.build_id

    update_confidence(
        p,
        p.precision if p.precision in (PrecisionLevel.MINOR, PrecisionLevel.BUILD) else PrecisionLevel.MAJOR,
    )
    return p
