FROM python:3.10-slim

WORKDIR /app

COPY server.py .

RUN pip install fastapi uvicorn websockets

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
