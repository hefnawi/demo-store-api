FROM python:3.6-alpine

LABEL maintainer="Ahmed Hefnawi <me@ahmedhefnawi.com>"

WORKDIR /usr/src/app

ENV DEBUG=True \
    SECRET_KEY=default-secret-key \
    ACCESS_EXPIRES=15 \
    REFRESH_EXPIRES=30

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api.py .

EXPOSE 5000

CMD ["gunicorn", "api:app", "-b", "0.0.0.0:5000"]
