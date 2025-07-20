FROM mcr.microsoft.com/devcontainers/base:jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
      libspatialindex-dev \
      && apt-get clean && rm -rf /var/lib/apt/lists/*

# Python, GDAL and other libraries are added via devcontainer features
