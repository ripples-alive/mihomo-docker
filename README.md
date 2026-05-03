# mihomo Docker image

This repository builds a Docker image for [MetaCubeX/mihomo](https://github.com/MetaCubeX/mihomo).

Images are published to GitHub Container Registry:

- `ghcr.io/ripples-alive/mihomo:1.19.21`
- `ghcr.io/ripples-alive/mihomo:1.19.21-compatible`
- `ghcr.io/ripples-alive/mihomo:latest`

The GHCR image name keeps the old Docker Hub image suffix from `ripples/mihomo`.

## Usage

```sh
docker run --rm \
  --name mihomo \
  --cap-add NET_ADMIN \
  --network host \
  -v /path/to/mihomo:/etc/mihomo \
  ghcr.io/ripples-alive/mihomo:1.19.21
```

Use the compatible build when needed:

```sh
docker run --rm \
  --name mihomo \
  --cap-add NET_ADMIN \
  --network host \
  -v /path/to/mihomo:/etc/mihomo \
  ghcr.io/ripples-alive/mihomo:1.19.21-compatible
```

If `/etc/mihomo` is empty, the container initializes it from
`ripples-alive/mihomo-proxy`.

## Builds

Local builds use `build.sh`, which pushes `ripples/mihomo:1.19.21` and
`ripples/mihomo:1.19.21-compatible` to Docker Hub for `linux/amd64`.

GitHub Actions builds the same Dockerfile with Buildx and publishes:

- `ghcr.io/ripples-alive/mihomo:1.19.21`
- `ghcr.io/ripples-alive/mihomo:1.19.21-compatible`
- `ghcr.io/ripples-alive/mihomo:latest`

Images are published on pushes to `main`, version tags such as `v1.19.21`, and
manual `workflow_dispatch` runs. Pull requests build the images for validation
but do not publish them.

To change the Mihomo source version used by GitHub Actions, update
`DEFAULT_MIHOMO_VERSION` in `.github/workflows/docker-image.yml`.
