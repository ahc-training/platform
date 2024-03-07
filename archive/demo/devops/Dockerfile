FROM docker.io/apache/spark-py:latest

USER root

RUN apt-get update
RUN apt-get install -y --no-cache=true git-sync
RUN rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app

USER 185

COPY requirements.txt /tmp
RUN python3 -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt
