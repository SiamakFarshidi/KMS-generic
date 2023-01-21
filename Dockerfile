FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt upgrade -y && apt install -y libenchant-2-2

COPY . ./KMS-generic
WORKDIR /KMS-generic

RUN python -m pip install --upgrade pip
RUN pip3 install -U pip

RUN pip3 install -r requirements.txt

RUN python -m spacy download en_core_web_md

CMD ["/bin/sh", "./django_app_setup.sh"]