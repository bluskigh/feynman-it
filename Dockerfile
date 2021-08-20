FROM python:3
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip3 install -r requirements.txt 
CMD gunicorn feynmanit.wsgi 
RUN python3 manage.py migrate 
