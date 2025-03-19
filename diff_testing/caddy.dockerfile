FROM caddy:latest

# Copy your static files into the container
COPY model_fs/ /usr/share/caddy

# Copy Caddyfile (configuration for Caddy)
COPY Caddyfile /etc/caddy/Caddyfile

# Expose the default HTTP port
EXPOSE 80

# Start Caddy
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]