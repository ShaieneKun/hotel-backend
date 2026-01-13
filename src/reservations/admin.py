from django.contrib import admin
from .models import Room, Reservation, Profile


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "room_type", "capacity", "price", "is_active")
    search_fields = ("number", "room_type")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "guest", "room", "check_in", "check_out", "status")
    list_filter = ("status",)
    search_fields = ("guest__username", "room__number")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__username",)
