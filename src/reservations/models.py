from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


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

    def is_admin(self):
        return self.role == "admin"

    def is_staff(self):
        return self.role == "staff"

    def is_client(self):
        return self.role == "client"


class Room(models.Model):
    ROOM_STATUS_CHOICES = (
        ("available", "Available"),
        ("occupied", "Occupied"),
        ("cleaning", "Cleaning/Maintenance"),
        ("blocked", "Blocked"),
    )
    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    capacity = models.PositiveSmallIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20, choices=ROOM_STATUS_CHOICES, default="available")

    def __str__(self):
        return f"Room {self.number} ({self.room_type})"

    @property
    def is_available(self):
        """Check if room is available for booking."""
        return self.status == "available" and self.is_active


class Reservation(models.Model):
    STATUS = (
        ("confirmed", "Confirmed"),
        ("checked_in", "Checked In"),
        ("checked_out", "Checked Out"),
        ("cancelled", "Cancelled"),
        ("no_show", "No-Show"),
    )
    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name="reservations")
    guest = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reservations")
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS, default="confirmed")
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Total price calculated when reservation is confirmed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["room", "status", "check_in"]),
            models.Index(fields=["guest", "status"]),
        ]

    def __str__(self):
        return f"Reservation {self.pk} - {self.guest.username} ({self.room.number})"

    def clean(self):
        """Validate that room is not double-booked."""
        if not self.check_in or not self.check_out:
            return

        if self.check_in >= self.check_out:
            raise ValidationError("Check-in must be before check-out.")

        # Prevent double booking: find conflicting reservations
        conflicting = Reservation.objects.filter(
            room=self.room,
            status__in=["confirmed", "checked_in"],
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
        )
        if self.pk:
            conflicting = conflicting.exclude(pk=self.pk)

        if conflicting.exists():
            raise ValidationError(
                f"Room {self.room.number} is already booked for the selected dates."
            )

    @property
    def is_past_checkin(self):
        """Check if check-in date has passed."""
        return self.check_in <= timezone.now()

    @property
    def is_past_checkout(self):
        """Check if check-out date has passed."""
        return self.check_out <= timezone.now()

    def get_status_display(self):
        """Return the human-readable status."""
        return dict(self.STATUS).get(self.status, self.status)

    def calculate_total_price(self):
        """Calculate total price based on room price and number of nights."""
        if self.check_in and self.check_out and self.room:
            nights = (self.check_out - self.check_in).days
            if nights < 1:
                nights = 1  # Minimum 1 night
            return self.room.price * nights
        return None

    def save(self, *args, **kwargs):
        self.clean()
        # Calculate total_price when reservation is confirmed
        if self.status == "confirmed" and self.total_price is None:
            self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)
