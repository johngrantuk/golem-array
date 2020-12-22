FROM ubuntu:16.04

WORKDIR /golem/work

# COPY main.py .

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev


VOLUME /golem/work
