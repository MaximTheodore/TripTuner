import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.password_validation import password_changed

from .models import *
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'image', 'email', 'first_name', 'last_name', 'patronymic', 'phone']
        widgets = {
            'password': forms.PasswordInput(),
        }
        labels = {
            'username': 'Имя пользователя',
            'password': 'Пароль',
            'image': 'Фото профиля',
            'email': 'Электронная почта',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'patronymic': 'Отчество (необязательно)',
            'phone': 'Телефон',

        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role_name = 'Клиент'
        if commit:
            user.save()
        return user


class UserChangeForm(UserChangeForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
        label="Пароль"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'image', 'first_name', 'last_name', 'patronymic', 'phone', 'role_name',
                  'is_staff']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AuthenticationForm1(AuthenticationForm):
    username = forms.CharField(
        label="Логин пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        min_length=5,
    )
    password = forms.CharField(
        label="Введите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
    )

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    self.user_cache = user
                else:
                    raise forms.ValidationError("Неверный логин или пароль.")
            except User.DoesNotExist:
                raise forms.ValidationError("Неверный логин или пароль.")

        return cleaned_data

    def get_user(self):
        return self.user_cache


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label="Логин пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        min_length=5,
    )
    password = forms.CharField(
        label="Придумайте пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    image = forms.ImageField(required=False)
    email = forms.CharField(
        label="Почта пользователя",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        label="Фамилия",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    patronymic = forms.CharField(
        label="Отчество (необязательно)",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    phone = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ['username', 'password', 'image', 'email',  'first_name', 'last_name', 'patronymic', 'phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_regex = re.compile(r'^8\d{10}$')
        if not phone_regex.match(phone):
            raise ValidationError("Номер телефона должен быть в формате 89997778866.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm1):
    username = forms.CharField(
        label="Логин пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        min_length=2,
    )
    password = forms.CharField(
        label="Введите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    self.user_cache = user
                else:
                    self.add_error('password', 'Неверный логин или пароль.')
            except User.DoesNotExist:
                self.add_error('username', 'Неверный логин или пароль.')

        return cleaned_data

class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = '__all__'


class PaymentForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    quantity = forms.IntegerField(label="Количество", min_value=1, required=True)
    payment_method = forms.ChoiceField(
        choices=[('card', 'Карта'), ('cash', 'Наличные'), ('qiwi', 'Qiwi')],
        label="Способ оплаты"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = '__all__'


class FlightForm(forms.ModelForm):
    class Meta:
        model = Flight
        fields = '__all__'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'




class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = '__all__'


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'


class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = '__all__'


class HotelRoomForm(forms.ModelForm):
    class Meta:
        model = HotelRoom
        fields = '__all__'


class HotelRoomImageForm(forms.ModelForm):
    class Meta:
        model = HotelRoomImage
        fields = '__all__'


class AmenityForm(forms.ModelForm):
    class Meta:
        model = Amenity
        fields = '__all__'


class FlightHotelHotelRoomForm(forms.ModelForm):
    class Meta:
        model = FlightHotelHotelRoom
        fields = '__all__'