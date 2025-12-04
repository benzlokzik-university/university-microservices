"""
FastAPI Gateway Service for Game Rental System

This is the main API Gateway that provides HTTP endpoints for all microservices.
It acts as a single entry point for external clients and routes requests to
appropriate backend services.

The gateway exposes OpenAPI documentation at /docs and /openapi.json
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from models import (
    # Game Catalog Models
    AddGameRequest,
    UpdateGameInfoRequest,
    UploadGamePhotosRequest,
    UpdateAvailableGamesRequest,
    SortGamesRequest,
    FindGameRequest,
    GameResponse,
    # Booking Models
    BookGameRequest,
    CancelBookingRequest,
    ConfirmBookingRequest,
    BookingResponse,
    # Rating Models
    LeaveRatingRequest,
    LeaveCommentRequest,
    UpdateGameRatingRequest,
    RatingResponse,
    CommentResponse,
    # User Account Models
    RegisterUserRequest,
    AuthorizeUserRequest,
    BlockUserRequest,
    UnblockUserRequest,
    UpdateUserProfileRequest,
    UserResponse,
    AuthResponse,
    # Rent Models
    CreateOrderRequest,
    SendPickupNotificationRequest,
    ConfirmGameReceiptRequest,
    SendReturnReminderRequest,
    ExtendRentalPeriodRequest,
    EndRentalPeriodRequest,
    ReturnGameRequest,
    ChargePenaltyRequest,
    ConfirmGameReturnRequest,
    OrderResponse,
    # Payment Models
    InitiatePaymentRequest,
    ProcessPaymentRequest,
    RequestRefundRequest,
    ProcessRefundRequest,
    DeclineRefundRequest,
    PaymentResponse,
    RefundResponse,
    # Common Models
    SuccessResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for the FastAPI application."""
    # Startup
    print("🚀 Gateway service starting up...")
    yield
    # Shutdown
    print("🛑 Gateway service shutting down...")


# Initialize FastAPI application
app = FastAPI(
    title="Game Rental System API Gateway",
    description="""
    API Gateway для системы аренды настольных игр.

    Этот сервис предоставляет единую точку входа для всех микросервисов системы:

    - **Каталог игр** - управление каталогом игр
    - **Бронирование** - управление бронированиями
    - **Оценка** - управление оценками и комментариями
    - **Аккаунт пользователя** - управление пользователями
    - **Аренда** - управление арендой игр
    - **Оплата** - управление платежами

    Все запросы проходят через этот шлюз и маршрутизируются к соответствующим микросервисам.
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Game Catalog Aggregate Endpoints
# ============================================================================


@app.post(
    "/api/v1/games",
    response_model=GameResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Game Catalog"],
    summary="Добавить игру в каталог",
    description="Создает новую игру в каталоге с указанными параметрами",
)
async def add_game(request: AddGameRequest):
    """
    Добавить игру в каталог.

    Создает новую запись об игре в системе с указанными характеристиками.
    После создания игры генерируется доменное событие "Игра добавлена в каталог".
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.put(
    "/api/v1/games/{game_id}",
    response_model=GameResponse,
    tags=["Game Catalog"],
    summary="Обновить информацию об игре",
    description="Обновляет информацию об существующей игре в каталоге",
)
async def update_game_info(game_id: str, request: UpdateGameInfoRequest):
    """
    Обновить информацию об игре.

    Обновляет параметры существующей игры. Можно обновить как все поля,
    так и только некоторые. После обновления генерируется доменное событие
    "Информация об игре обновлена".
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/games/{game_id}/photos",
    response_model=SuccessResponse,
    tags=["Game Catalog"],
    summary="Загрузить фотографии игры",
    description="Добавляет фотографии к игре в каталоге",
)
async def upload_game_photos(game_id: str, request: UploadGamePhotosRequest):
    """
    Загрузить фотографии игры.

    Добавляет URL фотографий к существующей игре. После загрузки
    генерируется доменное событие "Фотографии игры загружены".
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.patch(
    "/api/v1/games/{game_id}/availability",
    response_model=GameResponse,
    tags=["Game Catalog"],
    summary="Обновить количество доступных к аренде игр",
    description="Обновляет количество доступных экземпляров игры",
)
async def update_available_games(game_id: str, request: UpdateAvailableGamesRequest):
    """
    Обновить количество доступных к аренде игр.

    Изменяет количество доступных экземпляров игры. После обновления
    генерируется доменное событие "Количество доступных к аренде игр обновлено".
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/games/{game_id}/unavailable",
    response_model=SuccessResponse,
    tags=["Game Catalog"],
    summary="Пометить игру как недоступную",
    description="Помечает игру как недоступную для аренды",
)
async def mark_game_unavailable(game_id: str):
    """
    Пометить игру как недоступную.

    Изменяет статус игры на "недоступна". После изменения генерируется
    доменное событие "Игра помечена как недоступная".
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/games/sort",
    response_model=list[GameResponse],
    tags=["Game Catalog"],
    summary="Отсортировать игры",
    description="Возвращает отсортированный список игр",
)
async def sort_games(request: SortGamesRequest):
    """
    Отсортировать игры.

    Возвращает список игр, отсортированный по указанному полю и порядку.
    После сортировки генерируется доменное событие "Игры отсортированы".
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/games/search",
    response_model=list[GameResponse],
    tags=["Game Catalog"],
    summary="Найти игру",
    description="Выполняет поиск игр по заданным критериям",
)
async def find_game(request: FindGameRequest):
    """
    Найти игру.

    Выполняет поиск игр по различным критериям (название, категория, количество игроков и т.д.).
    После поиска генерируется доменное событие "Игра найдена" или "Игра не найдена".
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.get(
    "/api/v1/games/{game_id}",
    response_model=GameResponse,
    tags=["Game Catalog"],
    summary="Получить информацию об игре",
    description="Возвращает детальную информацию об игре",
)
async def get_game(game_id: str):
    """
    Получить информацию об игре.

    Возвращает полную информацию об игре по её идентификатору.
    """
    # TODO: Forward to game-catalog service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


# ============================================================================
# Booking Aggregate Endpoints
# ============================================================================


@app.post(
    "/api/v1/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Booking"],
    summary="Забронировать игру",
    description="Создает новое бронирование игры",
)
async def book_game(request: BookGameRequest):
    """
    Забронировать игру.

    Создает новое бронирование игры на указанную дату. После создания
    генерируется доменное событие "Игра забронирована".
    """
    # TODO: Forward to booking service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/bookings/{booking_id}/cancel",
    response_model=SuccessResponse,
    tags=["Booking"],
    summary="Отменить бронирование",
    description="Отменяет существующее бронирование",
)
async def cancel_booking(booking_id: str, request: CancelBookingRequest):
    """
    Отменить бронирование.

    Отменяет существующее бронирование. После отмены генерируется
    доменное событие "Бронирование отменено".
    """
    # TODO: Forward to booking service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/bookings/{booking_id}/confirm",
    response_model=BookingResponse,
    tags=["Booking"],
    summary="Подтвердить бронирование",
    description="Подтверждает существующее бронирование",
)
async def confirm_booking(booking_id: str, request: ConfirmBookingRequest):
    """
    Подтвердить бронирование.

    Подтверждает существующее бронирование. После подтверждения генерируется
    доменное событие "Бронирование подтверждено".
    """
    # TODO: Forward to booking service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.get(
    "/api/v1/bookings/{booking_id}",
    response_model=BookingResponse,
    tags=["Booking"],
    summary="Получить информацию о бронировании",
    description="Возвращает детальную информацию о бронировании",
)
async def get_booking(booking_id: str):
    """
    Получить информацию о бронировании.

    Возвращает полную информацию о бронировании по его идентификатору.
    """
    # TODO: Forward to booking service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


# ============================================================================
# Rating Aggregate Endpoints
# ============================================================================


@app.post(
    "/api/v1/ratings",
    response_model=RatingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Rating"],
    summary="Оставить оценку",
    description="Создает новую оценку игры",
)
async def leave_rating(request: LeaveRatingRequest):
    """
    Оставить оценку.

    Создает новую оценку игры от пользователя. После создания генерируется
    доменное событие "Оценка оставлена".
    """
    # TODO: Forward to rating service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Rating"],
    summary="Оставить комментарий",
    description="Создает новый комментарий к игре",
)
async def leave_comment(request: LeaveCommentRequest):
    """
    Оставить комментарий.

    Создает новый комментарий к игре от пользователя. Комментарий проходит
    модерацию через Perspective API. После создания генерируется доменное
    событие "Комментарий оставлен".
    """
    # TODO: Forward to rating service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.put(
    "/api/v1/games/{game_id}/rating",
    response_model=SuccessResponse,
    tags=["Rating"],
    summary="Обновить рейтинг игры",
    description="Обновляет средний рейтинг игры (системная команда)",
)
async def update_game_rating(game_id: str, request: UpdateGameRatingRequest):
    """
    Обновить рейтинг игры.

    Обновляет средний рейтинг игры на основе всех оценок. Это системная команда,
    которая вызывается автоматически при добавлении новой оценки. После обновления
    генерируется доменное событие "Рейтинг игры обновлён".
    """
    # TODO: Forward to rating service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


# ============================================================================
# User Account Aggregate Endpoints
# ============================================================================


@app.post(
    "/api/v1/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User Account"],
    summary="Зарегистрировать пользователя",
    description="Создает новый аккаунт пользователя",
)
async def register_user(request: RegisterUserRequest):
    """
    Зарегистрировать пользователя.

    Создает новый аккаунт пользователя в системе. После регистрации генерируется
    доменное событие "Пользователь зарегистрирован".
    """
    # TODO: Forward to user-account service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/users/authorize",
    response_model=AuthResponse,
    tags=["User Account"],
    summary="Авторизоваться",
    description="Выполняет авторизацию пользователя и возвращает токен доступа",
)
async def authorize_user(request: AuthorizeUserRequest):
    """
    Авторизоваться.

    Выполняет авторизацию пользователя по email и паролю. При успешной авторизации
    возвращает JWT токен доступа. Генерируется доменное событие "Пользователь авторизован".
    """
    # TODO: Forward to user-account service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/users/{user_id}/block",
    response_model=SuccessResponse,
    tags=["User Account"],
    summary="Заблокировать пользователя",
    description="Блокирует аккаунт пользователя",
)
async def block_user(user_id: str, request: BlockUserRequest):
    """
    Заблокировать пользователя.

    Блокирует аккаунт пользователя с указанием причины. После блокировки
    генерируется доменное событие "Пользователь заблокирован".
    """
    # TODO: Forward to user-account service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/users/{user_id}/unblock",
    response_model=SuccessResponse,
    tags=["User Account"],
    summary="Разблокировать пользователя",
    description="Разблокирует аккаунт пользователя",
)
async def unblock_user(user_id: str, request: UnblockUserRequest):
    """
    Разблокировать пользователя.

    Разблокирует ранее заблокированный аккаунт пользователя. После разблокировки
    генерируется доменное событие "Пользователь разблокирован".
    """
    # TODO: Forward to user-account service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.put(
    "/api/v1/users/{user_id}/profile",
    response_model=UserResponse,
    tags=["User Account"],
    summary="Обновить профиль пользователя",
    description="Обновляет информацию профиля пользователя",
)
async def update_user_profile(user_id: str, request: UpdateUserProfileRequest):
    """
    Обновить профиль пользователя.

    Обновляет информацию профиля пользователя (имя, фамилия, телефон).
    После обновления генерируется доменное событие "Профиль пользователя обновлен".
    """
    # TODO: Forward to user-account service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.get(
    "/api/v1/users/{user_id}",
    response_model=UserResponse,
    tags=["User Account"],
    summary="Получить информацию о пользователе",
    description="Возвращает детальную информацию о пользователе",
)
async def get_user(user_id: str):
    """
    Получить информацию о пользователе.

    Возвращает полную информацию о пользователе по его идентификатору.
    """
    # TODO: Forward to user-account service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


# ============================================================================
# Rent Aggregate Endpoints
# ============================================================================


@app.post(
    "/api/v1/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Rent"],
    summary="Создать заказ",
    description="Создает новый заказ на аренду игры",
)
async def create_order(request: CreateOrderRequest):
    """
    Создать заказ.

    Создает новый заказ на аренду игры на основе подтвержденного бронирования.
    После создания генерируется доменное событие "Заказ создан".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/pickup-notification",
    response_model=SuccessResponse,
    tags=["Rent"],
    summary="Отправить уведомление о дате и месте самовывоза",
    description="Отправляет уведомление пользователю о самовывозе",
)
async def send_pickup_notification(
    order_id: str, request: SendPickupNotificationRequest
):
    """
    Отправить уведомление о дате и месте самовывоза.

    Отправляет уведомление пользователю через OneSignal или SendGrid о дате
    и месте самовывоза игры. После отправки генерируется доменное событие
    "Уведомление о дате и месте самовывоза отправлено".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/confirm-receipt",
    response_model=SuccessResponse,
    tags=["Rent"],
    summary="Подтвердить получение игры",
    description="Подтверждает получение игры пользователем",
)
async def confirm_game_receipt(order_id: str, request: ConfirmGameReceiptRequest):
    """
    Подтвердить получение игры.

    Подтверждает, что пользователь получил игру. После подтверждения
    генерируется доменное событие "Получение игры подтверждено".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/return-reminder",
    response_model=SuccessResponse,
    tags=["Rent"],
    summary="Отправить напоминание о возврате",
    description="Отправляет напоминание пользователю о необходимости вернуть игру",
)
async def send_return_reminder(order_id: str, request: SendReturnReminderRequest):
    """
    Отправить напоминание о возврате.

    Отправляет напоминание пользователю через OneSignal или SendGrid о необходимости
    вернуть игру. После отправки генерируется доменное событие
    "Напоминание о возврате отправлено".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/extend",
    response_model=OrderResponse,
    tags=["Rent"],
    summary="Продлить срок аренды",
    description="Продлевает срок аренды игры",
)
async def extend_rental_period(order_id: str, request: ExtendRentalPeriodRequest):
    """
    Продлить срок аренды.

    Продлевает срок аренды игры на указанное количество дней. После продления
    генерируется доменное событие "Срок Аренды продлён".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/end",
    response_model=SuccessResponse,
    tags=["Rent"],
    summary="Завершить срок аренды",
    description="Завершает срок аренды (системная команда)",
)
async def end_rental_period(order_id: str, request: EndRentalPeriodRequest):
    """
    Завершить срок аренды.

    Завершает срок аренды игры. Это системная команда, которая вызывается
    автоматически при наступлении даты возврата. После завершения генерируется
    доменное событие "Срок аренды завершён".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/return",
    response_model=SuccessResponse,
    tags=["Rent"],
    summary="Вернуть игру",
    description="Инициирует процесс возврата игры",
)
async def return_game(order_id: str, request: ReturnGameRequest):
    """
    Вернуть игру.

    Инициирует процесс возврата игры пользователем. После возврата
    генерируется доменное событие "Игра возвращена".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/penalty",
    response_model=SuccessResponse,
    tags=["Rent"],
    summary="Начислить штраф",
    description="Начисляет штраф за просрочку возврата",
)
async def charge_penalty(order_id: str, request: ChargePenaltyRequest):
    """
    Начислить штраф.

    Начисляет штраф за просрочку возврата игры. После начисления
    генерируется доменное событие "Штраф начислен".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/orders/{order_id}/confirm-return",
    response_model=SuccessResponse,
    tags=["Rent"],
    summary="Подтвердить возврат игры",
    description="Подтверждает возврат игры и завершает аренду",
)
async def confirm_game_return(order_id: str, request: ConfirmGameReturnRequest):
    """
    Подтвердить возврат игры.

    Подтверждает возврат игры и завершает процесс аренды. После подтверждения
    генерируется доменное событие "Возврат игры подтвержден".
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.get(
    "/api/v1/orders/{order_id}",
    response_model=OrderResponse,
    tags=["Rent"],
    summary="Получить информацию о заказе",
    description="Возвращает детальную информацию о заказе",
)
async def get_order(order_id: str):
    """
    Получить информацию о заказе.

    Возвращает полную информацию о заказе по его идентификатору.
    """
    # TODO: Forward to rent service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


# ============================================================================
# Payment Aggregate Endpoints
# ============================================================================


@app.post(
    "/api/v1/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Payment"],
    summary="Инициировать платёж",
    description="Создает новый платеж для заказа",
)
async def initiate_payment(request: InitiatePaymentRequest):
    """
    Инициировать платёж.

    Создает новый платеж для указанного заказа. После создания
    генерируется доменное событие "Платёж инициирован".
    """
    # TODO: Forward to payment service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/payments/{payment_id}/process",
    response_model=PaymentResponse,
    tags=["Payment"],
    summary="Произвести оплату",
    description="Обрабатывает платеж через платежную систему",
)
async def process_payment(payment_id: str, request: ProcessPaymentRequest):
    """
    Произвести оплату.

    Обрабатывает платеж через платежную систему (Эквайринг). После обработки
    генерируется доменное событие "Оплата успешно проведена" или "Оплата отклонена".
    """
    # TODO: Forward to payment service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/refunds",
    response_model=RefundResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Payment"],
    summary="Запросить возврат средств",
    description="Создает запрос на возврат средств",
)
async def request_refund(request: RequestRefundRequest):
    """
    Запросить возврат средств.

    Создает запрос на возврат средств для указанного платежа. После создания
    генерируется доменное событие "Запрос на возврат средств создан".
    """
    # TODO: Forward to payment service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/refunds/{refund_id}/process",
    response_model=RefundResponse,
    tags=["Payment"],
    summary="Произвести возврат средств",
    description="Обрабатывает возврат средств через платежную систему",
)
async def process_refund(refund_id: str, request: ProcessRefundRequest):
    """
    Произвести возврат средств.

    Обрабатывает возврат средств через платежную систему. После обработки
    генерируется доменное событие "Возврат средств выполнен".
    """
    # TODO: Forward to payment service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.post(
    "/api/v1/refunds/{refund_id}/decline",
    response_model=SuccessResponse,
    tags=["Payment"],
    summary="Отклонить возврат средств",
    description="Отклоняет запрос на возврат средств",
)
async def decline_refund(refund_id: str, request: DeclineRefundRequest):
    """
    Отклонить возврат средств.

    Отклоняет запрос на возврат средств с указанием причины. После отклонения
    генерируется доменное событие "Возврат средств отклонен".
    """
    # TODO: Forward to payment service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.get(
    "/api/v1/payments/{payment_id}",
    response_model=PaymentResponse,
    tags=["Payment"],
    summary="Получить информацию о платеже",
    description="Возвращает детальную информацию о платеже",
)
async def get_payment(payment_id: str):
    """
    Получить информацию о платеже.

    Возвращает полную информацию о платеже по его идентификатору.
    """
    # TODO: Forward to payment service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


@app.get(
    "/api/v1/refunds/{refund_id}",
    response_model=RefundResponse,
    tags=["Payment"],
    summary="Получить информацию о возврате",
    description="Возвращает детальную информацию о возврате средств",
)
async def get_refund(refund_id: str):
    """
    Получить информацию о возврате.

    Возвращает полную информацию о возврате средств по его идентификатору.
    """
    # TODO: Forward to payment service
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Service not implemented yet",
    )


# ============================================================================
# Health Check and Root Endpoints
# ============================================================================


@app.get(
    "/",
    tags=["Health"],
    summary="Корневой endpoint",
    description="Возвращает информацию о сервисе",
)
async def root():
    """Корневой endpoint API Gateway."""
    return {
        "service": "Game Rental System API Gateway",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Проверка здоровья сервиса",
    description="Возвращает статус здоровья сервиса",
)
async def health_check():
    """Проверка здоровья сервиса."""
    return {"status": "healthy", "service": "gateway"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
