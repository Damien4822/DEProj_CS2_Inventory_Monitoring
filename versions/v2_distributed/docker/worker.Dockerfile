FROM python:3.11-slim

WORKDIR /app

COPY worker/ ./worker
COPY queue/ ./queue
COPY storage/ ./storage

COPY worker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "worker/worker.py"]