# mihomo Docker image

This repository builds a Docker image for [MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo).

Images are published to GitHub Container Registry:

- `ghcr.io/ripples-alive/mihomo:1.19.31`
- `ghcr.io/ripples-alive/mihomo:1.19.31-compatible`
- `ghcr.io/ripples-alive/mihomo:latest`

The GHCR image name keeps the old Docker Hub image suffix from `ripples/mihomo`.

## Usage

```sh
docker run --rm \
  --name mihomo \
  --cap-add NET_ADMIN \
  --network host \
  -v /path/to/mihomo:/etc/mihomo \
  ghcr.io/ripples-alive/mihomo:1.19.31
```

Use the compatible build when needed:

```sh
docker run --rm \
  --name mihomo \
  --cap-add NET_ADMIN \
  --network host \
  -v /path/to/mihomo:/etc/mihomo \
  ghcr.io/ripples-alive/mihomo:1.19.31-compatible
```

If `/etc/mihomo` is empty, the container initializes it from
`ripples-alive/mihomo-proxy`.

## Builds

Local builds use `build.sh`, which pushes `ripples/mihomo:1.19.31` and
`ripples/mihomo:1.19.31-compatible` to Docker Hub for `linux/amd64`.

GitHub Actions builds the same Dockerfile with Buildx and publishes:

- `ghcr.io/ripples-alive/mihomo:1.19.31`
- `ghcr.io/ripples-alive/mihomo:1.19.31-compatible`
- `ghcr.io/ripples-alive/mihomo:latest`

Images are published on pushes to `main`, except pushes that change only
`.github/keepalive/**`, version tags such as `v1.19.31`, and manual
`workflow_dispatch` runs. Pull requests build the images for validation but do
not publish them. The scheduled keepalive commit only changes that excluded
path, so it does not rebuild or publish an unchanged image.

To change the Mihomo source version used by GitHub Actions, update
`DEFAULT_MIHOMO_VERSION` in `.github/workflows/docker-image.yml`.

## Automated stable updates

`Update Mihomo stable release` checks the upstream stable release every day at
03:17 UTC. When a newer release is available, it verifies the standard and
compatible amd64 assets, prepares a version-update commit on the dedicated
`automation/mihomo-stable` branch, and opens a PR. The updater only merges that
exact branch and commit when repository rules allow it; conflicts, required
reviews, or failed builds leave the PR open and fail the run for notification.
After a successful merge it publishes both GHCR tags and `latest`. It also
repairs missing or stale tags when the pinned version has not changed.

The repository Actions setting `Allow GitHub Actions to create and approve pull
requests` must be enabled once so the scheduled workflow can create its update
PRs with `GITHUB_TOKEN`.

## Keepalive

`Keep repository active` checks the age of the latest `main` commit every day.
When `main` has been quiet for 45 days, it writes a UTC timestamp to
`.github/keepalive/last-run` and pushes one commit. A newer Mihomo release or
any other normal commit resets the timer, so no keepalive commit is created
when the repository is already active.
