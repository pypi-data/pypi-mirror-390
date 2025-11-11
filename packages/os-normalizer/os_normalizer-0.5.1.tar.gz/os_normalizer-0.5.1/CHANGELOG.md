# Changelog

All notable changes to this project are documented here.
This file adheres to Keep a Changelog and Semantic Versioning.

## `v0.5.1` — [Unreleased]

- Added BSD parser support for `/etc/os-release` blobs (FreeBSD, OpenBSD, NetBSD) plus fixtures that lock codename/channel/distro handling.
- Normalized the hyphenated `x86-64` architecture alias to `x86_64` and added regression coverage in the Linux suite.
- Fixed Windows fallback parsing so bare “Windows” banners no longer crash, now emit family-level `OSData`, and keep kernel metadata unset when unknown.

## `v0.5.0` — [2025-10-30]

- Update release docs, add 3.14 classifier, sort imports [b7e07de]
- Add a ton more architectures and extract into constants [bd481f8]
- Add esxi and solaris support [8c14505]
- Set the unreleased tag for uv-ship [791361c]

## `v0.4.4` — [2025-10-25]

- Add uv-ship config [afd3bed]
- Merge pull request #2 from johnscillieri/codex/refactor-family-strings-into-constants [cf84c0f]
- Polish enum usage and update changelog [c3fb7f4]
- Merge pull request #1 from johnscillieri/codex/add-support-for-huawei-harmonyos [45fe0f9]
- Document HarmonyOS support addition [584ed2f]
- Added: HarmonyOS detection for Huawei devices, including dedicated parsing and metadata.
- Added: HarmonyOS normalization captures build identifiers (e.g., `5.0.0.107`) and propagates them into generated CPE data.
- Changed: Replaced string literals for OS families and precision tiers with shared enums and ordering constants across the normalization pipeline.

## [0.4.3] - 2025-10-20

- Fixed: Windows build parsing and inconsistent strings

## [0.4.2] - 2025-10-20

- Fixed: Windows product fingerprinting by build number

## [0.4.1] - 2025-09-25

- Added: Broadened Windows product aliases (e.g., Win11, Win2k) and recognized the macOS 26 codename `Tahoe`.
- Changed: Windows normalization now always fills NT version major/minor fields and treats marketing releases (21H2/24H2/etc.) as the kernel version for richer telemetry.
- Changed: Windows CPE generation derives release-channel tokens from build numbers so clients emit `windows_10_21h2`, `windows_11_24h2`, and similar slugs automatically.
- Fixed: Windows 11 and Server 2025 inputs no longer fall back to Windows 10 defaults, and legacy server builds keep their correct product names.
- Fixed: Windows `OSData` string formatting avoids duplicate fragments and skips redundant kernel numbers when printing friendly names.

## [0.4.0] - 2025-09-22

- Changed: Windows parser now normalizes typoed `windws` tokens, infers server editions from `Windows 2008/2012/2003` strings, and derives build numbers from generic `6.x.yyyy` patterns.
- Fixed: Windows Server 2012 R2 and older NT-based servers are correctly identified when only kernel/build identifiers are present.
- Fixed: OSData now always captures `kernel_version`/`version_build` for telemetry-only inputs.

## [0.3.4] - 2025-09-21

- Added: Extensive Windows kernel/build fixtures (e.g., `Windows 7601 6.1.7601 ...`) to lock in parsing of raw telemetry strings.
- Added: Coverage for Windows Server kernel identifiers to ensure server products are emitted with matching CPE metadata.
- Added: Regression tests for Redstone/Windows 10 marketing channels and mixed-case architecture tokens.

## [0.3.3] - 2025-09-21

- Added: `tests/case_utils.py` to share parametrization helpers across suites.
- Added: Platform-specific suites for clearer test changes.
- Removed: Legacy `tests/test_os_normalizer.py` harness now that coverage lives beside each platform.

## [0.3.2] - 2025-09-11

- Added: More `pyproject.toml` metadata (description, keywords, classifiers, project URLs).
- Added: `LICENSE` (MIT) and referenced it from project metadata.
- Added: `RELEASING.md` with step-by-step TestPyPI/PyPI instructions.
- Changed: Switched to Hatchling build backend via `[build-system]` in `pyproject.toml`.
- Changed: Exclude dev artifacts from sdist (`tests/`, caches, lockfiles, egg-info).

## [0.3.1] - 2025-09-09

- Added: Table printing of all OS values.

## [0.3.0] - 2025-09-09

- Added: Support merging in new data to combine observations.
- Added: Tests covering merge behavior.

## [0.2.0] - 2025-09-09

- Added: Additional `os_key` data for broader OS coverage.
- Changed: Improve Linux and macOS parsing; update BSD product extraction; better Windows version identification; fix Darwin kernel parsing.
- Changed: Break up network parsing into vendor-specific modules; general code cleanup; repo structure tidy-up.
- Changed: Rename `OSParse` to `OSData`; project renamed to `os_normalizer`.
- Changed: Adopt Ruff and reformat codebase; fix linter errors; improve test harness.
- Fixed: Failing tests (including `tests/test_full.py`).
- Removed: Old `Observation` class; now parse text and data directly.

## [0.1.0] - 2025-09-06

- Initial release.

[Unreleased]: https://github.com/johnscillieri/os-normalizer/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/johnscillieri/os-normalizer/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/johnscillieri/os-normalizer/compare/v0.3.4...v0.4.0
[0.3.4]: https://github.com/johnscillieri/os-normalizer/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/johnscillieri/os-normalizer/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/johnscillieri/os-normalizer/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/johnscillieri/os-normalizer/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/johnscillieri/os-normalizer/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/johnscillieri/os-normalizer/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/johnscillieri/os-normalizer/releases/tag/v0.1.0
