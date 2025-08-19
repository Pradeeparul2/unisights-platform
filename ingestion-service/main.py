from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, HttpUrl, constr
from kafka import KafkaProducer
from kafka.errors import KafkaError
import geoip2.database
import json
import time
import logging
import os
from typing import Dict, List
from contextlib import asynccontextmanager
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from cipher import decrypt_payload
from kafka_setup import create_topic

from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app

# Allow CORS from 127.0.0.1:8080
origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",  # optional, if needed
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
]


# Global Kafka producer and readiness state
kafka_producer = None
producer_ready = False

UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Entering lifespan context")
    global kafka_producer, producer_ready
    logger.info("Application startup")
    max_retries = int(os.getenv("KAFKA_MAX_RETRIES", 5))
    retry_delay = int(os.getenv("KAFKA_RETRY_DELAY_SECONDS", 5))

    for attempt in range(max_retries):
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=os.getenv("KAFKA_BROKERS", "kafka:9092").split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
                batch_size=16384,
                linger_ms=10
            )

            # Create event topic if it doesn't exist
            create_topic(os.getenv("EVENT_TOPIC"), 1, 1)

            # Create stream topic if it doesn't exist
            create_topic(os.getenv("SESSION_TOPIC"), 1, 1)

            producer_ready = True
            logger.info(f"Kafka producer initialized on attempt {attempt + 1}")
            break
        except KafkaError as e:
            logger.error(f"Kafka initialization failed on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Kafka producer not initialized.")
                producer_ready = False
                raise Exception("Failed to initialize Kafka producer")

    yield

    if kafka_producer:
        kafka_producer.close()
        logger.info("Kafka producer closed")
    logger.info("Application shutdown")


app = FastAPI(title="Analytics Ingestion Service", 
              description="Service for ingesting analytics events and sending them to Kafka",
              version="1.0.0",
              lifespan=lifespan
              )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all (not recommended for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GeoIP database
try:
    geo_reader = geoip2.database.Reader(os.getenv("GEOIP_DB_PATH", "geo/GeoLite2-City.mmdb"))
    logger.info("GeoIP database loaded successfully")
except Exception as e:
    logger.error(f"Failed to load GeoIP database: {str(e)}")
    raise

# Pydantic models for payload validation
class EventData(BaseModel):
    type: str
    data: Dict

class Payload(BaseModel):
    data: str
    id: str

@app.post("/collect/events", status_code=202)
async def ingest_events(payload: Payload, request: Request):
    """Receive and process event payloads, sending to Kafka."""
    if not producer_ready or kafka_producer is None:
        logger.error("Kafka producer not initialized")
        raise HTTPException(status_code=503, detail="Kafka service unavailable")

    passphrase = os.getenv("ENCRYPTION_PASSPHRASE")
    salt = os.getenv("ENCRYPTION_SALT")
    # Check if encryption passphrase and salt are provided
    if passphrase is None or salt is None:
        raise HTTPException(status_code=500, detail="Encryption passphrase or salt not found")
    
    decrypted_payload = decrypt_payload(payload.data, payload.id, passphrase, salt)
    logger.info(f"Decrypted payload: {json.dumps(decrypted_payload, indent=2)}")
    try:
        # Enrich payload with metadata
        client_ip = request.client.host
        geo = None
        try:
            geo = geo_reader.city(client_ip)
        except geoip2.errors.AddressNotFoundError:
            logger.warning(f"GeoIP lookup failed for IP: {client_ip}")

        metadata = {
            "ip": client_ip,
            "geo": {
                "country": geo.country.iso_code if geo else None,
                "city": geo.city.name if geo else None,
                "lat": geo.location.latitude if geo else None,
                "lon": geo.location.longitude if geo else None
            },
            "received_at": int(time.time() * 1000),
            "user_agent": request.headers.get("user-agent")
        }
        
        # Validate that required fields exist
        if "events" not in decrypted_payload or not isinstance(decrypted_payload["events"], list):
            raise HTTPException(status_code=400, detail="Invalid or missing 'events' list")

        # Enrich base fields
        session_meta = {
            "asset_id": decrypted_payload.get("asset_id"),
            "session_id": decrypted_payload.get("session_id"),
            "page_url": decrypted_payload.get("page_url"),
            "entry_page": decrypted_payload.get("entry_page"),
            "exit_page": decrypted_payload.get("exit_page"),
            "scroll_depth": decrypted_payload.get("scroll_depth"),
            "time_on_page": decrypted_payload.get("time_on_page"),
            "device_type": decrypted_payload["device_info"].get("deviceType"),
            "os": decrypted_payload["device_info"].get("os"),
            "platform": decrypted_payload['device_info'].get("platform"),
            "screen_width": decrypted_payload['device_info'].get("screenWidth"),
            "screen_height": decrypted_payload["device_info"].get("screenHeight"),
            "utm_source": decrypted_payload["utm_params"].get("utm_source"),
            "utm_medium": decrypted_payload["utm_params"].get("utm_medium"),
            "utm_campaign": decrypted_payload["utm_params"].get("utm_campaign"),
            "utm_term": decrypted_payload["utm_params"].get("utm_term"),
            "utm_content": decrypted_payload["utm_params"].get("utm_content"),
            **metadata  # includes ip, geo, received_at, user_agent
        }

        # Publish each event separately
        for event in decrypted_payload["events"]:
            event_type = event.get("type")
            event_data = event.get("data", {})
            if not event_type or not isinstance(event_data, dict):
                logger.warning(f"Skipping invalid event: {event}")
                continue

            single_event_message = {
                "event_type": event_type,
                "event_data": event_data,
                "event_name": event_data.get("name"),  # e.g. button_click, FCP, TTFB, etc.
                "event_timestamp": event_data.get("timestamp"),
                **session_meta
            }

            kafka_producer.send(
                topic=os.getenv("EVENT_TOPIC"),  # or a separate topic like "event-stream"
                key=session_meta["asset_id"].encode("utf-8"),
                value=single_event_message
            )
            logger.debug(f"Published {event_type} event to Kafka for session {session_meta['asset_id']}")

        final_payload = {**decrypted_payload, **metadata}
        logger.info(f"Received payload: {json.dumps(final_payload, indent=2)}")
        kafka_producer.send(
                topic=os.getenv("SESSION_TOPIC"),
                key=final_payload["asset_id"].encode("utf-8"),
                value= session_meta
            )
        logger.debug(f"Published for session {session_meta['asset_id']} to Kafka")

        # # Publish each event to Kafka
        # for event in payload.events:
        #     event_message = {
        #         "timestamp": metadata["received_at"],
        #         "session_id": payload.session_id,
        #         "page_url": str(payload.page_url),
        #         "event_type": event.type,
        #         "event_data": event.data,
        #         "scroll_depth": payload.scroll_depth,
        #         "time_on_page": payload.time_on_page,
        #         **metadata
        #     }
        #     kafka_producer.send(
        #         topic=f"events.{event.type.lower()}",
        #         key=payload.session_id.encode("utf-8"),
        #         value=event_message
        #     )
        #     logger.debug(f"Published event {event.type} for session {payload.session_id} to Kafka")

        # Flush producer to ensure delivery
        kafka_producer.flush()
        logger.info(f"Successfully ingested events to Kafka for session {final_payload["session_id"]}")

        return {"status": "accepted"}
    except KafkaError as e:
        logger.error(f"Kafka ingestion failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Kafka service unavailable")
    except Exception as e:
        logger.error(f"Error processing payload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    if not producer_ready or kafka_producer is None:
        logger.error("Health check failed: Kafka producer not initialized")
        raise HTTPException(status_code=503, detail="Kafka service unavailable")

    try:
        # Send test message to health check topic
        kafka_producer.send(
            topic="health_check",
            value={"status": "ping", "timestamp": int(time.time() * 1000)}
        )
        kafka_producer.flush()
        logger.info("Health check passed")
        return {"status": "healthy", "kafka": "connected"}
    except KafkaError as e:
        logger.error(f"Health check failed: Kafka error - {str(e)}")
        raise HTTPException(status_code=503, detail=f"Kafka service unavailable")
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), lifespan="on")