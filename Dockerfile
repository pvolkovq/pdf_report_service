FROM python:3.10.2

WORKDIR /usr/src/pdfserv

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && \
    apt-get -y install libc-dev build-essential python3 python3-pip

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/pdfserv/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/pdfserv/

RUN mkdir -p /usr/src/pdfserv

RUN playwright install chromium && playwright install-deps
