"""
RabbitMQ client for Rating service to publish domain events.
"""

import aio_pika
import json
import os
from typing import Dict, Any


RABBITMQ_URL = os.getenv(
    "RABBITMQ_URL",
    "amqp://guest:guest@rabbitmq:5672/"
)


async def publish_event(event_type: str, event_data: Dict[str, Any]):
    """
    Publish a domain event to RabbitMQ.
    
    Args:
        event_type: Type of event (e.g., "rating.left")
        event_data: Event data dictionary
    """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        
        # Declare exchange
        exchange = await channel.declare_exchange(
            "rating_events",
            aio_pika.ExchangeType.TOPIC
        )
        
        # Publish event
        message_body = json.dumps(event_data).encode()
        await exchange.publish(
            aio_pika.Message(
                message_body,
                content_type="application/json",
                headers={"event_type": event_type}
            ),
            routing_key=event_type
        )
        
        await connection.close()
        print(f"Published event: {event_type}")
    except Exception as e:
        print(f"Error publishing event: {e}")

