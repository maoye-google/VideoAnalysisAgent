FROM python:3.9-slim-buster

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY backend .

CMD ["python", "app.py"]