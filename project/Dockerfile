FROM ubuntu:22.04

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    unzip \
    && ln -s /bin/python3 /usr/bin/python \
    && wget https://github.com/getgauge/gauge/releases/download/v1.6.20/gauge-1.6.20-linux.x86.zip\
    && unzip gauge-1.6.20-linux.x86.zip -d /usr/local/bin/ \
    && rm gauge-1.6.20-linux.x86.zip \
    && chmod +x /usr/local/bin/gauge \
    && pip install getgauge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip setuptools && \
    pip install -r requirements.txt
