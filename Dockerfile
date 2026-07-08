FROM python:3.12-slim

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /src/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /src/