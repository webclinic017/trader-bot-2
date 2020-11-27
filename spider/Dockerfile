FROM python:3.7-slim

RUN apt -y update && apt-get clean

RUN apt -y install libpq-dev python3.7-dev

COPY . /spider

WORKDIR /spider

RUN pip install -r /spider/requirements.txt

RUN ["chmod", "+x", "./docker-entrypoint.sh"]

ENTRYPOINT ["./docker-entrypoint.sh"]