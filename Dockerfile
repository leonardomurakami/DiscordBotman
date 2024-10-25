# BUILDER IMAGE
FROM golang:1.22 AS builder

RUN apt-get update && apt-get install -y ca-certificates openssl

ARG cert_location=/usr/local/share/ca-certificates
ENV SSL_CERT_DIR=/etc/ssl/certs
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

RUN openssl s_client -showcerts -connect github.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM > ${cert_location}/github.crt
RUN openssl s_client -showcerts -connect proxy.golang.org:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/proxy.golang.crt
RUN openssl s_client -showcerts -connect golang.org:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/golang.crt
RUN openssl s_client -showcerts -connect go.googlesource.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/go.googlesource.crt
RUN openssl s_client -showcerts -connect google.golang.org:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/google.golang.crt
RUN openssl s_client -showcerts -connect discord.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/discord.crt
RUN openssl s_client -showcerts -connect gateway.discord.gg:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/gateway.discord.crt
RUN openssl s_client -showcerts -connect youtube.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/youtube.crt
RUN openssl s_client -showcerts -connect twitch.tv:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/twitch.crt
RUN openssl s_client -showcerts -connect www.youtube.com:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/www.youtube.crt
RUN openssl s_client -showcerts -connect www.twitch.tv:443 </dev/null 2>/dev/null|openssl x509 -outform PEM >  ${cert_location}/www.twitch.crt
RUN update-ca-certificates

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# SERVICE
FROM scratch AS service

ARG DISCORD_BOT_TOKEN
ARG LAVALINK_SERVER_HOST
ARG LAVALINK_SERVER_PORT
ARG LAVALINK_SERVER_PASSWORD

ENV DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
ENV LAVALINK_SERVER_HOST=${LAVALINK_SERVER_HOST}
ENV LAVALINK_SERVER_PORT=${LAVALINK_SERVER_PORT}
ENV LAVALINK_SERVER_PASSWORD=${LAVALINK_SERVER_PASSWORD}

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/main .
ENTRYPOINT ["./main"]