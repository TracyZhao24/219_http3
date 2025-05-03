# Dockerfile for H2O static file server
FROM ubuntu:22.04

# Install H2O
RUN apt-get update \
 && apt-get install -y --no-install-recommends h2o \
 && rm -rf /var/lib/apt/lists/*

# Copy config
COPY h2o.conf /etc/h2o/h2o.conf

# Copy site content
COPY model_fs/ /usr/share/h2o/htdocs/

EXPOSE 80

# Start H2O in foreground
CMD ["h2o", "-c", "/etc/h2o/h2o.conf"]
