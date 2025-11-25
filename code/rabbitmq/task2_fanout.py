"""
Задание 2.1: Схема взаимодействия сервисов с нагрузкой
Тип обменника: fanout
Символ для обозначения времени сна: #
Сообщения должны храниться при выключении RabbitMQ (durable)
"""

import asyncio
import sys
from aio_pika import connect_robust, ExchangeType, Message
from aio_pika.abc import AbstractConnection, AbstractChannel


EXCHANGE_NAME = "game_catalog_events"
QUEUE_NAME = "game_catalog_listener"
SLEEP_SYMBOL = "#"
SLEEP_TIME = 2  # секунды


async def producer():
    """Производитель сообщений для fanout exchange"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Создание durable fanout exchange для событий каталога игр
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.FANOUT,
        durable=True,  # Exchange сохранится при перезапуске
    )

    # Создание durable очереди
    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True,  # Очередь сохранится при перезапуске
    )

    # Привязка очереди к exchange
    await queue.bind(exchange)

    print(f"Producer: Fanout exchange '{EXCHANGE_NAME}' создан (durable)")
    print(f"Producer: Очередь '{QUEUE_NAME}' создана (durable)")

    # Отправка сообщений с задержкой
    events = [
        "Игра добавлена в каталог",
        "Информация об игре обновлена",
        "Количество доступных к аренде игр обновлено",
        "Игра помечена как недоступная",
        "Фотографии игры загружены",
    ]

    for i, event in enumerate(events, 1):
        message = f"{event} (сообщение {i})"
        await exchange.publish(
            Message(
                message.encode(),
                delivery_mode=2,  # Persistent сообщение
            ),
            routing_key="",  # Для fanout routing_key игнорируется
        )
        print(f"Producer: Отправлено - {message}")
        print(f"Producer: Сон {SLEEP_SYMBOL} на {SLEEP_TIME} секунд...")
        await asyncio.sleep(SLEEP_TIME)

    await connection.close()
    print("Producer: Завершен")


async def consumer():
    """Потребитель сообщений из fanout exchange"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Убеждаемся, что exchange и очередь существуют
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, ExchangeType.FANOUT, durable=True
    )
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange)

    async def process_message(message):
        async with message.process():
            print(f"Consumer: Получено - {message.body.decode()}")
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
        print("  python task2_fanout.py producer  # Запустить производителя")
        print("  python task2_fanout.py consumer  # Запустить потребителя")
