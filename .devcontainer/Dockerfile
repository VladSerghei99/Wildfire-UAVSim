FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y

RUN apt install -y python3 python3-pip

RUN pip install mesa numpy matplotlib

# Add custom user "dev" with sudo permissions
RUN useradd dev -u 1000 -m -s /bin/bash && \
	echo "dev ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
USER dev
