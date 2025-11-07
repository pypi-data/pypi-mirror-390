FROM ubuntu:22.04

# User can change those variables to update the toolchain
ARG ARM_VERSION=10.3-2021.10
ARG ARM_PLATFORM=x86_64

# Install linux packages
RUN apt update \
    && apt install --no-install-recommends -y wget git tar build-essential cmake

# Installation directory for the ARM tools
ENV ARM_TOOLCHAIN_ROOT=/opt/arm_compiler
WORKDIR ${ARM_TOOLCHAIN_ROOT}

# Install GNU Arm Embedded Toolchain
RUN wget --no-check-certificate -c \
https://developer.arm.com/-/media/Files/downloads/gnu-rm/${ARM_VERSION}/gcc-arm-none-eabi-${ARM_VERSION}-${ARM_PLATFORM}-linux.tar.bz2

# Unpack the tarball to the install directory
RUN tar xjf gcc-arm-none-eabi-${ARM_VERSION}-${ARM_PLATFORM}-linux.tar.bz2

# Make accessible the toolchain anywhere
ENV PATH=$PATH:${ARM_TOOLCHAIN_ROOT}/gcc-arm-none-eabi-${ARM_VERSION}/bin

# Workspace directory
WORKDIR /workspace

# Start bash login shell
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/bin/bash", "-i"]
