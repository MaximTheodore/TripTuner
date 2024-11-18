from django.contrib import admin

from .forms import UserCreationForm, UserChangeForm
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ['username', 'image', 'email', 'first_name', 'last_name', 'role_name', 'is_active', 'is_staff']
    list_display_links = ['username']
    list_editable = ['image', 'email', 'first_name', 'last_name', 'role_name']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['role_name']




@admin.register(SupportTicket)
class SupportTicketsAdmin(admin.ModelAdmin):
    list_display = ['issue_description', 'created_at', 'resolved_at', 'answer_status', 'tourAgent_id', 'client_id']
    list_display_links = ['issue_description']
    search_fields = ['issue_description', 'answer_status']
    list_filter = ['created_at', 'resolved_at', 'answer_status']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'country_id']
    list_display_links = ['name']
    search_fields = ['name']
    list_filter = ['country_id']


@admin.register(Hotel)
class HotelsAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'city_id']
    list_display_links = ['name']
    search_fields = ['name', 'address']
    list_filter = ['city_id']


@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'size', 'hotel_id']
    list_display_links = ['name']
    list_editable = ['size']
    search_fields = ['name']
    list_filter = ['hotel_id']


@admin.register(HotelRoomImage)
class HotelRoomImageAdmin(admin.ModelAdmin):
    list_display = ['hotelRoom_id']
    list_filter = ['hotelRoom_id']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['title', 'country_id__name']
    list_display_links = ['title']
    search_fields = ['title', 'description']
    list_filter = ['country_id']


@admin.register(Review)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['rating', 'hotelRoom_id', 'client_id', 'review_date']
    list_display_links = ['rating']
    search_fields = ['advantages', 'disadvantages']
    list_filter = ['hotelRoom_id', 'client_id']


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ['flight_number', 'amount_places', 'tour_id', 'departure_date', 'return_date']
    list_display_links = ['flight_number']
    list_editable = ['amount_places']
    search_fields = ['flight_number']
    list_filter = ['tour_id', 'departure_date', 'return_date']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['date_ordered', 'booking_place', 'price_of_order', 'client_id']
    list_display_links = ['date_ordered']
    list_editable = ['booking_place', 'price_of_order']
    search_fields = ['client_id__last_name']
    list_filter = ['date_ordered', 'flight_id', 'client_id']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_date', 'payment_amount', 'payment_status', 'payment_method', 'order_id']
    list_display_links = ['payment_date']
    list_editable = ['payment_amount', 'payment_status', 'payment_method']
    search_fields = ['payment_status', 'payment_method']
    list_filter = ['payment_date', 'order_id']


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'client_id']
    list_display_links = ['order_id']
    search_fields = ['order_id__date_ordered']
    list_filter = ['order_id']


@admin.register(FlightHotelHotelRoom)
class FlightHotelHotelRoomAdmin(admin.ModelAdmin):
    list_display = ['flight_id', 'hotel_id', 'hotelRoom_id']
    list_display_links = ['flight_id']



