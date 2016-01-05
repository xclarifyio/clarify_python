FROM python:3
ADD . /data
WORKDIR /data
RUN python setup.py install
RUN python setup.py test
