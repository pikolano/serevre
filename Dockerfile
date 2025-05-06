FROM python:3.10-alpine

WORKDIR /app

COPY main.py .

RUN pip install --no-cache-dir fastapi uvicorn websockets

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]FROM python:3.10-slim

WORKDIR /app

COPY main.py .

RUN pip install fastapi uvicorn websockets

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
