# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

RUN  apt-get update \
    && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

ENTRYPOINT ["python3", "./main.py"]
