#INFORMATION
#MAINTAINER Julie Orjuela
#version="2.1"
#software="base dockerfile to launch pypi packages test"
#description="contains minimal dependencies for gitlab dojo test, updated for Ubuntu 24.04 and change apptainner instead of singularity"
FROM ubuntu:noble
USER root

# Set timezone and locale
ENV TZ=Europe/Paris
ENV DEBIAN_FRONTEND=noninteractive
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8

# Update and install base dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    locales \
    tzdata \
    git \
    vim \
    curl \
    wget \
    less \
    locate \
    openssh-server \
    software-properties-common \
    graphviz \
    build-essential \
    libssl-dev \
    uuid-dev \
    libgpgme11-dev \
    pkg-config \
    rsync \
    gzip \
    libcairo2-dev \
    libxt-dev \
    zlib1g-dev \
    cmake \
    cryptsetup \
    squashfs-tools \
    zip \
    util-linux \
    libbz2-dev \
    liblzma-dev \
    python3-all-dev \
    python3-pip \
    python3-venv \
    libseccomp-dev \
    libgpgme-dev \
    libassuan-dev \
    libbtrfs-dev \
    libdevmapper-dev \
    libfuse-dev \
    libfuse3-dev \
    libsqlite3-dev \
    libarchive-dev \
    libcurl4-openssl-dev \
    libssh-dev \
    libcrypto++-dev \
    libmicrohttpd-dev \
    libldns-dev \
    libuuid1 \
    autoconf \
    automake \
    libtool \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install Go (for Apptainer)
RUN wget https://go.dev/dl/go1.21.4.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.21.4.linux-amd64.tar.gz && \
    rm go1.21.4.linux-amd64.tar.gz
ENV PATH=/usr/local/go/bin:$PATH

# Install Apptainer dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libseccomp-dev \
    libglib2.0-dev \
    pkg-config \
    cryptsetup-bin \
    squashfs-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Apptainer from source
RUN wget https://github.com/apptainer/apptainer/releases/download/v1.2.5/apptainer-1.2.5.tar.gz && \
    tar -xzf apptainer-1.2.5.tar.gz && \
    rm apptainer-1.2.5.tar.gz
ENV PKG_CONFIG_PATH=/usr/lib/pkgconfig:/usr/lib/x86_64-linux-gnu/pkgconfig/
RUN cd /apptainer-1.2.5 && \
    ./mconfig -p /usr/local && \
    make -C builddir && \
    make -C builddir install || (cat builddir/config.log && exit 1)