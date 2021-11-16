FROM ubuntu:20.04

# Fix for https://github.com/actions/virtual-environments/issues/2803
ENV LD_PRELOAD=/lib/x86_64-linux-gnu/libgcc_s.so.1
ENV PATH="/home/dev/.local/bin:${PATH}"
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    python3.8 \
    python3.8-distutil \
    python3.8-dev \
    && rm -rf /var/lib/apt/lists/*
RUN useradd -m dev
USER dev
WORKDIR /home/dev
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.8 get-pip.py \
    && rm get-pip.py \
    && python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install pdm==1.10.2
COPY --chown=dev . reproducibility
WORKDIR reproducibility
RUN pdm sync -v
ENTRYPOINT ["pdm", "run"]
