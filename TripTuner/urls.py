from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include

from TripTuner import views

urlpatterns = [
    path('', views.home, name='home'),

    path('registration/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('tours/', views.TourListView.as_view(), name='tours'),
    path('tours/country/<int:country_id>/', views.TourListView.as_view(), name='tours_by_country'),
    path('tours/<int:tour_id>/flights/', views.flight_list, name='flight_list'),
    path('tours/<int:tour_id>/flights/<int:flight_id>/', views.flight_detail, name='flight_detail'),


    path('hotels/', views.HotelsListView.as_view(), name='hotels'),
    path('hotels/<int:hotel_id>/rooms/', views.HotelRoomListView.as_view(), name='hotel_rooms'),
    path('hotels/rooms/<int:pk>/', views.HotelRoomDetailView.as_view(), name='hotel_room_detail'),
    path('hotels/rooms/<int:room_id>/add_review/', views.add_review, name='add_review'),

    path('remove_from_cart/<int:order_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('add_to_cart/<int:flight_id>/', views.add_to_cart, name='add_to_cart'),
    path('basket/', views.basket, name='basket'),

    path('profile/', views.profile_view, name='profile'),
    path('support/send/', views.support_ticket_create, name='support_ticket_create'),
    path('order-history/u/<int:user_id>', views.order_history_view, name='order_history'),

    path('payment/<int:order_id>/', views.payment_view, name='payment_page'),


    path('control-panel/', views.control_panel, name='control_panel'),
    path('control-panel/edit/<int:pk>/<str:table>/', views.edit_object, name='edit_object'),
    path('control-panel/delete/<int:pk>/<str:table>/', views.delete_object, name='delete_object'),
    path('control-panel/export/', views.export_data, name='export'),
    path('control-panel/import/', views.import_data, name='import'),

]