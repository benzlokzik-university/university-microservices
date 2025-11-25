#!/bin/bash

# Задание 1: Создание очередей

# 1. Создать эксклюзивную очередь для временных операций поиска игры
rabbitmqadmin declare queue name=game_search_temporary exclusive=true

# 2. Создать очередь, сохраняемую при перезапуске сервера RabbitMQ (durable)
# Очередь для события "Пользователь зарегистрирован"
rabbitmqadmin declare queue name=user_registered durable=true

# 3. Создать автоудаляемую очередь для временных уведомлений
rabbitmqadmin declare queue name=notification_temporary auto_delete=true

# Задание 2: Создание обменников и очередей для взаимодействия сервисов

# 1. Fanout exchange с durable сообщениями (символ сна: #)
# Обменник для событий каталога игр
rabbitmqadmin declare exchange name=game_catalog_events type=fanout durable=true
rabbitmqadmin declare queue name=game_catalog_listener durable=true
rabbitmqadmin declare binding source=game_catalog_events destination=game_catalog_listener

# 2. Direct exchange с non-durable сообщениями (символ сна: *)
# Обменник для событий бронирования
rabbitmqadmin declare exchange name=booking_events type=direct durable=false
rabbitmqadmin declare queue name=booking_processor durable=false auto_delete=true
rabbitmqadmin declare binding source=booking_events destination=booking_processor routing_key=game.booked

# 3. Topic exchange с durable сообщениями (символ сна: -)
# Обменник для событий аренды
rabbitmqadmin declare exchange name=rent_events type=topic durable=true
rabbitmqadmin declare queue name=rent_processor durable=true
rabbitmqadmin declare binding source=rent_events destination=rent_processor routing_key=rent.order.created

