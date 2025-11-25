"""
Задание 2.2: Схема взаимодействия сервисов с нагрузкой
Тип обменника: direct
Символ для обозначения времени сна: *
Сообщения могут не храниться при выключении RabbitMQ (non-durable)
"""

import asyncio
import sys
from aio_pika import connect_robust, ExchangeType, Message
from aio_pika.abc import AbstractConnection, AbstractChannel


EXCHANGE_NAME = "booking_events"
QUEUE_NAME = "booking_processor"
ROUTING_KEY = "game.booked"
SLEEP_SYMBOL = "*"
SLEEP_TIME = 1  # секунды


async def producer():
    """Производитель сообщений для direct exchange"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Создание non-durable direct exchange для событий бронирования
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.DIRECT,
        durable=False,  # Exchange НЕ сохранится при перезапуске
    )

    # Создание non-durable очереди с auto_delete
    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=False,  # Очередь НЕ сохранится при перезапуске
        auto_delete=True,  # Очередь удалится при отсутствии потребителей
    )

    # Привязка очереди к exchange с routing_key
    await queue.bind(exchange, routing_key=ROUTING_KEY)

    print(f"Producer: Direct exchange '{EXCHANGE_NAME}' создан (non-durable)")
    print(f"Producer: Очередь '{QUEUE_NAME}' создана (non-durable, auto-delete)")
    print(f"Producer: Routing key: '{ROUTING_KEY}'")

    # Отправка сообщений с задержкой
    events = [
        "Игра забронирована",
        "Бронирование отменено",
        "Бронирование подтверждено",
    ]

    for i, event in enumerate(events, 1):
        message = f"{event} (сообщение {i})"
        await exchange.publish(
            Message(
                message.encode(),
                delivery_mode=1,  # Non-persistent сообщение
            ),
            routing_key=ROUTING_KEY,
        )
        print(f"Producer: Отправлено - {message}")
        print(f"Producer: Сон {SLEEP_SYMBOL} на {SLEEP_TIME} секунд...")
        await asyncio.sleep(SLEEP_TIME)

    await connection.close()
    print("Producer: Завершен")


async def consumer():
    """Потребитель сообщений из direct exchange"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Убеждаемся, что exchange и очередь существуют
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, ExchangeType.DIRECT, durable=False
    )
    queue = await channel.declare_queue(QUEUE_NAME, durable=False, auto_delete=True)
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
        print("  python task2_direct.py producer  # Запустить производителя")
        print("  python task2_direct.py consumer  # Запустить потребителя")
