FROM python:3.11-slim

WORKDIR /app

# Evitem buffering de logs
ENV PYTHONUNBUFFERED=1

# Instal·lar dependències de sistema mínimes (si calen per a torch)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8080
ENV PYTHONPATH=/app

CMD ["python", "triaxis/server.py"]
