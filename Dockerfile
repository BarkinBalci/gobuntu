ARG UBUNTU_VERSION=26.04

FROM ubuntu:${UBUNTU_VERSION} AS go
ARG GO_VERSION=1.26

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        python3 \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/install-go.py /usr/local/bin/install-go.py
RUN chmod +x /usr/local/bin/install-go.py \
    && install-go.py "${GO_VERSION}" \
    && rm -f /usr/local/bin/install-go.py

FROM ubuntu:${UBUNTU_VERSION}
ARG SOURCE_REPOSITORY=https://github.com/local/gobuntu
ARG GO_TOOLS="golang.org/x/tools/gopls@latest golang.org/x/tools/cmd/goimports@latest"
ARG AGENT_USER=agent
ARG AGENT_GROUP=agent

LABEL org.opencontainers.image.title="gobuntu" \
      org.opencontainers.image.description="Rolling Ubuntu image for Go development tools" \
      org.opencontainers.image.source="${SOURCE_REPOSITORY}" \
      org.opencontainers.image.licenses="MIT"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    GOPATH=/go \
    GOBIN=/usr/local/bin \
    GOTOOLCHAIN=auto
ENV PATH=/usr/local/go/bin:/go/bin:/usr/local/bin:${PATH}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        cmake \
        curl \
        dnsutils \
        fd-find \
        file \
        gdb \
        git \
        iproute2 \
        iputils-ping \
        jq \
        lsof \
        make \
        openssh-client \
        pkg-config \
        procps \
        ripgrep \
    && ln -sf /usr/bin/fdfind /usr/local/bin/fd \
    && mkdir -p /workspace "${GOPATH}" \
    && rm -rf /var/lib/apt/lists/*

COPY --from=go /usr/local/go /usr/local/go
RUN for tool in ${GO_TOOLS}; do \
        go install "${tool}"; \
    done \
    && go clean -cache -modcache \
    && rm -rf /tmp/* /var/tmp/*

RUN groupadd --gid 0 --non-unique "${AGENT_GROUP}" \
    && useradd --uid 0 --non-unique --gid 0 --create-home --shell /bin/bash "${AGENT_USER}" \
    && chown -R "${AGENT_USER}:${AGENT_GROUP}" /workspace "${GOPATH}"

WORKDIR /workspace

USER ${AGENT_USER}

CMD ["bash"]
