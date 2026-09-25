#!/usr/bin/env python3
"""Check whether the public GHCR tags for a Mihomo release are complete."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request


ACCEPT = ", ".join(
    (
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    )
)


def _request(url: str, headers: dict[str, str]) -> urllib.response.addinfourl:
    request = urllib.request.Request(url, headers=headers, method="GET")
    return urllib.request.urlopen(request, timeout=20)


def _registry_token(repository: str) -> str:
    query = urllib.parse.urlencode({"scope": f"repository:{repository}:pull"})
    with _request(f"https://ghcr.io/token?{query}", {}) as response:
        payload = json.load(response)
    token = payload.get("token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("GHCR token endpoint returned no token")
    return token


def _manifest_digest(repository: str, tag: str, token: str) -> str | None:
    url = (
        f"https://ghcr.io/v2/{repository}/manifests/{urllib.parse.quote(tag, safe='')}"
    )
    request = urllib.request.Request(
        url,
        headers={"Accept": ACCEPT, "Authorization": f"Bearer {token}"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            digest = response.headers.get("Docker-Content-Digest")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise
    if not digest:
        raise RuntimeError(f"GHCR returned no digest for {repository}:{tag}")
    return digest


def check(image: str, version: str) -> dict[str, object]:
    if "/" not in image:
        raise ValueError("image must include a registry and repository")
    registry, repository = image.split("/", 1)
    if registry != "ghcr.io":
        raise ValueError("this checker currently supports only ghcr.io images")

    token = _registry_token(repository)
    tags = (version, f"{version}-compatible", "latest")
    digests = {tag: _manifest_digest(repository, tag, token) for tag in tags}
    missing = [tag for tag, digest in digests.items() if digest is None]
    standard = digests[version]
    latest = digests["latest"]
    if standard and latest and standard != latest:
        missing.append("latest (stale)")
    return {
        "image": image,
        "version": version,
        "digests": digests,
        "missing": missing,
        "publish_needed": bool(missing),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="ghcr.io/ripples-alive/mihomo")
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.image, args.version), sort_keys=True))
    except (OSError, RuntimeError, ValueError, urllib.error.URLError) as error:
        print(f"image tag check unavailable: {error}", file=sys.stderr)
        # A failed inspection must not turn into a false no-op.  Let the caller
        # attempt a publish, which also provides a visible failure if GHCR is
        # unavailable.
        print(
            json.dumps(
                {
                    "image": args.image,
                    "version": args.version,
                    "digests": {},
                    "missing": ["inspection unavailable"],
                    "publish_needed": True,
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
