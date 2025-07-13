FROM phusion/baseimage:noble-1.0.2

ARG MIHOMO_VERSION
ARG MIHOMO_TAG

# Config timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
RUN ln -nsf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ >/etc/timezone

RUN sed -i 's/http:\/\/\(archive\|security\).ubuntu.com/https:\/\/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources

RUN apt-get update && apt-get install -y \
    curl \
    git \
    iproute2 \
    ipset \
    iptables \
    sudo \
    tzdata \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fSL https://github.com/MetaCubeX/mihomo/releases/download/v${MIHOMO_VERSION}/mihomo-linux-amd64${MIHOMO_TAG:+-${MIHOMO_TAG}}-v${MIHOMO_VERSION}.gz -o /tmp/mihomo.gz && \
    gunzip /tmp/mihomo.gz && \
    mv /tmp/mihomo /usr/bin/mihomo && \
    chmod +x /usr/bin/mihomo

COPY service /etc/service/mihomo
COPY rc.local /etc/rc.local
COPY cron /etc/cron.d/mihomo
