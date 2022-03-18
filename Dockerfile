ARG base=ubuntu:20.04
FROM ${base}
# Fix for https://github.com/actions/virtual-environments/issues/2803
ENV LD_PRELOAD=/lib/x86_64-linux-gnu/libgcc_s.so.1
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    python3.8 \
    python3.8-distutil \
    python3.8-dev \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=newt
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.8 get-pip.py \
    && rm get-pip.py \
    && python3.8 -m pip install --upgrade pip &&\
    python3.8 -m pip install pdm
WORKDIR src
COPY . .
RUN pdm install --dev --no-lock
ENTRYPOINT ["pdm", "run"]
