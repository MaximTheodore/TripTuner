from django.utils import timezone

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from django.db import models
from django.core.validators import (
    RegexValidator, EmailValidator, MinLengthValidator, MaxValueValidator, MinValueValidator, DecimalValidator
)
from django.contrib.auth.hashers import make_password
from Coursework import settings


phone_validator = RegexValidator(
    regex=r'^8\d{10}$',
    message="Введите правильный номер телефона (например, 89997778855)."
)
name_validator = RegexValidator(
    regex=r'^[А-Яа-яA-Za-z]+$',
    message="Поле должно содержать только буквы."
)
text_validator = RegexValidator(
    regex=r'^[а-яА-Яa-zA-Z\s]*$',
    message="Поле должно содержать только буквы."
)
number_validator = RegexValidator(
    regex=r'^\d+$',
    message="Поле должно содержать только цифры."
)
decimal_validator = RegexValidator(
    regex=r'^(\d+)$',
    message="Поле должно содержать только цифры."
)
flight_number_validator = RegexValidator(
    regex=r'^[A-Za-z0-9]*$',
    message="Номер рейса должен содержать только буквы и цифры."
)
ROLE_CHOICES = [
    ('Client', 'Клиент'),
    ('DB Admin', 'Администратор базы данных'),
    ('Travel Agent', 'Турагент'),
    ('Hotel Manager', 'Менеджер отелей')
]


class User(AbstractUser):
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Имя пользователя",
        validators=[
            MinLengthValidator(1, message="Минимальный размер имени пользователя 5"),
            RegexValidator(
                regex=r'^[A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]*$',
                message="Имя пользователя может содержать латинские буквы, цифры, и специальные символы."
            )
        ]
    )

    password = models.CharField(
        max_length=255,
        verbose_name="Пароль",
        validators=[
            MinLengthValidator(8),
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                message="Пароль должен содержать минимум одну букву, одну цифру и один спецсимвол, и только латиница."
            )
        ]
    )
    image = models.ImageField(verbose_name="Фото профиля",
                              null=True,
                              blank=True)
    email = models.CharField(
        max_length=50,
        verbose_name="Электронная почта",
        unique=True,
        null=True,
        blank=True,
        validators=[EmailValidator()]
    )
    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя",
        validators=[MinLengthValidator(2)]
    )
    last_name = models.CharField(
        max_length=50,
        verbose_name="Фамилия",
        validators=[MinLengthValidator(2)]
    )
    patronymic = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Отчество (необязательно)"
    )
    phone = models.CharField(
        max_length=15,
        verbose_name="Телефон",
        validators=[phone_validator]
    )
    role_name = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        verbose_name="Название роли",
        default="Клиент"
    )

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


    class Meta:
        swappable = settings.AUTH_USER_MODEL
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class SupportTicket(models.Model):
    issue_description = models.TextField(
        max_length=255,
        verbose_name="Описание проблемы",
        validators=[MinLengthValidator(10, "Описание должно содержать минимум 10 символов.")]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    resolved_at = models.DateTimeField(verbose_name="Дата решения", null=True, blank=True)
    answer_status = models.CharField(
        max_length=50,
        verbose_name="Статус ответа",
        validators=[name_validator]
    )
    tourAgent_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agent", verbose_name="Турагент", default=None, null=True, blank=True)
    client_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client", verbose_name="Клиент")

    class Meta:
        verbose_name = "Поддержка"
        verbose_name_plural = "Поддержка"

    def __str__(self):
        issue_description_preview = self.issue_description[:50] + "..." if len(self.issue_description) > 50 else self.issue_description
        return f"Обращение от {self.client_id.username} {self.client_id.last_name}: {issue_description_preview}"



class Country(models.Model):
    image = models.ImageField(verbose_name="Изображение")
    name = models.CharField(max_length=100, verbose_name="Название страны", validators=[text_validator])

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self):
        return self.name


class City(models.Model):
    image = models.ImageField(verbose_name="Изображение")
    name = models.CharField(max_length=100, verbose_name="Название города", validators=[text_validator])
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна", default=None, null=True, blank=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.name


class Hotel(models.Model):
    image = models.ImageField(verbose_name="Изображение")
    name = models.CharField(max_length=255, verbose_name="Название отеля")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    city_id = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город", default=None, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Отель"
        verbose_name_plural = "Отели"


class HotelRoom(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название комнаты")
    size = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Размер", validators=[
        MinValueValidator(0.0, message="Размер не может быть отрицательным."),
        DecimalValidator(10, 2)
    ])
    description = models.TextField(verbose_name="Описание")
    hotel_id = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Отель")

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"

    def __str__(self):
        return self.name


class HotelRoomImage(models.Model):
    image = models.ImageField(verbose_name="Изображение комнаты")
    hotelRoom_id = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, verbose_name="Комната")

    class Meta:
        verbose_name = "Изображение комнаты"
        verbose_name_plural = "Изображения комнаты"


class Amenity(models.Model):
    image = models.ImageField(verbose_name="Изображение")
    name = models.CharField(max_length=255, verbose_name="Название удобства", validators=[text_validator])
    hotelRoom_id = models.ManyToManyField(HotelRoom, verbose_name="Комната")

    class Meta:
        verbose_name = "Удобство"
        verbose_name_plural = "Удобства"

    def __str__(self):
        return self.name


class Tour(models.Model):
    image = models.ImageField(verbose_name="Изображение")
    title = models.CharField(max_length=100, verbose_name="Название тура", validators=[text_validator])
    description = models.TextField(verbose_name="Описание")
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна", default=None, null=True, blank=True)
    tourAgent_id = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name="Турагент", default=None)

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"

    def __str__(self):
        return self.title




class Flight(models.Model):
    flight_number = models.CharField(max_length=50, verbose_name="Номер рейса", validators=[flight_number_validator])
    amount_places = models.IntegerField(verbose_name="Количество мест", validators=[
        MinValueValidator(1, message="Должно быть как минимум одно место.")
    ])
    VISA = models.BooleanField(verbose_name="Нужна виза?", default=False)
    cost_with_bag = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость с багажом", validators=[
        MinValueValidator(0.0, message="Стоимость не может быть отрицательной.")
    ])
    cost_without_bag = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость без багажа", validators=[
        MinValueValidator(0.0, message="Стоимость не может быть отрицательной.")
    ])
    way = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Дистанция", validators=[
        MinValueValidator(0.0, message="Дистанция не может быть отрицательной.")
    ])
    days_of_rest = models.IntegerField(verbose_name="Количество дней отдыха", validators=[
        MinValueValidator(1, message="Количество дней отдыха должно быть больше 0.")
    ])
    return_date = models.DateTimeField(verbose_name="Дата возвращения")
    departure_date = models.DateTimeField(verbose_name="Дата отправления")
    tour_id = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name="Тур")
    departure_location_id = models.ForeignKey(City, on_delete=models.CASCADE, related_name="departure_flights", verbose_name="Место отправления")
    arrival_location_id = models.ForeignKey(City, on_delete=models.CASCADE, related_name="arrival_flights", verbose_name="Место прибытия")

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"

    def __str__(self):
        return self.flight_number


class Review(models.Model):
    rating = models.IntegerField(verbose_name="Оценка", validators=[
        MinValueValidator(1, message="Оценка не может быть меньше 1."),
        MaxValueValidator(5, message="Оценка не может быть больше 5.")
    ], null=True, blank=True)
    advantages = models.TextField(verbose_name="Преимущества", default=None, null=True, blank=True)
    disadvantages = models.TextField(verbose_name="Недостатки", default=None, null=True, blank=True)
    review_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")
    hotelRoom_id = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, verbose_name="Номер отеля", default=None, null=True, blank=True)
    client_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return self.id + ' ' + self.hotelRoom_id.name


class Order(models.Model):
    booking_place = models.IntegerField(verbose_name="Забронированные места", validators=[
        MinValueValidator(1, message="Должно быть забронировано хотя бы одно место.")
    ])
    price_of_order = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена заказа", validators=[
        MinValueValidator(0.0, message="Цена не может быть отрицательной.")
    ])
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    flight_id = models.ForeignKey(Flight, on_delete=models.CASCADE, verbose_name="Рейс")
    client_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Клиент")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"{self.id} - {self.flight_id.flight_number} - {self.client_id.first_name}"


class OrderHistory(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    client_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Клиент")

    class Meta:
        verbose_name = "История заказов клиента"
        verbose_name_plural = "Истории заказов клиентов"


class Payment(models.Model):
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты", validators=[
        MinValueValidator(0.0, message="Сумма оплаты не может быть отрицательной.")
    ])
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    payment_status = models.CharField(max_length=50, verbose_name="Статус оплаты")
    payment_method = models.CharField(max_length=50, verbose_name="Способ оплаты")
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"


class FlightHotelHotelRoom(models.Model):
    flight_id = models.ForeignKey(Flight, on_delete=models.CASCADE, verbose_name="Рейс")
    hotel_id = models.ForeignKey(Hotel, on_delete=models.CASCADE, verbose_name="Отель")
    hotelRoom_id = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, verbose_name="Номер в отеле")

    class Meta:
        verbose_name = "Рейс-Отель-Номер"
        verbose_name_plural = "Рейсы-Отели-Номера"

    def __str__(self):
        return f'Рейс {self.flight_id.flight_number} - Отель {self.hotel_id.name} - Номер {self.hotelRoom_id.name}'