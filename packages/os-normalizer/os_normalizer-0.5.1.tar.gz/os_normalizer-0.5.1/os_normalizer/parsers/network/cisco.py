"""Cisco network OS parsing (IOS, IOS XE, NX-OS)."""

import re

from os_normalizer.constants import CISCO_TRAIN_NAMES, OSFamily, PrecisionLevel
from os_normalizer.helpers import update_confidence
from os_normalizer.models import OSData

# Detection and parsing regex
CISCO_IOS_XE_RE = re.compile(r"(ios[\s-]?xe)", re.IGNORECASE)
CISCO_IOS_RE = re.compile(r"\bios(?!\s?xe)\b", re.IGNORECASE)
CISCO_NXOS_RE = re.compile(r"\bnx-?os\b|\bNexus Operating System\b", re.IGNORECASE)
CISCO_VERSION_RE = re.compile(
    r"\bVersion\s+([0-9]+\.[0-9.()a-zA-Z]+)\b|\bnxos\.(\d+\.\d+(?:\.\d+|\(\d+\)))",
    re.IGNORECASE,
)
CISCO_IMAGE_RE = re.compile(r"\b([a-z0-9][a-z0-9_.-]+\.bin)\b", re.IGNORECASE)
CISCO_MODEL_RE = re.compile(
    r"\b(N9K-[A-Z0-9-]+|C\d{3,4}[\w-]+|ASR\d{3,4}[\w-]*|ISR\d{3,4}[\w/-]*|Catalyst\s?\d{3,4}[\w-]*)\b",
    re.IGNORECASE,
)
CISCO_EDITION_RE = re.compile(
    r"\b(universalk9|ipbase|adv(ip)?services|metroipaccess|securityk9|datak9)\b",
    re.IGNORECASE,
)


def parse_cisco(text: str, p: OSData) -> OSData:
    p.vendor = "Cisco"
    if not isinstance(p.family, OSFamily):
        p.family = OSFamily(p.family) if p.family in OSFamily._value2member_map_ else None
    p.family = p.family or OSFamily.NETWORK

    # Detect product line
    if CISCO_IOS_XE_RE.search(text):
        p.product, p.kernel_name = "IOS XE", "ios-xe"
    elif CISCO_NXOS_RE.search(text):
        p.product, p.kernel_name = "NX-OS", "nx-os"
    elif CISCO_IOS_RE.search(text):
        p.product, p.kernel_name = "IOS", "ios"
    else:
        p.product = p.product or "Cisco OS"

    # Version (Version X or nxos.X from text)
    vm = CISCO_VERSION_RE.search(text)
    if vm:
        ver = vm.group(1) or vm.group(2)
        if ver:
            p.evidence["version_raw"] = ver
            num = re.findall(r"\d+", ver)
            if len(num) >= 1:
                p.version_major = int(num[0])
            if len(num) >= 2:
                p.version_minor = int(num[1])
            if len(num) >= 3:
                p.version_patch = int(num[2])
            p.version_build = ver
            p.precision = (
                PrecisionLevel.PATCH
                if p.version_patch is not None
                else (PrecisionLevel.MINOR if p.version_minor is not None else PrecisionLevel.MAJOR)
            )

    # Image filename
    img = CISCO_IMAGE_RE.search(text)
    if img:
        p.build_id = img.group(1)
        p.precision = PrecisionLevel.BUILD

    # If NX-OS and only got version via filename, parse nxos.A.B.C.bin
    if not p.version_major and p.build_id:
        m = re.search(r"nxos\.(\d+)\.(\d+)\.(\d+)", p.build_id, re.IGNORECASE)
        if m:
            p.version_major = int(m.group(1))
            p.version_minor = int(m.group(2))
            p.version_patch = int(m.group(3))
            p.version_build = f"{p.version_major}.{p.version_minor}.{p.version_patch}"
            p.precision = PrecisionLevel.PATCH

    # Model
    mm = CISCO_MODEL_RE.search(text)
    if mm:
        p.hw_model = mm.group(1)

    # Edition (universalk9/ipbase)
    fl = CISCO_EDITION_RE.search(text)
    if fl:
        p.edition = fl.group(1).lower()

    # Train codename
    tl = text.lower()
    for train in CISCO_TRAIN_NAMES:
        if train.lower() in tl:
            p.codename = train
            break

    # Boost confidence based on precision
    update_confidence(
        p,
        p.precision if p.precision in (PrecisionLevel.BUILD, PrecisionLevel.PATCH) else PrecisionLevel.MINOR,
    )
    return p
