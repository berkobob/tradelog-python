FROM python:3.8

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD admin.py .
ADD http.ini .

ADD src ./src

CMD ["uwsgi", "http.ini"]