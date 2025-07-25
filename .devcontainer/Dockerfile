FROM mcr.microsoft.com/devcontainers/base:jammy

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
      libspatialindex-dev \
      libproj-dev \
      libgeos-dev \
      && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Python and GDAL are added via devcontainer features
