#!/bin/sh

NAME=mihomo
BUILDER="${NAME}-builder"
SCRIPT_DIR=$(CDPATH=; cd -- "$(dirname -- "$0")" && pwd)
MIHOMO_VERSION=$(tr -d '\r\n' <"$SCRIPT_DIR/mihomo-version.txt")

docker buildx create --use --name "$BUILDER"
docker buildx inspect --bootstrap

docker buildx build \
    --platform linux/amd64 \
    --push \
    --pull \
    --tag "ripples/$NAME:$MIHOMO_VERSION" \
    --build-arg "MIHOMO_VERSION=$MIHOMO_VERSION" \
    --builder "$BUILDER" .

docker buildx build \
    --platform linux/amd64 \
    --push \
    --pull \
    --tag "ripples/$NAME:$MIHOMO_VERSION-compatible" \
    --build-arg "MIHOMO_VERSION=$MIHOMO_VERSION" \
    --build-arg MIHOMO_TAG=compatible \
    --builder "$BUILDER" .

docker buildx stop "$BUILDER"
docker buildx rm "$BUILDER"
