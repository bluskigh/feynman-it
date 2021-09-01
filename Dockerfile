FROM python:3
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN apt-get update
RUN apt-get install libmemcached-dev
RUN pip3 install -r requirements.txt 
CMD gunicorn feynmanit.wsgi
