FROM debian:latest

# Install H2O
RUN apt-get update && apt-get install -y h2o && rm -rf /var/lib/apt/lists/*

# Create a directory for static files
RUN mkdir -p /var/www/html

# Copy static files into the container
COPY model_fs /var/www/html

# Create H2O configuration file
RUN mkdir -p /etc/h2o
COPY h2o.conf /etc/h2o/h2o.conf

# Expose the default H2O HTTP port
EXPOSE 80

# Command to run H2O with the specified configuration
CMD ["h2o", "-c", "/etc/h2o/h2o.conf"]
