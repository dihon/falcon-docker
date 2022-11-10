FROM python:alpine

EXPOSE 80

# Install gunicorn & falcon
RUN apk update
RUN apk add
RUN pip install gunicorn falcon requests falcon-cors
RUN apk add --update libmagic
#RUN apt-get install libmagic-dev
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add --no-cache mariadb-dev
RUN pip3 install mysqlclient 
RUN apk del build-deps
#python3-mysql.connector
RUN pip3 install python-magic
# Add demo app
COPY ./app /app
WORKDIR /app

CMD ["gunicorn", "-b", "0.0.0.0:80", "main:app"]
