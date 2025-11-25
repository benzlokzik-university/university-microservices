"""
Задание 2.3: Схема взаимодействия сервисов с нагрузкой
Тип обменника: topic
Символ для обозначения времени сна: -
Сообщения должны храниться при выключении RabbitMQ (durable)
"""

import asyncio
import sys
from aio_pika import connect_robust, ExchangeType, Message
from aio_pika.abc import AbstractConnection, AbstractChannel


EXCHANGE_NAME = "rent_events"
QUEUE_NAME = "rent_processor"
ROUTING_KEY = "rent.order.created"
SLEEP_SYMBOL = "-"
SLEEP_TIME = 1.5  # секунды


async def producer():
    """Производитель сообщений для topic exchange"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Создание durable topic exchange для событий аренды
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.TOPIC,
        durable=True,  # Exchange сохранится при перезапуске
    )

    # Создание durable очереди
    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True,  # Очередь сохранится при перезапуске
    )

    # Привязка очереди к exchange с routing_key pattern
    await queue.bind(exchange, routing_key=ROUTING_KEY)

    print(f"Producer: Topic exchange '{EXCHANGE_NAME}' создан (durable)")
    print(f"Producer: Очередь '{QUEUE_NAME}' создана (durable)")
    print(f"Producer: Routing key pattern: '{ROUTING_KEY}'")

    # Отправка сообщений с задержкой
    events = [
        ("rent.order.created", "Заказ создан"),
        ("rent.game.received", "Получение игры подтверждено"),
        ("rent.period.extended", "Срок аренды продлён"),
        ("rent.game.returned", "Игра возвращена"),
        ("rent.penalty.charged", "Штраф начислен"),
    ]

    for i, (routing_key, event) in enumerate(events, 1):
        message = f"{event} (сообщение {i})"
        await exchange.publish(
            Message(
                message.encode(),
                delivery_mode=2,  # Persistent сообщение
            ),
            routing_key=routing_key,
        )
        print(f"Producer: Отправлено - {message} (routing_key: {routing_key})")
        print(f"Producer: Сон {SLEEP_SYMBOL} на {SLEEP_TIME} секунд...")
        await asyncio.sleep(SLEEP_TIME)

    await connection.close()
    print("Producer: Завершен")


async def consumer():
    """Потребитель сообщений из topic exchange"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Убеждаемся, что exchange и очередь существуют
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, ExchangeType.TOPIC, durable=True
    )
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=ROUTING_KEY)

    async def process_message(message):
        async with message.process():
            print(f"Consumer: Получено - {message.body.decode()}")
            print(f"Consumer: Routing key: {message.routing_key}")
            print(f"Consumer: Сон {SLEEP_SYMBOL} на {SLEEP_TIME} секунд...")
            await asyncio.sleep(SLEEP_TIME)

    await queue.consume(process_message)

    print("Consumer: Ожидание сообщений. Для выхода нажмите Ctrl+C")
    try:
        await asyncio.Future()  # Бесконечное ожидание
    except KeyboardInterrupt:
        await connection.close()
        print("Consumer: Завершен")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "producer":
        asyncio.run(producer())
    elif len(sys.argv) > 1 and sys.argv[1] == "consumer":
        asyncio.run(consumer())
    else:
        print("Использование:")
        print("  python task2_topic.py producer  # Запустить производителя")
        print("  python task2_topic.py consumer  # Запустить потребителя")
