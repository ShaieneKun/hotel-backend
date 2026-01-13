from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ("client", "Client"),
        ("staff", "Staff"),
        ("admin", "Admin"),
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="client")

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    capacity = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.number} ({self.room_type})"


class Reservation(models.Model):
    STATUS = (
        ("reserved", "Reserved"),
        ("cancelled", "Cancelled"),
        ("checked_out", "Checked out"),
    )
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name="reservations")
    guest = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations")
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS, default="reserved")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reservation {self.id} - {self.guest.username} ({self.room.number})"
