FROM python:alpine

EXPOSE 80

# Install gunicorn & falcon
RUN pip install gunicorn falcon requests falcon-cors
RUN apk add --update libmagic
#RUN apt-get install libmagic-dev
RUN apt-get install python3-mysql.connector
RUN pip3 install python-magic
# Add demo app
COPY ./app /app
WORKDIR /app

CMD ["gunicorn", "-b", "0.0.0.0:80", "main:app"]
