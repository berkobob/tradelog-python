FROM ubuntu:bionic

RUN apt update && apt upgrade -y && \
    apt install software-properties-common vim python3-pip git -y && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && apt install python3.7 -y

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN pip3 install pipenv

RUN git clone -b docker https://github.com/berkobob/tradelog.git

WORKDIR /tradelog

RUN pipenv install

CMD ["pipenv", "run", "uwsgi", "http.ini"]