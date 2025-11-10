FROM registry.gitlab.com/hydroqc/hydroqc-base-container/3.13:latest

# Create devcontainer user with home directory and bash shell, install sudo, and configure passwordless sudo
RUN useradd -m -s /bin/bash devcontainer \
    && apt-get update && apt-get install -y sudo gnulib locales \
    && echo "devcontainer ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/devcontainer

WORKDIR /home/devcontainer
USER devcontainer
RUN mkdir -p /home/devcontainer/.local/bin \
    && export PATH=$PATH:/home/devcontainer/.local/bin
