import csv
from msilib import Table

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .forms import *
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from .models import *
import logging

import pandas as pd
import json
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
import openpyxl

logger = logging.getLogger('django')


def home(request):
    logger.info("Запрошена главная страница.")
    countries = Country.objects.prefetch_related('city_set').all()
    return render(request, 'TripTuner/index.html', {'countries': countries})


def register(request):
    logger.info("Запрос на регистрацию.")
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт для {username} создан успешно!')
            logger.info(f"Аккаунт для {username} создан.")
            return redirect('login')
        else:
            print(form.errors)
            logger.warning("Форма регистрации не прошла валидацию.")
    else:
        form = RegistrationForm()
    return render(request, 'TripTuner/auth/registration.html', {'form': form})


def login_view(request):
    logger.info("Запрос на вход.")
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"Пользователь {user.username} вошел в систему.")
            if user.role_name == 'Travel Agent' or user.role_name == 'Hotel Manager':
                return redirect('control_panel')
            else:
                return redirect('home')
        else:
            logger.warning("Форма входа не прошла валидацию.")
            return render(request, 'TripTuner/auth/login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'TripTuner/auth/login.html', {'form': form})


def logout_view(request):
    logger.info(f"Пользователь {request.user.username} вышел из профиля.")
    logout(request)
    messages.success(request, "Вы успешно вышли из профиля.")
    return redirect('home')


class TourListView(ListView):
    model = Tour
    template_name = 'TripTuner/tours.html'
    context_object_name = 'tours'
    paginate_by = 2

    def get_queryset(self):
        logger.info("Запрос на получение списка туров.")
        country_id = self.kwargs.get('country_id')
        queryset = Tour.objects.filter(country_id=country_id) if country_id else Tour.objects.all()

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(country_id__name__icontains=search_query) |
                Q(description__icontains=search_query)
            ).distinct()
            logger.info(f"Поиск туров по запросу '{search_query}'.")
        return queryset



def profile_view(request):
    logger.info(f"Запрос на просмотр профиля пользователя {request.user.username}.")
    user = request.user
    editable = request.method == 'POST' and 'update_profile' in request.POST

    if editable:
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.save()
        messages.success(request, 'Профиль успешно обновлен!')
        logger.info(f"Профиль пользователя {user.username} обновлен.")
        return redirect('profile')

    if request.method == 'POST' and 'update_password' in request.POST:
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and confirm_password:
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Пароль успешно обновлен!')
                logger.info(f"Пароль пользователя {user.username} обновлен.")
            else:
                messages.error(request, 'Пароли не совпадают.')
                logger.warning("Пароли не совпадают.")
        else:
            messages.error(request, 'Пожалуйста, заполните оба поля для пароля.')
            logger.warning("Не заполнены оба поля для пароля.")
        return redirect('profile')

    return render(request, 'TripTuner/profile.html', {'user': user, 'editable': editable})


def order_history_view(request, user_id):
    logger.info(f"Запрос на просмотр истории заказов пользователя {user_id}.")
    order_history = Order.objects.filter(client_id=user_id).select_related(
        'flight_id', 'flight_id__departure_location_id', 'flight_id__arrival_location_id'
    )
    return render(request, 'TripTuner/orderHistory.html', {'order_history': order_history})


def flight_list(request, tour_id):
    logger.info(f"Запрос на получение списка рейсов для тура {tour_id}.")
    flights = Flight.objects.filter(tour_id=tour_id)
    paginator = Paginator(flights, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'TripTuner/flight.html', {
        'page_obj': page_obj,
        'tour_id': tour_id
    })


def flight_detail(request, tour_id, flight_id):
    logger.info(f"Запрос на просмотр деталей рейса {flight_id} для тура {tour_id}.")
    flight = get_object_or_404(Flight, id=flight_id, tour_id=tour_id)
    flight_hotel_info = FlightHotelHotelRoom.objects.filter(flight_id=flight).select_related('hotel_id', 'hotelRoom_id')

    hotel_room_ids = [item.hotelRoom_id.id for item in flight_hotel_info]
    reviews = Review.objects.filter(hotelRoom_id__in=hotel_room_ids)

    return render(request, 'TripTuner/flightView.html', {
        'flight': flight,
        'flight_hotel_info': flight_hotel_info,
        'reviews': reviews
    })


class HotelsListView(ListView):
    model = Hotel
    template_name = 'TripTuner/hotels.html'
    context_object_name = 'hotels'
    paginate_by = 10

    def get_queryset(self):
        logger.info("Запрос на получение списка отелей.")

        queryset = Hotel.objects.select_related('city_id__country_id').all()

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(city_id__name__icontains=search_query) |
                Q(city_id__country_id__name__icontains=search_query)
            ).distinct()
            logger.info(f"Поиск отелей по запросу '{search_query}'.")

        return queryset


class HotelRoomListView(ListView):
    model = HotelRoom
    template_name = 'TripTuner/hotelRoom.html'
    context_object_name = 'rooms'
    paginate_by = 10

    def get_queryset(self):
        hotel_id = self.kwargs.get('hotel_id')
        logger.info(f"Запрос на получение списка номеров для отеля {hotel_id}.")
        return HotelRoom.objects.filter(hotel_id=hotel_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = context['rooms']
        room_ids = [room.id for room in rooms]
        context['amenities'] = Amenity.objects.filter(hotelRoom_id__in=room_ids)
        return context


class HotelRoomDetailView(DetailView):
    model = HotelRoom
    template_name = 'TripTuner/hotelRoomDetail.html'
    context_object_name = 'room'

    def get_context_data(self, **kwargs):
        logger.info(f"Запрос на просмотр деталей номера {self.object.id}.")
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(hotelRoom_id=self.object.id).select_related('client_id')
        context['amenities'] = Amenity.objects.filter(hotelRoom_id=self.object.id)
        return context


@login_required
def add_review(request, room_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        advantages = request.POST.get('advantages')
        disadvantages = request.POST.get('disadvantages')
        hotel_room = get_object_or_404(HotelRoom, id=room_id)
        Review.objects.create(
            rating=rating,
            advantages=advantages,
            disadvantages=disadvantages,
            hotelRoom_id=hotel_room,
            client_id=request.user
        )
        logger.info(f'Пользователь {request.user.id} - {request.user.username}  отправил')
        return redirect('hotel_room_detail', pk=room_id)


@login_required
def add_to_cart(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == "POST":
        booking_place = int(request.POST.get('booking_place', 1))
        flight.amount_places -= booking_place

        if request.POST.get('price_option') == 'with_bag':
            price_of_order = flight.cost_with_bag * booking_place
        else:
            price_of_order = flight.cost_without_bag * booking_place

        order = Order(
            booking_place=booking_place,
            price_of_order=price_of_order,
            flight_id=flight,
            client_id=request.user
        )
        order.save()
        logger.info(f'Пользователь {request.user.id} - {request.user.username} добавил рейс {flight.id} в корзину')
        flight.save()

        return redirect('basket')

    return redirect('flight_detail', flight_id=flight_id)


@login_required
def remove_from_cart(request, order_id):
    order = get_object_or_404(Order, id=order_id, client_id=request.user)
    order.delete()
    logger.info(f'Пользователь {request.user.id} - {request.user.username} удалил товар {order_id} из корзины')
    return redirect('basket')


@login_required
def basket(request):
    logger.info(f"Пользователь {request.user.id} - {request.user.username} просматривает корзину.")
    orders = Order.objects.filter(client_id=request.user).exclude(payment__isnull=False)
    logger.debug(f"Количество заказов в корзине: {orders.count()}")
    context = {
        'orders': orders,
    }
    return render(request, 'TripTuner/basket.html', context)




@login_required
def payment_view(request, order_id):
    logger.info(f"Пользователь {request.user.username} инициировал просмотр страницы оплаты для заказа с ID заказа {order_id}.")
    order = get_object_or_404(Order, id=order_id)

    initial_data = {
        'email': order.client_id.email,
        'quantity': order.booking_place
    }

    if request.method == 'POST':
        logger.info("Обрабатывается POST-запрос для оплаты.")
        form = PaymentForm(request.POST, initial=initial_data)
        if form.is_valid():
            payment = Payment.objects.create(
                payment_amount=order.price_of_order * form.cleaned_data['quantity'],
                payment_status="Completed",
                payment_method=form.cleaned_data['payment_method'],
                order_id=order
            )
            logger.info(f"Оплата успешно создана. Сумма: {payment.payment_amount}, Способ: {payment.payment_method}.")
            payment_method_display = payment.payment_method

            payment_method_mapping = {
                'credit_card': 'Кредитная карта',
                'paypal': 'PayPal',
                'bank_transfer': 'Банковский перевод'
            }
            payment_method_display = payment_method_mapping.get(payment.payment_method, 'Неизвестно')

            send_mail(
                'Оплата подтверждена',
                f'Ваш заказ оплачен. Сумма: {payment.payment_amount} руб. Способ оплаты: {payment_method_display}. '
                f'Если не явитесь за день до отправления {order.flight_id.departure_date}, заказ аннулируется, и деньги будут возвращены.',
                settings.DEFAULT_FROM_EMAIL,
                recipient_list=[f'{order.client_id.email}'],
                fail_silently=False,
            )
            logger.info(f"Письмо об успешной оплате отправлено на {order.client_id.email}.")
            messages.success(request, "Оплата прошла успешно!")
            return redirect('basket')
        else:
            logger.warning("Форма оплаты не прошла валидацию.")
    else:
        form = PaymentForm(initial=initial_data)
        logger.info("Отображение формы оплаты.")

    return render(request, 'TripTuner/payment.html', {'form': form, 'order': order})

@login_required
def support_ticket_create(request):
    logger.info("Пользователь инициировал создание тикета поддержки.")
    if request.method == 'POST':
        description = request.POST.get('issue_description')
        if description:
            logger.debug(f"Описание тикета: {description}")
            ticket = SupportTicket.objects.create(
                issue_description=description,
                client_id=request.user
            )
            ticket.save()
            logger.info(f"Тикет поддержки создан пользователем {request.user.username}.")
            messages.success(request, "Ваше сообщение отправлено в поддержку.")
        else:
            logger.warning("Попытка создания тикета поддержки без описания.")
            messages.error(request, "Пожалуйста, заполните описание проблемы.")
        return redirect('profile')


model_form_mapping = {
    'supportTickets': (SupportTicket, SupportTicketForm),
    'flights': (Flight, FlightForm),
    'orders': (Order, OrderForm),
    'tours': (Tour, TourForm),
    'countries': (Country, CountryForm),
    'cities': (City, CityForm),
    'hotels': (Hotel, HotelForm),
    'hotelRooms': (HotelRoom, HotelRoomForm),
    'hotelRoomImages': (HotelRoomImage, HotelRoomImageForm),
    'amenities': (Amenity, AmenityForm),
    'flighthotelhotelroom': (FlightHotelHotelRoom, FlightHotelHotelRoomForm),
    }

def control_panel(request):
    if request.user.role_name == 'Travel Agent' or request.user.is_superuser:
        logger.info(f"Был прои")
        tables = [
            ('supportTickets', 'Поддержка'),
            ('tours', 'Туры'),
            ('flights', 'Рейсы'),
            ('orders', 'Заказы'),
            ('flighthotelhotelroom', 'Прикрепление отеля и номера к рейсу')
        ]
    elif request.user.role_name == 'Hotel Manager':
        tables = [
            ('hotels', 'Отели'),
            ('hotelRooms', 'Номера отелей'),
            ('countries', 'Страны'),
            ('cities', 'Города'),
            ('hotelRoomImages', 'Изображения номеров'),
            ('amenities', 'Удобства номеров')
        ]
    else:
        return redirect('home')

    table_name = request.GET.get('table', tables[0][0])
    model_class, form_class = model_form_mapping.get(table_name, (None, None))

    if model_class is None:
        return redirect('home')

    objects = model_class.objects.all()
    form = form_class(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(f'/triptuner/control-panel/?table={table_name}')

    return render(request, 'TripTuner/control-panel.html', {'user': request.user,'objects': objects,
        'form': form,
        'table_name': table_name, 'tables': tables
    })



@login_required
def edit_object(request, pk, table):
    model_class, form_class = model_form_mapping.get(table, (None, None))

    if model_class is None:
        return redirect('control_panel')

    object = get_object_or_404(model_class, pk=pk)
    form = form_class(request.POST or None, instance=object)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('control_panel')

    return render(request, 'TripTuner/control-panel.html', {'form': form})
@login_required
def delete_object(request, pk, table):
    model_class, _ = model_form_mapping.get(table, (None, None))

    if model_class is None:
        return redirect('control_panel')

    object = get_object_or_404(model_class, pk=pk)
    object.delete()
    return redirect('control_panel')




from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
def export_data(request):
    table_name = request.GET.get('table')
    format_type = request.GET.get('format', 'json')
    model_class, form_class = model_form_mapping.get(table_name, (None, None))

    if model_class is None:
        return JsonResponse({'error': 'Невозможно найти таблицу'}, status=400)

    objects = model_class.objects.all()

    if format_type == 'json':
        data = list(objects.values())
        response = JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False})
        response['Content-Disposition'] = f'attachment; filename={table_name}.json'
        return response

    return JsonResponse({'error': 'Неподдерживаемый формат'}, status=400)

def import_data(request):
    if request.method == 'POST':
        table_name = request.POST.get('table')
        file = request.FILES.get('file')
        format_type = request.POST.get('format', 'json')
        model_class, _ = model_form_mapping.get(table_name, (None, None))

        if model_class is None:
            return JsonResponse({'error': 'Невозможно найти таблицу'}, status=400)

        if not file:
            return JsonResponse({'error': 'Не выбран файл для импорта'}, status=400)

        if format_type == 'json':
            try:
                data = json.load(file)

                for item in data:
                    try:
                        obj, created = model_class.objects.update_or_create(
                            id=item.get('id'),
                            defaults=item
                        )
                    except ValidationError as e:
                        return JsonResponse({'error': f'Ошибка при сохранении данных: {e.message}'}, status=400)

                return redirect(f'/triptuner/control-panel/?table={table_name}')
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Ошибка в формате файла'}, status=400)
        else:
            return JsonResponse({'error': 'Неподдерживаемый формат'}, status=400)

    return JsonResponse({'error': 'Метод POST ожидается'}, status=400)