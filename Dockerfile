FROM python:3.9-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get -y install postgresql-client

RUN chmod +x entrypoint.sh

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
