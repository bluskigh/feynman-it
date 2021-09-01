FROM python:3
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN sudo apt-get install libmemcached-div
RUN pip3 install -r requirements.txt 
CMD gunicorn feynmanit.wsgi
