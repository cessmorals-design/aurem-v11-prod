FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt
COPY..
ENV PYTHONUNBUFFERED=1
ENV PORT=10000
EXPOSE 10000
CMD ["gunicorn","-w","4","-b","0.0.0.0:10000","v11_max:app","--timeout","120"]
