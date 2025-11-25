"""
RabbitMQ client for Rent service to publish and consume domain events.
"""

import aio_pika
import json
import os
from typing import Dict, Any, Callable, Optional


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")


async def publish_event(event_type: str, event_data: Dict[str, Any]):
    """
    Publish a domain event to RabbitMQ.

    Args:
        event_type: Type of event (e.g., "rent.order.created")
        event_data: Event data dictionary
    """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        # Declare exchange
        exchange = await channel.declare_exchange(
            "rent_events", aio_pika.ExchangeType.TOPIC
        )

        # Publish event
        message_body = json.dumps(event_data).encode()
        await exchange.publish(
            aio_pika.Message(
                message_body,
                content_type="application/json",
                headers={"event_type": event_type},
            ),
            routing_key=event_type,
        )

        await connection.close()
        print(f"Published event: {event_type}")
    except Exception as e:
        print(f"Error publishing event: {e}")


async def consume_events(
    exchange_name: str,
    queue_name: str,
    routing_key: str,
    callback: Callable[[Dict[str, Any]], None],
):
    """
    Consume events from RabbitMQ.

    Args:
        exchange_name: Name of the exchange
        queue_name: Name of the queue
        routing_key: Routing key pattern
        callback: Callback function to process events
    """
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        # Declare exchange
        exchange = await channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC
        )

        # Declare queue
        queue = await channel.declare_queue(queue_name, durable=True)

        # Bind queue to exchange
        await queue.bind(exchange, routing_key=routing_key)

        # Consume messages
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        event_data = json.loads(message.body.decode())
                        callback(event_data)
                    except Exception as e:
                        print(f"Error processing event: {e}")

    except Exception as e:
        print(f"Error consuming events: {e}")
