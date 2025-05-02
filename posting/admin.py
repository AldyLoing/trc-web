from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('nomor_hape', 'role')}),
    )

    list_display = ('username', 'email', 'nomor_hape', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role',)

admin.site.register(CustomUser, CustomUserAdmin)
