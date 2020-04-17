FROM python:3.7

RUN useradd tradelog \
 && mkdir /home/tradelog \
 && chown tradelog:tradelog /home/tradelog

ENV PATH="/home/tradelog/.local/bin:${PATH}"

USER tradelog

WORKDIR /home/tradelog

COPY . .

RUN pip3 install pipenv && pipenv install

CMD ["pipenv", "run", "uwsgi", "http.ini"]