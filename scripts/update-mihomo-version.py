#!/usr/bin/env python3
"""Read and update the pinned Mihomo release version.

The canonical version lives in a regular repository file rather than a
workflow file.  Keeping automated version commits away from
``.github/workflows`` lets the repository's ``GITHUB_TOKEN`` push the update
branch without requiring the unavailable ``workflows`` permission.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


VERSION_PATTERN = r"\d+\.\d+\.\d+"
VERSION_RE = re.compile(rf"^{VERSION_PATTERN}$")

VERSION_FILE = Path("mihomo-version.txt")
BUILD_SCRIPT = Path("build.sh")
README = Path("README.md")


def _read(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def _validate_version(version: str) -> tuple[int, int, int]:
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"unsupported Mihomo version: {version!r}")
    return tuple(int(part) for part in version.split("."))  # type: ignore[return-value]


def read_current(root: Path) -> str:
    version = _read(root, VERSION_FILE).strip()
    build_script = _read(root, BUILD_SCRIPT)
    readme = _read(root, README)

    _validate_version(version)
    if VERSION_FILE.name not in build_script:
        raise ValueError(f"{BUILD_SCRIPT} does not read the canonical {VERSION_FILE}")

    readme_versions = set(re.findall(r"(?<!\d)\d+\.\d+\.\d+(?!\d)", readme))
    if readme_versions != {version}:
        values = ", ".join(sorted(readme_versions)) or "none"
        raise ValueError(
            f"Mihomo version drift in {README}: expected {version}, found {values}"
        )
    return version


def update(root: Path, new_version: str) -> bool:
    new_parts = _validate_version(new_version)
    current = read_current(root)
    current_parts = _validate_version(current)
    if new_parts < current_parts:
        raise ValueError(
            f"refusing to downgrade Mihomo from {current} to {new_version}"
        )
    if new_version == current:
        return False

    version_path = root / VERSION_FILE
    version_path.write_text(f"{new_version}\n", encoding="utf-8")

    readme_path = root / README
    readme = readme_path.read_text(encoding="utf-8")
    readme, readme_count = re.subn(
        rf"(?<!\d){re.escape(current)}(?!\d)",
        new_version,
        readme,
    )
    if readme_count < 1:
        raise ValueError(f"failed to update {README}")
    readme_path.write_text(readme, encoding="utf-8")

    if read_current(root) != new_version:
        raise ValueError("version update did not leave the repository consistent")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the checkout containing this script)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--current", action="store_true")
    group.add_argument("--set", dest="new_version", metavar="VERSION")
    args = parser.parse_args()

    try:
        if args.current:
            print(read_current(args.root))
        else:
            changed = update(args.root, args.new_version)
            print("updated" if changed else "unchanged")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
