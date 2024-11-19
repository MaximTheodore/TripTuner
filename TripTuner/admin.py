from django.contrib import admin

from .forms import UserCreationForm, UserChangeForm
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ['username', 'image', 'email', 'first_name', 'last_name', 'role_name', 'is_active', 'is_staff']
    list_display_links = ['username']
    list_editable = ['role_name']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['role_name']



