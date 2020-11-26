FROM python:3.7-slim

RUN apt -y update && apt-get clean

WORKDIR /app

COPY . /app

RUN pip install -r /app/requirements.txt \
    rm -rf /root/.cache/pip

ENTRYPOINT ["/docker-entrypoint.sh"]