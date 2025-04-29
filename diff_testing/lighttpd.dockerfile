FROM debian:stable-slim

# Install Lighttpd
RUN apt-get update \
 && apt-get install -y --no-install-recommends lighttpd \
 && rm -rf /var/lib/apt/lists/*

# Copy your local site/ directory into the default document root
COPY model_fs/ /var/www/html/

EXPOSE 80

# Run in the foreground
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]
