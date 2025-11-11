"""Constants and static lookup tables for the OS fingerprinting package."""

from enum import StrEnum


class OSFamily(StrEnum):
    """Canonical OS family identifiers used throughout the project."""

    ANDROID = "android"
    BSD = "bsd"
    ESXI = "esxi"
    HARMONYOS = "harmonyos"
    IOS = "ios"
    LINUX = "linux"
    MACOS = "macos"
    NETWORK = "network-os"
    SOLARIS = "solaris"
    WINDOWS = "windows"


class PrecisionLevel(StrEnum):
    """Granularity levels for parsed OS version information."""

    UNKNOWN = "unknown"
    FAMILY = "family"
    PRODUCT = "product"
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    BUILD = "build"


PRECISION_ORDER = {
    PrecisionLevel.BUILD: 6,
    PrecisionLevel.PATCH: 5,
    PrecisionLevel.MINOR: 4,
    PrecisionLevel.MAJOR: 3,
    PrecisionLevel.PRODUCT: 2,
    PrecisionLevel.FAMILY: 1,
    PrecisionLevel.UNKNOWN: 0,
}


# Architecture tokens recognised across parsers.
ARCHITECTURE_TOKENS = (
    "x86_64",
    "amd64",
    "x64",
    "x86-64",
    "x86",
    "ia32",
    "i386",
    "i486",
    "i586",
    "i686",
    "arm64",
    "aarch64",
    "arm64e",
    "armv8",
    "armv8l",
    "arm",
    "armv7",
    "armv7l",
    "armv7hf",
    "armv6",
    "armhf",
    "armel",
    "ppc64le",
    "powerpc64le",
    "ppc64",
    "powerpc64",
    "ppc",
    "ppc32",
    "ppcle",
    "powerpc",
    "sparc",
    "sparc64",
    "sparcv9",
    "sun4u",
    "sun4v",
    "mips",
    "mips32",
    "mipsel",
    "mips64",
    "mips64el",
    "mips64le",
    "s390x",
    "s390",
    "riscv64",
    "riscv",
    "loongarch64",
    "tilegx",
    "alpha",
    "ia64",
    "itanium",
    "hppa",
    "parisc",
    "m68k",
)

# Architecture synonyms
ARCH_SYNONYMS = {
    "x86_64": "x86_64",
    "amd64": "x86_64",
    "x64": "x86_64",
    "x86-64": "x86_64",
    "x86": "x86",
    "ia32": "x86",
    "i386": "x86",
    "i486": "x86",
    "i586": "x86",
    "i686": "x86",
    "arm64": "arm64",
    "aarch64": "arm64",
    "arm64e": "arm64",
    "armv8": "arm64",
    "armv8l": "arm64",
    "arm": "arm",
    "armv7": "arm",
    "armv7l": "arm",
    "armv7hf": "arm",
    "armv6": "arm",
    "armhf": "arm",
    "armel": "arm",
    "ppc64le": "ppc64le",
    "powerpc64le": "ppc64le",
    "ppc64": "ppc64",
    "powerpc64": "ppc64",
    "ppc": "ppc",
    "ppc32": "ppc",
    "ppcle": "ppc",
    "powerpc": "ppc",
    "sparc": "sparc",
    "sparc64": "sparc",
    "sparcv9": "sparc",
    "sun4u": "sparc",
    "sun4v": "sparc",
    "mips": "mips",
    "mips32": "mips",
    "mipsel": "mips",
    "mips64": "mips64",
    "mips64el": "mips64",
    "mips64le": "mips64",
    "s390x": "s390x",
    "s390": "s390x",
    "riscv64": "riscv64",
    "riscv": "riscv64",
    "loongarch64": "loongarch64",
    "tilegx": "tilegx",
    "alpha": "alpha",
    "ia64": "ia64",
    "itanium": "ia64",
    "hppa": "parisc",
    "parisc": "parisc",
    "m68k": "m68k",
}

# Windows build map (build number range -> product name, marketing channel)
# Notes:
# - This focuses on common client builds; server detection is handled separately
#   and this map is not applied if a server product was already detected.
# - Marketing/channel labels use common public naming where applicable
#   (e.g., 21H2/22H2 for Windows 10/11, RTM/SPx for older releases).
WINDOWS_BUILD_MAP = [
    # NT era (pre-Windows 10)
    (1381, 1381, "Windows NT 4.0", "RTM"),
    (1998, 1998, "Windows 98", "RTM"),
    (2195, 2195, "Windows 2000", "RTM"),
    (2600, 2600, "Windows XP", "RTM"),
    (3000, 3000, "Windows Me", "RTM"),
    (3790, 3790, "Windows XP x64", "RTM"),
    # Vista/7/8/8.1
    (6000, 6000, "Windows Vista", "RTM"),
    (6001, 6001, "Windows Vista", "SP1"),
    (6002, 6002, "Windows Vista", "SP2"),
    (7600, 7600, "Windows 7", "RTM"),
    (7601, 7601, "Windows 7", "SP1"),
    (9200, 9200, "Windows 8", "RTM"),
    (9600, 9600, "Windows 8.1", "RTM"),
    # Windows 10 (builds and marketing versions)
    (10240, 10240, "Windows 10", "1507"),
    (10586, 10586, "Windows 10", "1511"),
    (14393, 14393, "Windows 10", "1607"),
    (15063, 15063, "Windows 10", "1703"),
    (16299, 16299, "Windows 10", "1709"),
    (17134, 17134, "Windows 10", "1803"),
    (17763, 17763, "Windows 10", "1809"),
    (18362, 18362, "Windows 10", "1903"),
    (18363, 18363, "Windows 10", "1909"),
    (19041, 19041, "Windows 10", "2004"),
    (19042, 19042, "Windows 10", "20H2"),
    (19043, 19043, "Windows 10", "21H1"),
    (19044, 19044, "Windows 10", "21H2"),
    (19045, 19045, "Windows 10", "22H2"),
    # Windows 11
    (22000, 22000, "Windows 11", "21H2"),
    (22621, 22621, "Windows 11", "22H2"),
    (22631, 25999, "Windows 11", "23H2"),
    (26100, 26199, "Windows 11", "24H2"),
]

# Windows Server build map (build number range -> product name, marketing channel)
# This is consulted only when the input looks server-like or when an explicit
# Windows Server product is already detected. Client mapping will not override
# explicit server detections.
WINDOWS_SERVER_BUILD_MAP = [
    # Legacy server releases aligned with Vista/7/8/8.1
    (3790, 3790, "Windows Server 2003", "RTM"),
    (6001, 6001, "Windows Server 2008", "RTM"),  # 6001 corresponds to 2008 RTM
    (6002, 6002, "Windows Server 2008", "SP2"),
    (7600, 7600, "Windows Server 2008 R2", "RTM"),
    (7601, 7601, "Windows Server 2008 R2", "SP1"),
    (9200, 9200, "Windows Server 2012", "RTM"),
    (9600, 9600, "Windows Server 2012 R2", "RTM"),
    # NT 10.0 based server releases
    (14393, 14393, "Windows Server 2016", "1607"),
    (17763, 17763, "Windows Server 2019", "1809"),
    (20348, 20348, "Windows Server 2022", "21H2"),
    # Windows Server 2025 (vNext) uses the 26100 train alongside client 24H2
    (26100, 26199, "Windows Server 2025", "24H2"),
]

# Windows NT version tuple -> client product (ambiguous NT 6.x split out)
WINDOWS_NT_CLIENT_MAP = {
    (4, 0): "Windows NT 4.0",
    (4, 10): "Windows 98",
    (4, 90): "Windows Me",
    (5, 0): "Windows 2000",
    (5, 1): "Windows XP",
    (5, 2): "Windows XP x64",
    (6, 0): "Windows Vista",
    (6, 1): "Windows 7",
    (6, 2): "Windows 8",
    (6, 3): "Windows 8.1",
    (10, 0): "Windows 10/11",
}

# Windows NT version tuple -> server product
WINDOWS_NT_SERVER_MAP = {
    (4, 0): "Windows NT 4.0 Server",
    (5, 0): "Windows 2000 Server",
    (5, 2): "Windows Server 2003",
    (6, 0): "Windows Server 2008",
    (6, 1): "Windows Server 2008 R2",
    (6, 2): "Windows Server 2012",
    (6, 3): "Windows Server 2012 R2",
    # NT 10.0: Server 2016/2019/2022 detected via explicit names, not NT mapping
}


WINDOWS_PRODUCT_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("Windows 11", ("windows 11", "win11")),
    ("Windows 10", ("windows 10", "win10")),
    ("Windows 8.1", ("windows 8.1", "win81")),
    ("Windows 8", ("windows 8", "win8")),
    ("Windows 7", ("windows 7", "win7")),
    ("Windows ME", ("windows me", "windows millenium")),
    ("Windows 98", ("windows 98", "win98")),
    ("Windows Server 2022", ("windows server 2022", "windows 2022", "win2k22", "win2022")),
    ("Windows Server 2019", ("windows server 2019", "windows 2019", "win2k19", "win2019")),
    ("Windows Server 2016", ("windows server 2016", "windows 2016", "win2k16", "win2016")),
    ("Windows Server 2012 R2", ("windows server 2012 r2", "windows 2012 r2", "win2k12r2", "win2012r2")),
    ("Windows Server 2012", ("windows server 2012", "windows 2012", "win2k12", "win2012")),
    ("Windows Server 2008 R2", ("windows server 2008 r2", "windows 2008 r2", "win2k8r2", "win2008r2")),
    ("Windows Server 2008", ("windows server 2008", "windows 2008", "win2k8", "win2008")),
    ("Windows Server 2003", ("windows server 2003", "windows 2003", "win2k3", "win2003")),
    ("Windows Server 2000", ("windows server 2000", "windows 2000", "win2k", "win2000")),
]


# Human readable aliases (macOS codenames)
MACOS_ALIASES = {
    "tahoe": "macOS 26",
    "sequoia": "macOS 15",
    "sonoma": "macOS 14",
    "ventura": "macOS 13",
    "monterey": "macOS 12",
    "big sur": "macOS 11",
    "bigsur": "macOS 11",
    "catalina": "macOS 10.15",
}

# macOS Darwin major version -> (product name, product version, codename)
MACOS_DARWIN_MAP = {
    19: ("macOS", "10.15", "Catalina"),
    20: ("macOS", "11", "Big Sur"),
    21: ("macOS", "12", "Monterey"),
    22: ("macOS", "13", "Ventura"),
    23: ("macOS", "14", "Sonoma"),
    24: ("macOS", "15", "Sequoia"),
    25: ("macOS", "26", "Tahoe"),
}

# Cisco train names (used for codename detection)
CISCO_TRAIN_NAMES = {"Everest", "Fuji", "Gibraltar", "Amsterdam", "Denali"}
