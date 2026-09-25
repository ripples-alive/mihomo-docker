#!/usr/bin/env python3
"""Read and update the pinned Mihomo release version.

The repository intentionally keeps the version in the workflow, local build
script, and README examples.  This small helper keeps those copies in sync and
fails closed if a future manual edit introduces drift.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


VERSION_PATTERN = r"\d+\.\d+\.\d+"
VERSION_RE = re.compile(rf"^{VERSION_PATTERN}$")

WORKFLOW = Path(".github/workflows/docker-image.yml")
BUILD_SCRIPT = Path("build.sh")
README = Path("README.md")


def _read(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def _single_match(content: str, pattern: str, path: Path) -> str:
    matches = re.findall(pattern, content, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(
            f"expected one version declaration in {path}, found {len(matches)}"
        )
    return matches[0]


def _validate_version(version: str) -> tuple[int, int, int]:
    if not VERSION_RE.fullmatch(version):
        raise ValueError(f"unsupported Mihomo version: {version!r}")
    return tuple(int(part) for part in version.split("."))  # type: ignore[return-value]


def read_current(root: Path) -> str:
    workflow = _read(root, WORKFLOW)
    build_script = _read(root, BUILD_SCRIPT)
    readme = _read(root, README)

    workflow_version = _single_match(
        workflow,
        rf'^  DEFAULT_MIHOMO_VERSION: "({VERSION_PATTERN})"$',
        WORKFLOW,
    )
    build_version = _single_match(
        build_script,
        rf"^MIHOMO_VERSION=({VERSION_PATTERN})$",
        BUILD_SCRIPT,
    )
    _validate_version(workflow_version)
    _validate_version(build_version)
    if workflow_version != build_version:
        raise ValueError(
            "Mihomo version drift: "
            f"{WORKFLOW}={workflow_version}, {BUILD_SCRIPT}={build_version}"
        )

    readme_versions = set(re.findall(r"(?<!\d)\d+\.\d+\.\d+(?!\d)", readme))
    if readme_versions != {workflow_version}:
        values = ", ".join(sorted(readme_versions)) or "none"
        raise ValueError(
            f"Mihomo version drift in {README}: expected {workflow_version}, found {values}"
        )
    return workflow_version


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

    workflow_path = root / WORKFLOW
    workflow = workflow_path.read_text(encoding="utf-8")
    workflow, workflow_count = re.subn(
        rf'(^  DEFAULT_MIHOMO_VERSION: "){re.escape(current)}("$)',
        rf"\g<1>{new_version}\g<2>",
        workflow,
        count=1,
        flags=re.MULTILINE,
    )
    if workflow_count != 1:
        raise ValueError(f"failed to update {WORKFLOW}")
    workflow_path.write_text(workflow, encoding="utf-8")

    build_path = root / BUILD_SCRIPT
    build_script = build_path.read_text(encoding="utf-8")
    build_script, build_count = re.subn(
        rf"(^MIHOMO_VERSION=){re.escape(current)}$",
        rf"\g<1>{new_version}",
        build_script,
        count=1,
        flags=re.MULTILINE,
    )
    if build_count != 1:
        raise ValueError(f"failed to update {BUILD_SCRIPT}")
    build_path.write_text(build_script, encoding="utf-8")

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
