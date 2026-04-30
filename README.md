# gobuntu

[![CI](https://github.com/BarkinBalci/gobuntu/actions/workflows/ci.yml/badge.svg)](https://github.com/BarkinBalci/gobuntu/actions/workflows/ci.yml)

A downstream Ubuntu image for running Go coding agents in a container.

It gives agents a clean sandbox with Go, Git, search tools, and build/debug basics.

## Local Build

```sh
docker build --platform linux/amd64 --build-arg GO_VERSION=1.26 -t gobuntu:latest .
```

Run it with the current directory mounted at `/workspace`:

```sh
docker run --rm -it -v "$PWD:/workspace" -w /workspace gobuntu:latest
```