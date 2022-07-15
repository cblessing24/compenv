ARG BASE=ubuntu:22.04
FROM $BASE
# Fix for https://github.com/actions/virtual-environments/issues/2803
ENV LD_PRELOAD=/lib/x86_64-linux-gnu/libgcc_s.so.1
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update &&\
    apt-get install -y \
        curl \
        build-essential \
        git \
        python3-distutils \
        software-properties-common &&\
    add-apt-repository -y ppa:deadsnakes/ppa &&\
    apt-get update &&\
    apt-get install -y \
        python3.8 \
        python3.8-venv &&\
    rm -rf /var/lib/apt/lists/* &&\
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py &&\
    python3.8 get-pip.py &&\
    rm get-pip.py &&\
    python3.8 -m pip install --upgrade pip &&\
    python3.8 -m pip install pdm
ENV DEBIAN_FRONTEND=newt
WORKDIR src
COPY . .
ARG COMPENV_REF
LABEL compenv.ref=$COMPENV_REF
RUN pdm install --dev --no-lock
ENTRYPOINT ["pdm", "run"]
