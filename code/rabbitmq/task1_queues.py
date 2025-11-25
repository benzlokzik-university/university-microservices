"""
Задание 1: Создание очередей RabbitMQ
- Эксклюзивная очередь
- Durable очередь
- Автоудаляемая очередь
"""

import asyncio
from aio_pika import connect_robust, ExchangeType, Message
from aio_pika.abc import AbstractConnection, AbstractChannel


async def create_exclusive_queue():
    """Создать эксклюзивную очередь для временных операций"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Эксклюзивная очередь для поиска игры (временная операция)
    queue = await channel.declare_queue(
        "game_search_temporary",
        exclusive=True,  # Очередь удалится при закрытии соединения
    )

    print("Эксклюзивная очередь 'game_search_temporary' создана")
    print("Очередь будет удалена при закрытии соединения")

    # Отправляем тестовое сообщение
    await channel.default_exchange.publish(
        Message("Тестовое сообщение для эксклюзивной очереди".encode("utf-8")),
        routing_key="game_search_temporary",
    )

    await asyncio.sleep(1)
    await connection.close()
    print("Соединение закрыто. Очередь удалена.")


async def create_durable_queue():
    """Создать durable очередь для регистрации пользователей"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Durable очередь для события "Пользователь зарегистрирован"
    queue = await channel.declare_queue(
        "user_registered",
        durable=True,  # Очередь сохранится при перезапуске RabbitMQ
    )

    print("Durable очередь 'user_registered' создана")
    print("Очередь будет сохранена при перезапуске сервера RabbitMQ")

    # Отправляем persistent сообщение
    await channel.default_exchange.publish(
        Message(
            "Пользователь зарегистрирован: user123".encode("utf-8"),
            delivery_mode=2,  # Persistent сообщение
        ),
        routing_key="user_registered",
    )

    print("Отправлено persistent сообщение")
    await connection.close()
    print(
        "Соединение закрыто. Очередь и сообщения останутся после перезапуска RabbitMQ."
    )


async def create_auto_delete_queue():
    """Создать автоудаляемую очередь для временных уведомлений"""
    connection: AbstractConnection = await connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel: AbstractChannel = await connection.channel()

    # Автоудаляемая очередь для временных уведомлений
    queue = await channel.declare_queue(
        "notification_temporary",
        auto_delete=True,  # Очередь удалится автоматически
    )

    print("Автоудаляемая очередь 'notification_temporary' создана")
    print("Очередь будет автоматически удалена, когда на ней не останется потребителей")

    # Создаем потребителя
    async def process_message(message):
        async with message.process():
            print(f"Получено сообщение: {message.body.decode()}")

    await queue.consume(process_message)

    # Отправляем тестовое сообщение
    await channel.default_exchange.publish(
        Message("Временное уведомление".encode("utf-8")),
        routing_key="notification_temporary",
    )

    print("Отправлено тестовое сообщение")
    await asyncio.sleep(2)

    await connection.close()
    print("Потребитель отключен. Очередь будет автоматически удалена.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Использование:")
        print("  python task1_queues.py exclusive   # Создать эксклюзивную очередь")
        print("  python task1_queues.py durable     # Создать durable очередь")
        print("  python task1_queues.py auto_delete # Создать автоудаляемую очередь")
        sys.exit(1)

    task = sys.argv[1]

    if task == "exclusive":
        asyncio.run(create_exclusive_queue())
    elif task == "durable":
        asyncio.run(create_durable_queue())
    elif task == "auto_delete":
        asyncio.run(create_auto_delete_queue())
    else:
        print(f"Неизвестная задача: {task}")
