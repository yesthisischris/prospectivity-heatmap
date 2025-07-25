FROM mcr.microsoft.com/devcontainers/base:jammy

# Install system dependencies for geospatial libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
      libspatialindex-dev \
      libproj-dev \
      libgeos-dev \
      libgdal30 \
      && apt-get clean && rm -rf /var/lib/apt/lists/*

# UV is installed via devcontainer feature
# Python and GDAL are added via devcontainer features
