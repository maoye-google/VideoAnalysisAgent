FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

CMD ["python", "app.py"]