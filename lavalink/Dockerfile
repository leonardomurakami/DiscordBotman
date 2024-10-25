FROM ghcr.io/lavalink-devs/lavalink:4.0.8

USER root

# Install certificates including Java certificates
RUN apt-get update && \
    apt-get install -y ca-certificates-java && \
    update-ca-certificates

# Configure Java to use the system truststore
ENV JAVA_OPTS="-Djavax.net.ssl.trustStore=/etc/ssl/certs/java/cacerts -Djavax.net.ssl.trustStorePassword=changeit"

USER lavalink