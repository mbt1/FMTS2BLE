FROM mcr.microsoft.com/devcontainers/javascript-node:0-18

RUN apt-get update && \
    apt-get install -y qemu qemu-user-static binfmt-support && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY DockerPostCreate.sh /
RUN chmod +x /DockerPostCreate.sh
