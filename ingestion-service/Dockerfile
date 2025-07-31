FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies including curl
RUN apt-get update && apt-get install -y curl && apt-get clean

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Set environment variables
ENV KAFKA_BROKERS=localhost:9094 \
    GEOIP_DB_PATH=geo/GeoLite2-City.mmdb \
    PORT=8000 \
    ENCRYPTION_PASSPHRASE=insights-secret \
    ENCRYPTION_SALT=analytics-salt \
    EVENT_TOPIC=events-stream \
    SESSION_TOPIC=sessions-stream

# Expose port and run
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]