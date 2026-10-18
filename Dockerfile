FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY v11_max.py .
COPY out/ ./out/

RUN mkdir -p out/admin

EXPOSE 10000

CMD gunicorn v11_max:app --bind 0.0.0.0:10000 --workers 1 --timeout 120
