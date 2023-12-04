FROM python:3.12-alpine3.18

COPY requirements.txt /temp/requirements.txt

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password api-user
USER api-user

COPY myblog /myblog
WORKDIR /myblog
EXPOSE 8000
