"""
Pydantic models for the Game Rental System API Gateway.

This module contains all request and response models for the microservices gateway,
organized by aggregate (bounded context).
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, EmailStr, HttpUrl


# ============================================================================
# Game Catalog Aggregate Models
# ============================================================================

class GameStatus(str, Enum):
    """Статус доступности игры для аренды."""
    AVAILABLE = "available"  # Доступна
    UNAVAILABLE = "unavailable"  # Недоступна
    RESERVED = "reserved"  # Зарезервирована
    RENTED = "rented"  # На руках у клиента
    INSPECTION = "inspection"  # На проверке
    REPAIR = "repair"  # В ремонте


class SortOrder(str, Enum):
    """Порядок сортировки игр."""
    ASC = "asc"  # По возрастанию
    DESC = "desc"  # По убыванию


class SortField(str, Enum):
    """Поле для сортировки игр."""
    NAME = "name"  # По названию
    RATING = "rating"  # По рейтингу
    PRICE = "price"  # По цене
    RELEASE_DATE = "release_date"  # По дате выпуска


class AddGameRequest(BaseModel):
    """Запрос на добавление игры в каталог.
    
    Attributes:
        name: Название игры (обязательное поле)
        description: Описание игры
        min_players: Минимальное количество игроков
        max_players: Максимальное количество игроков
        play_time_minutes: Продолжительность игры в минутах
        age_rating: Возрастное ограничение
        category: Категория игры (например, стратегия, карточная и т.д.)
        price_per_day: Стоимость аренды за день
        total_copies: Общее количество экземпляров игры
    """
    name: str = Field(..., description="Название игры", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Описание игры", max_length=2000)
    min_players: int = Field(..., description="Минимальное количество игроков", ge=1, le=20)
    max_players: int = Field(..., description="Максимальное количество игроков", ge=1, le=50)
    play_time_minutes: Optional[int] = Field(None, description="Продолжительность игры в минутах", ge=1)
    age_rating: Optional[int] = Field(None, description="Возрастное ограничение", ge=0, le=18)
    category: Optional[str] = Field(None, description="Категория игры", max_length=100)
    price_per_day: float = Field(..., description="Стоимость аренды за день", ge=0)
    total_copies: int = Field(..., description="Общее количество экземпляров игры", ge=1)


class UpdateGameInfoRequest(BaseModel):
    """Запрос на обновление информации об игре.
    
    Attributes:
        name: Новое название игры
        description: Новое описание игры
        min_players: Новое минимальное количество игроков
        max_players: Новое максимальное количество игроков
        play_time_minutes: Новая продолжительность игры в минутах
        age_rating: Новое возрастное ограничение
        category: Новая категория игры
        price_per_day: Новая стоимость аренды за день
    """
    name: Optional[str] = Field(None, description="Название игры", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Описание игры", max_length=2000)
    min_players: Optional[int] = Field(None, description="Минимальное количество игроков", ge=1, le=20)
    max_players: Optional[int] = Field(None, description="Максимальное количество игроков", ge=1, le=50)
    play_time_minutes: Optional[int] = Field(None, description="Продолжительность игры в минутах", ge=1)
    age_rating: Optional[int] = Field(None, description="Возрастное ограничение", ge=0, le=18)
    category: Optional[str] = Field(None, description="Категория игры", max_length=100)
    price_per_day: Optional[float] = Field(None, description="Стоимость аренды за день", ge=0)


class UploadGamePhotosRequest(BaseModel):
    """Запрос на загрузку фотографий игры.
    
    Attributes:
        photo_urls: Список URL фотографий игры
    """
    photo_urls: List[HttpUrl] = Field(..., description="Список URL фотографий игры", min_items=1, max_items=10)


class UpdateAvailableGamesRequest(BaseModel):
    """Запрос на обновление количества доступных к аренде игр.
    
    Attributes:
        available_count: Новое количество доступных экземпляров игры
    """
    available_count: int = Field(..., description="Количество доступных экземпляров игры", ge=0)


class SortGamesRequest(BaseModel):
    """Запрос на сортировку игр.
    
    Attributes:
        sort_field: Поле для сортировки (name, rating, price, release_date)
        sort_order: Порядок сортировки (asc, desc)
        limit: Максимальное количество результатов
        offset: Смещение для пагинации
    """
    sort_field: SortField = Field(..., description="Поле для сортировки")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Порядок сортировки")
    limit: int = Field(50, description="Максимальное количество результатов", ge=1, le=100)
    offset: int = Field(0, description="Смещение для пагинации", ge=0)


class FindGameRequest(BaseModel):
    """Запрос на поиск игры.
    
    Attributes:
        query: Поисковый запрос (название, описание, категория)
        category: Фильтр по категории
        min_players: Минимальное количество игроков
        max_players: Максимальное количество игроков
        max_price: Максимальная стоимость аренды за день
    """
    query: Optional[str] = Field(None, description="Поисковый запрос", max_length=200)
    category: Optional[str] = Field(None, description="Фильтр по категории", max_length=100)
    min_players: Optional[int] = Field(None, description="Минимальное количество игроков", ge=1)
    max_players: Optional[int] = Field(None, description="Максимальное количество игроков", ge=1)
    max_price: Optional[float] = Field(None, description="Максимальная стоимость аренды за день", ge=0)


class GameResponse(BaseModel):
    """Ответ с информацией об игре.
    
    Attributes:
        game_id: Уникальный идентификатор игры
        name: Название игры
        description: Описание игры
        status: Статус доступности игры
        available_count: Количество доступных экземпляров
        total_copies: Общее количество экземпляров
        photo_urls: Список URL фотографий
        rating: Средний рейтинг игры
        created_at: Дата создания записи
        updated_at: Дата последнего обновления
    """
    game_id: str = Field(..., description="Уникальный идентификатор игры")
    name: str = Field(..., description="Название игры")
    description: Optional[str] = Field(None, description="Описание игры")
    status: GameStatus = Field(..., description="Статус доступности игры")
    available_count: int = Field(..., description="Количество доступных экземпляров")
    total_copies: int = Field(..., description="Общее количество экземпляров")
    photo_urls: List[str] = Field(default_factory=list, description="Список URL фотографий")
    rating: Optional[float] = Field(None, description="Средний рейтинг игры", ge=0, le=5)
    created_at: datetime = Field(..., description="Дата создания записи")
    updated_at: datetime = Field(..., description="Дата последнего обновления")


# ============================================================================
# Booking Aggregate Models
# ============================================================================

class BookGameRequest(BaseModel):
    """Запрос на бронирование игры.
    
    Attributes:
        game_id: Идентификатор игры для бронирования
        user_id: Идентификатор пользователя
        booking_date: Дата бронирования
        pickup_date: Желаемая дата самовывоза
    """
    game_id: str = Field(..., description="Идентификатор игры для бронирования")
    user_id: str = Field(..., description="Идентификатор пользователя")
    booking_date: datetime = Field(..., description="Дата бронирования")
    pickup_date: datetime = Field(..., description="Желаемая дата самовывоза")


class CancelBookingRequest(BaseModel):
    """Запрос на отмену бронирования.
    
    Attributes:
        booking_id: Идентификатор бронирования
        user_id: Идентификатор пользователя (для проверки прав)
        reason: Причина отмены
    """
    booking_id: str = Field(..., description="Идентификатор бронирования")
    user_id: str = Field(..., description="Идентификатор пользователя")
    reason: Optional[str] = Field(None, description="Причина отмены", max_length=500)


class ConfirmBookingRequest(BaseModel):
    """Запрос на подтверждение бронирования.
    
    Attributes:
        booking_id: Идентификатор бронирования
        user_id: Идентификатор пользователя
    """
    booking_id: str = Field(..., description="Идентификатор бронирования")
    user_id: str = Field(..., description="Идентификатор пользователя")


class BookingResponse(BaseModel):
    """Ответ с информацией о бронировании.
    
    Attributes:
        booking_id: Уникальный идентификатор бронирования
        game_id: Идентификатор игры
        user_id: Идентификатор пользователя
        status: Статус бронирования (pending, confirmed, canceled)
        booking_date: Дата бронирования
        pickup_date: Дата самовывоза
        created_at: Дата создания бронирования
    """
    booking_id: str = Field(..., description="Уникальный идентификатор бронирования")
    game_id: str = Field(..., description="Идентификатор игры")
    user_id: str = Field(..., description="Идентификатор пользователя")
    status: str = Field(..., description="Статус бронирования")
    booking_date: datetime = Field(..., description="Дата бронирования")
    pickup_date: datetime = Field(..., description="Дата самовывоза")
    created_at: datetime = Field(..., description="Дата создания бронирования")


# ============================================================================
# Rating Aggregate Models
# ============================================================================

class LeaveRatingRequest(BaseModel):
    """Запрос на оставление оценки игры.
    
    Attributes:
        game_id: Идентификатор игры
        user_id: Идентификатор пользователя
        rating: Оценка от 1 до 5
    """
    game_id: str = Field(..., description="Идентификатор игры")
    user_id: str = Field(..., description="Идентификатор пользователя")
    rating: int = Field(..., description="Оценка от 1 до 5", ge=1, le=5)


class LeaveCommentRequest(BaseModel):
    """Запрос на оставление комментария к игре.
    
    Attributes:
        game_id: Идентификатор игры
        user_id: Идентификатор пользователя
        comment_text: Текст комментария
    """
    game_id: str = Field(..., description="Идентификатор игры")
    user_id: str = Field(..., description="Идентификатор пользователя")
    comment_text: str = Field(..., description="Текст комментария", min_length=1, max_length=2000)


class UpdateGameRatingRequest(BaseModel):
    """Запрос на обновление рейтинга игры (системная команда).
    
    Attributes:
        game_id: Идентификатор игры
        new_rating: Новый средний рейтинг игры
    """
    game_id: str = Field(..., description="Идентификатор игры")
    new_rating: float = Field(..., description="Новый средний рейтинг игры", ge=0, le=5)


class RatingResponse(BaseModel):
    """Ответ с информацией об оценке.
    
    Attributes:
        rating_id: Уникальный идентификатор оценки
        game_id: Идентификатор игры
        user_id: Идентификатор пользователя
        rating: Оценка от 1 до 5
        created_at: Дата создания оценки
    """
    rating_id: str = Field(..., description="Уникальный идентификатор оценки")
    game_id: str = Field(..., description="Идентификатор игры")
    user_id: str = Field(..., description="Идентификатор пользователя")
    rating: int = Field(..., description="Оценка от 1 до 5")
    created_at: datetime = Field(..., description="Дата создания оценки")


class CommentResponse(BaseModel):
    """Ответ с информацией о комментарии.
    
    Attributes:
        comment_id: Уникальный идентификатор комментария
        game_id: Идентификатор игры
        user_id: Идентификатор пользователя
        comment_text: Текст комментария
        is_moderated: Флаг модерации комментария
        created_at: Дата создания комментария
    """
    comment_id: str = Field(..., description="Уникальный идентификатор комментария")
    game_id: str = Field(..., description="Идентификатор игры")
    user_id: str = Field(..., description="Идентификатор пользователя")
    comment_text: str = Field(..., description="Текст комментария")
    is_moderated: bool = Field(..., description="Флаг модерации комментария")
    created_at: datetime = Field(..., description="Дата создания комментария")


# ============================================================================
# User Account Aggregate Models
# ============================================================================

class RegisterUserRequest(BaseModel):
    """Запрос на регистрацию пользователя.
    
    Attributes:
        email: Email адрес пользователя
        password: Пароль пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        phone: Номер телефона
    """
    email: EmailStr = Field(..., description="Email адрес пользователя")
    password: str = Field(..., description="Пароль пользователя", min_length=8, max_length=100)
    first_name: str = Field(..., description="Имя пользователя", min_length=1, max_length=100)
    last_name: str = Field(..., description="Фамилия пользователя", min_length=1, max_length=100)
    phone: Optional[str] = Field(None, description="Номер телефона", max_length=20)


class AuthorizeUserRequest(BaseModel):
    """Запрос на авторизацию пользователя.
    
    Attributes:
        email: Email адрес пользователя
        password: Пароль пользователя
    """
    email: EmailStr = Field(..., description="Email адрес пользователя")
    password: str = Field(..., description="Пароль пользователя")


class BlockUserRequest(BaseModel):
    """Запрос на блокировку пользователя.
    
    Attributes:
        user_id: Идентификатор пользователя для блокировки
        reason: Причина блокировки
    """
    user_id: str = Field(..., description="Идентификатор пользователя для блокировки")
    reason: Optional[str] = Field(None, description="Причина блокировки", max_length=500)


class UnblockUserRequest(BaseModel):
    """Запрос на разблокировку пользователя.
    
    Attributes:
        user_id: Идентификатор пользователя для разблокировки
    """
    user_id: str = Field(..., description="Идентификатор пользователя для разблокировки")


class UpdateUserProfileRequest(BaseModel):
    """Запрос на обновление профиля пользователя.
    
    Attributes:
        user_id: Идентификатор пользователя
        first_name: Новое имя пользователя
        last_name: Новая фамилия пользователя
        phone: Новый номер телефона
    """
    user_id: str = Field(..., description="Идентификатор пользователя")
    first_name: Optional[str] = Field(None, description="Имя пользователя", min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, description="Фамилия пользователя", min_length=1, max_length=100)
    phone: Optional[str] = Field(None, description="Номер телефона", max_length=20)


class UserResponse(BaseModel):
    """Ответ с информацией о пользователе.
    
    Attributes:
        user_id: Уникальный идентификатор пользователя
        email: Email адрес пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя
        phone: Номер телефона
        is_blocked: Флаг блокировки пользователя
        created_at: Дата регистрации
        updated_at: Дата последнего обновления
    """
    user_id: str = Field(..., description="Уникальный идентификатор пользователя")
    email: EmailStr = Field(..., description="Email адрес пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str = Field(..., description="Фамилия пользователя")
    phone: Optional[str] = Field(None, description="Номер телефона")
    is_blocked: bool = Field(..., description="Флаг блокировки пользователя")
    created_at: datetime = Field(..., description="Дата регистрации")
    updated_at: datetime = Field(..., description="Дата последнего обновления")


class AuthResponse(BaseModel):
    """Ответ с результатом авторизации.
    
    Attributes:
        access_token: JWT токен доступа
        token_type: Тип токена (обычно "bearer")
        user: Информация о пользователе
    """
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field("bearer", description="Тип токена")
    user: UserResponse = Field(..., description="Информация о пользователе")


# ============================================================================
# Rent Aggregate Models
# ============================================================================

class CreateOrderRequest(BaseModel):
    """Запрос на создание заказа на аренду.
    
    Attributes:
        booking_id: Идентификатор подтвержденного бронирования
        user_id: Идентификатор пользователя
        pickup_location: Адрес места самовывоза
        rental_days: Количество дней аренды
    """
    booking_id: str = Field(..., description="Идентификатор подтвержденного бронирования")
    user_id: str = Field(..., description="Идентификатор пользователя")
    pickup_location: str = Field(..., description="Адрес места самовывоза", max_length=200)
    rental_days: int = Field(..., description="Количество дней аренды", ge=1, le=30)


class SendPickupNotificationRequest(BaseModel):
    """Запрос на отправку уведомления о дате и месте самовывоза.
    
    Attributes:
        order_id: Идентификатор заказа
        pickup_date: Дата самовывоза
        pickup_location: Адрес места самовывоза
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    pickup_date: datetime = Field(..., description="Дата самовывоза")
    pickup_location: str = Field(..., description="Адрес места самовывоза", max_length=200)


class ConfirmGameReceiptRequest(BaseModel):
    """Запрос на подтверждение получения игры.
    
    Attributes:
        order_id: Идентификатор заказа
        user_id: Идентификатор пользователя
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    user_id: str = Field(..., description="Идентификатор пользователя")


class SendReturnReminderRequest(BaseModel):
    """Запрос на отправку напоминания о возврате игры.
    
    Attributes:
        order_id: Идентификатор заказа
        return_date: Дата возврата
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    return_date: datetime = Field(..., description="Дата возврата")


class ExtendRentalPeriodRequest(BaseModel):
    """Запрос на продление срока аренды.
    
    Attributes:
        order_id: Идентификатор заказа
        user_id: Идентификатор пользователя
        additional_days: Количество дополнительных дней аренды
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    user_id: str = Field(..., description="Идентификатор пользователя")
    additional_days: int = Field(..., description="Количество дополнительных дней аренды", ge=1, le=7)


class EndRentalPeriodRequest(BaseModel):
    """Запрос на завершение срока аренды (системная команда).
    
    Attributes:
        order_id: Идентификатор заказа
    """
    order_id: str = Field(..., description="Идентификатор заказа")


class ReturnGameRequest(BaseModel):
    """Запрос на возврат игры.
    
    Attributes:
        order_id: Идентификатор заказа
        user_id: Идентификатор пользователя
        return_location: Адрес места возврата
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    user_id: str = Field(..., description="Идентификатор пользователя")
    return_location: str = Field(..., description="Адрес места возврата", max_length=200)


class ChargePenaltyRequest(BaseModel):
    """Запрос на начисление штрафа за просрочку.
    
    Attributes:
        order_id: Идентификатор заказа
        penalty_amount: Сумма штрафа
        reason: Причина начисления штрафа
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    penalty_amount: float = Field(..., description="Сумма штрафа", ge=0)
    reason: str = Field(..., description="Причина начисления штрафа", max_length=500)


class ConfirmGameReturnRequest(BaseModel):
    """Запрос на подтверждение возврата игры.
    
    Attributes:
        order_id: Идентификатор заказа
        game_condition: Состояние игры при возврате
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    game_condition: str = Field(..., description="Состояние игры при возврате", max_length=200)


class OrderResponse(BaseModel):
    """Ответ с информацией о заказе на аренду.
    
    Attributes:
        order_id: Уникальный идентификатор заказа
        booking_id: Идентификатор бронирования
        game_id: Идентификатор игры
        user_id: Идентификатор пользователя
        status: Статус заказа
        pickup_date: Дата самовывоза
        pickup_location: Адрес места самовывоза
        return_date: Дата возврата
        rental_days: Количество дней аренды
        total_amount: Общая сумма заказа
        penalty_amount: Сумма штрафа (если есть)
        created_at: Дата создания заказа
    """
    order_id: str = Field(..., description="Уникальный идентификатор заказа")
    booking_id: str = Field(..., description="Идентификатор бронирования")
    game_id: str = Field(..., description="Идентификатор игры")
    user_id: str = Field(..., description="Идентификатор пользователя")
    status: str = Field(..., description="Статус заказа")
    pickup_date: datetime = Field(..., description="Дата самовывоза")
    pickup_location: str = Field(..., description="Адрес места самовывоза")
    return_date: Optional[datetime] = Field(None, description="Дата возврата")
    rental_days: int = Field(..., description="Количество дней аренды")
    total_amount: float = Field(..., description="Общая сумма заказа")
    penalty_amount: Optional[float] = Field(None, description="Сумма штрафа")
    created_at: datetime = Field(..., description="Дата создания заказа")


# ============================================================================
# Payment Aggregate Models
# ============================================================================

class InitiatePaymentRequest(BaseModel):
    """Запрос на инициирование платежа.
    
    Attributes:
        order_id: Идентификатор заказа
        user_id: Идентификатор пользователя
        amount: Сумма платежа
        payment_method: Способ оплаты
    """
    order_id: str = Field(..., description="Идентификатор заказа")
    user_id: str = Field(..., description="Идентификатор пользователя")
    amount: float = Field(..., description="Сумма платежа", ge=0)
    payment_method: str = Field(..., description="Способ оплаты", max_length=50)


class ProcessPaymentRequest(BaseModel):
    """Запрос на обработку платежа.
    
    Attributes:
        payment_id: Идентификатор платежа
        transaction_id: Идентификатор транзакции от платежной системы
    """
    payment_id: str = Field(..., description="Идентификатор платежа")
    transaction_id: str = Field(..., description="Идентификатор транзакции от платежной системы")


class RequestRefundRequest(BaseModel):
    """Запрос на возврат средств.
    
    Attributes:
        payment_id: Идентификатор платежа
        user_id: Идентификатор пользователя
        reason: Причина возврата
        amount: Сумма возврата (если частичный возврат)
    """
    payment_id: str = Field(..., description="Идентификатор платежа")
    user_id: str = Field(..., description="Идентификатор пользователя")
    reason: str = Field(..., description="Причина возврата", max_length=500)
    amount: Optional[float] = Field(None, description="Сумма возврата (если частичный возврат)", ge=0)


class ProcessRefundRequest(BaseModel):
    """Запрос на обработку возврата средств.
    
    Attributes:
        refund_id: Идентификатор запроса на возврат
        transaction_id: Идентификатор транзакции возврата от платежной системы
    """
    refund_id: str = Field(..., description="Идентификатор запроса на возврат")
    transaction_id: str = Field(..., description="Идентификатор транзакции возврата от платежной системы")


class DeclineRefundRequest(BaseModel):
    """Запрос на отклонение возврата средств.
    
    Attributes:
        refund_id: Идентификатор запроса на возврат
        reason: Причина отклонения
    """
    refund_id: str = Field(..., description="Идентификатор запроса на возврат")
    reason: str = Field(..., description="Причина отклонения", max_length=500)


class PaymentResponse(BaseModel):
    """Ответ с информацией о платеже.
    
    Attributes:
        payment_id: Уникальный идентификатор платежа
        order_id: Идентификатор заказа
        user_id: Идентификатор пользователя
        amount: Сумма платежа
        status: Статус платежа (initiated, processing, completed, declined, refunded)
        payment_method: Способ оплаты
        transaction_id: Идентификатор транзакции
        created_at: Дата создания платежа
        completed_at: Дата завершения платежа
    """
    payment_id: str = Field(..., description="Уникальный идентификатор платежа")
    order_id: str = Field(..., description="Идентификатор заказа")
    user_id: str = Field(..., description="Идентификатор пользователя")
    amount: float = Field(..., description="Сумма платежа")
    status: str = Field(..., description="Статус платежа")
    payment_method: str = Field(..., description="Способ оплаты")
    transaction_id: Optional[str] = Field(None, description="Идентификатор транзакции")
    created_at: datetime = Field(..., description="Дата создания платежа")
    completed_at: Optional[datetime] = Field(None, description="Дата завершения платежа")


class RefundResponse(BaseModel):
    """Ответ с информацией о возврате средств.
    
    Attributes:
        refund_id: Уникальный идентификатор возврата
        payment_id: Идентификатор платежа
        user_id: Идентификатор пользователя
        amount: Сумма возврата
        status: Статус возврата (requested, processing, completed, declined)
        reason: Причина возврата
        transaction_id: Идентификатор транзакции возврата
        created_at: Дата создания запроса на возврат
        completed_at: Дата завершения возврата
    """
    refund_id: str = Field(..., description="Уникальный идентификатор возврата")
    payment_id: str = Field(..., description="Идентификатор платежа")
    user_id: str = Field(..., description="Идентификатор пользователя")
    amount: float = Field(..., description="Сумма возврата")
    status: str = Field(..., description="Статус возврата")
    reason: str = Field(..., description="Причина возврата")
    transaction_id: Optional[str] = Field(None, description="Идентификатор транзакции возврата")
    created_at: datetime = Field(..., description="Дата создания запроса на возврат")
    completed_at: Optional[datetime] = Field(None, description="Дата завершения возврата")


# ============================================================================
# Common Response Models
# ============================================================================

class SuccessResponse(BaseModel):
    """Универсальный ответ об успешном выполнении операции.
    
    Attributes:
        success: Флаг успешного выполнения
        message: Сообщение о результате операции
    """
    success: bool = Field(True, description="Флаг успешного выполнения")
    message: str = Field(..., description="Сообщение о результате операции")


class ErrorResponse(BaseModel):
    """Ответ об ошибке.
    
    Attributes:
        success: Флаг успешного выполнения (всегда False)
        error: Код ошибки
        message: Сообщение об ошибке
        details: Дополнительные детали об ошибке
    """
    success: bool = Field(False, description="Флаг успешного выполнения")
    error: str = Field(..., description="Код ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[dict] = Field(None, description="Дополнительные детали об ошибке")

