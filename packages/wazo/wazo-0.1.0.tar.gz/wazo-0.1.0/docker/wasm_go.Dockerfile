# syntax=docker/dockerfile:1.4
FROM tinygo/tinygo:latest

LABEL maintainer="wazo"
LABEL description="Go WebAssembly builder using TinyGo"

WORKDIR /src
CMD ["tinygo", "version"]

