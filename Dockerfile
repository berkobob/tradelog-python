FROM python:3.6

RUN pip install pipenv

RUN git clone -b docker https://github.com/berkobob/tradelog.git

WORKDIR /tradelog

RUN pipenv install

CMD ["pipenv", "run", "uwsgi", "http.ini"]