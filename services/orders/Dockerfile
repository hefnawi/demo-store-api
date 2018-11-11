FROM python:3.6-alpine

LABEL maintainer="Ahmed Hefnawi <me@ahmedhefnawi.com>"

WORKDIR /usr/src/app

ENV DEBUG=True \
    SECRET_KEY=zulu-alpha111 \
    JWT_ACCESS_LIFESPAN=24 \
    JWT_REFRESH_LIFESPAN=30

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .

EXPOSE 5000

CMD [ "python", "./api.py" ]
